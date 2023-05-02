from dataclasses import dataclass
from enum import Enum

import cbor2
import pytest
from pydantic import BaseModel

from local_migrator import cbor_decoder, cbor_encoder, class_to_str, register_class, rename_key


class RadiusType(Enum):
    NO = 0
    R2D = 1
    R3D = 2


@dataclass
class SampleDataclass:
    filed1: int
    field2: str


class SamplePydantic(BaseModel):
    sample_int: int
    sample_str: str
    sample_dataclass: SampleDataclass


class SampleAsDict:
    def __init__(self, value1, value2):
        self.value1 = value1
        self.value2 = value2

    def as_dict(self):
        return {"value1": self.value1, "value2": self.value2}

    def __eq__(self, other):
        return self.value1 == other.value1 and self.value2 == other.value2

    def __repr__(self) -> str:
        return f"SampleAsDict(value1={self.value1}, value2={self.value2})"


def test_simple(tmp_path):
    data = {"aa": 1, "bb": 2}
    with open(tmp_path / "test.cbor", "wb") as f_p:
        cbor2.dump(data, f_p, default=cbor_encoder)

    with open(tmp_path / "test.cbor", "rb") as f_p:
        data2 = cbor2.load(f_p, object_hook=cbor_decoder)
    assert data2 == data


def test_hook_failure(tmp_path):
    class DummyClass:
        def __init__(self):
            pass

    with pytest.raises(TypeError), open(tmp_path / "test.cbor", "wb") as f_p:
        cbor2.dump(DummyClass(), f_p, default=cbor_encoder)


def test_serialize_enum(tmp_path, clean_register):
    with open(tmp_path / "test.cbor", "wb") as f_p:
        cbor2.dump(RadiusType.NO, f_p, default=cbor_encoder)

    with open(tmp_path / "test.cbor", "rb") as f_p:
        data = cbor2.load(f_p, object_hook=cbor_decoder)
    assert data == RadiusType.NO


def test_dataclass_serialize(tmp_path, clean_register):
    data = SampleDataclass(1, "cc")
    with open(tmp_path / "test.cbor", "wb") as f_p:
        cbor2.dump(data, f_p, default=cbor_encoder)

    with open(tmp_path / "test.cbor", "rb") as f_p:
        data2 = cbor2.load(f_p, object_hook=cbor_decoder)
    assert data2 == data


def test_pydantic_serialize(tmp_path, clean_register):
    data = SamplePydantic(sample_int=2, sample_str="ee", sample_dataclass=SampleDataclass(1, "cc"))
    with open(tmp_path / "test.cbor", "wb") as f_p:
        cbor2.dump(data, f_p, default=cbor_encoder)

    with open(tmp_path / "test.cbor", "rb") as f_p:
        data2 = cbor2.load(f_p, object_hook=cbor_decoder)
    assert data2 == data


def test_as_dict_serialize(tmp_path, clean_register):
    data = SampleAsDict(value1=1, value2=[1, 2, 3])
    with open(tmp_path / "test.cbor", "wb") as f_p:
        cbor2.dump(data, f_p, default=cbor_encoder)

    with open(tmp_path / "test.cbor", "rb") as f_p:
        data2 = cbor2.load(f_p, object_hook=cbor_decoder)
    assert data2 == data


def test_migration_base(tmp_path, clean_register):
    @register_class
    class SampleClass(BaseModel):
        field: int = 1

    with open(tmp_path / "test.cbor", "wb") as f_p:
        cbor2.dump(SampleClass(), f_p, default=cbor_encoder)

    clean_register()

    def provide_default(dkt):
        dkt["field2"] = 7
        return dkt

    @register_class(
        version="0.0.2",
        old_paths=[class_to_str(SampleClass)],
        migrations=[("0.0.1", rename_key("field", "field1")), ("0.0.2", provide_default)],
    )
    class SampleClass2(BaseModel):
        field1: int = 1
        field2: int = 4

    with open(tmp_path / "test.cbor", "rb") as f_p:
        data = cbor2.load(f_p, object_hook=cbor_decoder)
    assert SampleClass2(field1=1, field2=7) == data
