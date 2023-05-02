# pylint: disable=R0201

import json
from enum import Enum
from pathlib import Path

import numpy as np
import pytest
from pydantic import BaseModel, Extra, dataclasses

from local_migrator import Encoder, class_to_str, object_hook, register_class, rename_key
from local_migrator._serialize_hooks import add_class_info

try:
    from napari.utils import Colormap
    from napari.utils.notifications import NotificationSeverity
except ImportError:
    Colormap = None
    NotificationSeverity = None


@dataclasses.dataclass
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


class RadiusType(Enum):
    NO = 0
    R2D = 1
    R3D = 2


@pytest.mark.skipif(Colormap is None, reason="napari not installed")
def test_colormap_dump(tmp_path):
    cmap_list = [Colormap([(0, 0, 0), (1, 1, 1)]), Colormap([(0, 0, 0), (1, 1, 1)], controls=[0, 1])]
    with open(tmp_path / "test.json", "w") as f_p:
        json.dump(cmap_list, f_p, cls=Encoder)

    with open(tmp_path / "test.json") as f_p:
        cmap_list2 = json.load(f_p, object_hook=object_hook)

    assert np.array_equal(cmap_list[0].colors, cmap_list2[0].colors)
    assert np.array_equal(cmap_list[0].controls, cmap_list2[0].controls)
    assert np.array_equal(cmap_list[1].colors, cmap_list2[1].colors)
    assert np.array_equal(cmap_list[1].controls, cmap_list2[1].controls)

    cmap_list = [
        Colormap([(0, 0, 0), (1, 1, 1)]),
        Colormap([(0, 0, 0), (0, 0, 0), (1, 1, 1), (1, 1, 1)], controls=[0, 0.1, 0.8, 1]),
    ]
    with open(tmp_path / "test2.json", "w") as f_p:
        json.dump(cmap_list, f_p, cls=Encoder)

    with open(tmp_path / "test2.json") as f_p:
        cmap_list2 = json.load(f_p, object_hook=object_hook)

    assert np.array_equal(cmap_list[0].colors, cmap_list2[0].colors)
    assert np.array_equal(cmap_list[0].controls, cmap_list2[0].controls)
    assert np.array_equal(cmap_list[1].colors, cmap_list2[1].colors)
    assert np.array_equal(cmap_list[1].controls, cmap_list2[1].controls)
    assert cmap_list2[1].controls[0] == 0
    assert cmap_list2[1].controls[-1] == 1
    assert np.array_equal(cmap_list[1].colors[0], cmap_list2[1].colors[0])
    assert np.array_equal(cmap_list[1].colors[-1], cmap_list2[1].colors[-1])


@pytest.mark.parametrize("dtype", [np.uint8, np.uint16, np.uint32, np.float32, np.float64])
def test_dump_numpy_types(dtype):
    data = {"a": dtype(2)}
    text = json.dumps(data, cls=Encoder)
    loaded = json.loads(text)
    assert loaded["a"] == 2


class TestNMEEncoder:
    @pytest.mark.skipif(NotificationSeverity is None, reason="napari not installed")
    def test_enum_serialize(self, tmp_path):
        data = {"value1": RadiusType.R2D, "value2": RadiusType.NO, "value3": NotificationSeverity.ERROR}
        with (tmp_path / "test.json").open("w") as f_p:
            json.dump(data, f_p, cls=Encoder)
        with (tmp_path / "test.json").open("r") as f_p:
            data2 = json.load(f_p, object_hook=object_hook)
        assert data2["value1"] == RadiusType.R2D
        assert data2["value2"] == RadiusType.NO
        assert data2["value3"] == NotificationSeverity.ERROR

    def test_dataclass_serialze(self, tmp_path):
        data = {"value": SampleDataclass(1, "text")}
        with (tmp_path / "test.json").open("w") as f_p:
            json.dump(data, f_p, cls=Encoder)
        with (tmp_path / "test.json").open("r") as f_p:
            data2 = json.load(f_p, object_hook=object_hook)

        assert isinstance(data2["value"], SampleDataclass)
        assert data2["value"] == SampleDataclass(1, "text")

    @pytest.mark.skipif(Colormap is None, reason="napari not installed")
    def test_pydantic_serialize(self, tmp_path):
        data = {
            "color1": Colormap(colors=[[0, 0, 0], [0, 0, 0]], controls=[0, 1]),
            "other": SamplePydantic(sample_int=1, sample_str="text", sample_dataclass=SampleDataclass(1, "text")),
        }
        with (tmp_path / "test.json").open("w") as f_p:
            json.dump(data, f_p, cls=Encoder)
        with (tmp_path / "test.json").open("r") as f_p:
            data2 = json.load(f_p, object_hook=object_hook)
        assert data2["color1"] == Colormap(colors=[[0, 0, 0], [0, 0, 0]], controls=[0, 1])
        assert isinstance(data2["other"], SamplePydantic)
        assert isinstance(data2["other"].sample_dataclass, SampleDataclass)

    def test_numpy_serialize(self, tmp_path):
        data = {"arr": np.arange(10), "f": np.float32(0.1), "i": np.int16(1000)}
        with (tmp_path / "test.json").open("w") as f_p:
            json.dump(data, f_p, cls=Encoder)
        with (tmp_path / "test.json").open("r") as f_p:
            data2 = json.load(f_p, object_hook=object_hook)
        assert data2["arr"] == list(range(10))
        assert np.isclose(data["f"], 0.1)
        assert data2["i"] == 1000

    def test_class_with_as_dict(self, tmp_path):
        data = {"d": SampleAsDict(1, 10)}
        with (tmp_path / "test.json").open("w") as f_p:
            json.dump(data, f_p, cls=Encoder)
        with (tmp_path / "test.json").open("r") as f_p:
            data2 = json.load(f_p, object_hook=object_hook)
        assert isinstance(data2["d"], SampleAsDict)
        assert data2["d"].value1 == data["d"].value1
        assert data2["d"].value2 == data["d"].value2

    def test_sub_class_serialization(self, tmp_path):
        ob = DummyClassForTest.DummySubClassForTest(1, 2)
        with (tmp_path / "test.json").open("w") as f_p:
            json.dump(ob, f_p, cls=Encoder)
        with (tmp_path / "test.json").open("r") as f_p:
            ob2 = json.load(f_p, object_hook=object_hook)
        assert ob2.data1 == 1
        assert ob2.data2 == 2


def test_add_class_info_pydantic(clean_register):
    @register_class
    class SampleClass(BaseModel):
        field: int = 1

    dkt = {}
    dkt = add_class_info(SampleClass(), dkt)
    assert "__class__" in dkt
    assert class_to_str(SampleClass) == dkt["__class__"]
    assert len(dkt["__class_version_dkt__"]) == 1
    assert dkt["__class_version_dkt__"][class_to_str(SampleClass)] == "0.0.0"


def test_add_class_info_enum(clean_register):
    @register_class
    class SampleEnum(Enum):
        field = 1

    dkt = {}
    dkt = add_class_info(SampleEnum.field, dkt)
    assert "__class__" in dkt
    assert class_to_str(SampleEnum) == dkt["__class__"]
    assert len(dkt["__class_version_dkt__"]) == 1
    assert dkt["__class_version_dkt__"][class_to_str(SampleEnum)] == "0.0.0"


def test_path_serialization(tmp_path):
    with (tmp_path / "test.json").open("w") as f_p:
        json.dump(Path(), f_p, cls=Encoder)
    with (tmp_path / "test.json").open("r") as f_p:
        data = json.load(f_p, object_hook=object_hook)
    assert str(Path()) == data


def test_error_deserialization(clean_register, tmp_path):
    class SampleEnum(Enum):
        field = 1

    with (tmp_path / "test.json").open("w") as f_p:
        f_p.write(
            '{"value": 1, "__class__": "test_json_hooks.test_error_deserialization.<locals>.SampleEnum",'
            '"__class_version_dkt__": {"test_json_hooks.test_error_deserialization.<locals>.SampleEnum": "0.0.0"}}'
        )
    with (tmp_path / "test.json").open("r") as f_p:
        data2 = json.load(f_p, object_hook=object_hook)
    assert "__error__" in data2

    register_class(SampleEnum)

    with (tmp_path / "test2.json").open("w") as f_p:
        json.dump(data2, f_p, cls=Encoder)

    with (tmp_path / "test2.json").open("r") as f_p:
        data3 = json.load(f_p, object_hook=object_hook)

    assert data3 == SampleEnum.field


class TestNMEObjectHook:
    def test_no_inheritance_read(self, clean_register, tmp_path):
        @register_class(version="0.0.1", migrations=[("0.0.1", rename_key("field", "field1"))])
        class BaseClass(BaseModel):
            field1: int = 1

        @register_class(
            version="0.0.1", migrations=[("0.0.1", rename_key("field", "field1"))], use_parent_migrations=False
        )
        class MainClass(BaseClass):
            field2: int = 5

        data_str = """
        {"field": 1, "field2": 5,
         "__class__":
         "test_json_hooks.TestNMEObjectHook.test_no_inheritance_read.<locals>.MainClass",
         "__class_version_dkt__": {
         "test_json_hooks.TestNMEObjectHook.test_no_inheritance_read.<locals>.MainClass": "0.0.0",
         "test_json_hooks.TestNMEObjectHook.test_no_inheritance_read.<locals>.BaseClass": "0.0.0"
         }}
         """

        ob = json.loads(data_str, object_hook=object_hook)
        assert isinstance(ob, MainClass)

    def test_error_in_object_restore(self, clean_register):
        @register_class
        class SubClass(BaseModel, extra=Extra.forbid):
            field: int = 1

        @register_class
        class MainClass(BaseModel):
            field: int = 1
            sub11: SubClass = SubClass()

        data_str = """
        {"__class__": "test_json_hooks.TestNMEObjectHook.test_error_in_object_restore.<locals>.MainClass",
        "__class_version_dkt__":
        {"test_json_hooks.TestNMEObjectHook.test_error_in_object_restore.<locals>.MainClass": "0.0.0"},
        "__values__": {"field": 1,
        "sub11": {"__class__": "test_json_hooks.TestNMEObjectHook.test_error_in_object_restore.<locals>.SubClass",
        "__class_version_dkt__":
        {"test_json_hooks.TestNMEObjectHook.test_error_in_object_restore.<locals>.SubClass": "0.0.0"},
        "__values__": {"field": 1, "eee": 1}}}}
        """

        ob = json.loads(data_str, object_hook=object_hook)
        assert isinstance(ob, dict)
        assert "__error__" in ob
        assert ob["__error__"] == "Error in fields: sub11"


class DummyClassForTest:
    class DummySubClassForTest:
        def __init__(self, data1, data2):
            self.data1, self.data2 = data1, data2

        def as_dict(self):
            return {"data1": self.data1, "data2": self.data2}
