from enum import Enum
from typing import Any, Dict

import pytest

from local_migrator import REGISTER, class_to_str, register_class, rename_key, update_argument


@register_class
class SampleClass1:
    pass


def rename_a_to_c(dkt: Dict[str, Any]) -> Dict[str, Any]:
    dkt = dict(dkt)
    dkt["c"] = dkt["a"]
    del dkt["a"]
    return dkt


@register_class(version="0.0.1", migrations=[("0.0.1", rename_a_to_c)])
class SampleClass2:
    pass


class SampleClass3:
    pass


@register_class(old_paths=["test.test.BBase"], version="0.0.2")
class SampleClass4:
    pass


class SampleClass6:
    pass


def test_migrate():
    assert REGISTER.migrate_data(class_to_str(SampleClass1), {}, {"a": 1, "b": 2}) == {"a": 1, "b": 2}
    assert REGISTER.migrate_data(
        class_to_str(SampleClass2), {class_to_str(SampleClass2): "0.0.1"}, {"a": 1, "b": 2}
    ) == {"a": 1, "b": 2}
    assert REGISTER.migrate_data(class_to_str(SampleClass2), {}, {"a": 1, "b": 2}) == {"c": 1, "b": 2}


def test_unregistered_class():
    assert REGISTER.get_class(class_to_str(SampleClass3)) is SampleClass3


def test_old_paths():
    assert REGISTER.get_class("test.test.BBase") is SampleClass4


def test_import_part():
    obj = REGISTER.get_class("class_register_util.SampleClass5")
    from class_register_util import SampleClass5

    assert SampleClass5 is obj


def test_old_class_error():
    with pytest.raises(RuntimeError):
        register_class(SampleClass6, old_paths=[class_to_str(SampleClass4)])


def test_get_version():
    assert str(REGISTER.get_version(SampleClass1)) == "0.0.0"
    assert str(REGISTER.get_version(SampleClass2)) == "0.0.1"
    assert str(REGISTER.get_version(SampleClass4)) == "0.0.2"


def test_rename_key():
    dkt = {"aaa": 1, "bbb": 2}
    assert rename_key(from_key="aaa", to_key="ccc")(dkt) == {"bbb": 2, "ccc": 1}
    with pytest.raises(KeyError):
        rename_key("ccc", "ddd")(dkt)

    assert rename_key("ccc", "ddd", optional=True)(dkt) == dkt


def test_update_argument(clean_register):
    @REGISTER.register(version="0.0.1")
    class MigrateClass:
        def __init__(self, a, b):
            self.a = a
            self.b = b

    class ClassToCall:
        __argument_class__ = MigrateClass

        @classmethod
        @update_argument("arg")
        def call_func(cls, aa, arg: MigrateClass):
            print(aa, arg.a)

    ClassToCall.call_func(aa=1, arg={"a": 1, "b": 2})
    ClassToCall.call_func(1, {"a": 1, "b": 2})


def test_migrate_parent_class(clean_register):
    @register_class(version="0.0.1", migrations=[("0.0.1", rename_key("field", "field1"))])
    class BaseMigrateClass:
        def __init__(self, field1):
            self.field1 = field1

    @register_class
    class MigrateClass(BaseMigrateClass):
        def __init__(self, field2, **kwargs):
            super().__init__(**kwargs)
            self.field2 = field2

    migrated = REGISTER.migrate_data(class_to_str(MigrateClass), {}, {"field2": 1, "field": 5})
    assert "field1" in migrated


def test_migrate_by_class(clean_register):
    @register_class(version="0.0.1", migrations=[("0.0.1", rename_key("field", "field1"))])
    class MigrateClass:
        def __init__(self, field1):
            self.field1 = field1

    migrated = REGISTER.migrate_data(class_to_str(MigrateClass), {}, {"field": 5})
    migrated2 = REGISTER.migrate_data(MigrateClass, {}, {"field": 5})
    assert migrated == {"field1": 5}
    assert migrated == migrated2


def test_migrate_keywords_args(clean_register):
    @register_class(version="0.0.1", migrations=[("0.0.1", rename_key("field", "field1"))])
    class MigrateClass:
        def __init__(self, field1):
            self.field1 = field1

    migrated = REGISTER.migrate_data(cls=class_to_str(MigrateClass), class_str_to_version_dkt={}, data={"field": 5})
    with pytest.warns(FutureWarning):
        migrated2 = REGISTER.migrate_data(
            class_str=class_to_str(MigrateClass), class_str_to_version_dkt={}, data={"field": 5}
        )
    assert migrated == {"field1": 5}
    assert migrated == migrated2


def test_wrong_version(clean_register):
    class SampleEnum(Enum):
        value1 = 1

    with pytest.raises(ValueError, match="class version lower than in migrations"):
        register_class("0.0.0", migrations=[("0.0.1", lambda x: x)])(SampleEnum)


def test_double_register(clean_register):
    class SampleEnum(Enum):
        value1 = 1

    register_class(SampleEnum)

    with pytest.raises(RuntimeError):
        register_class(SampleEnum)


def test_missed_class(clean_register):
    with pytest.raises(ValueError, match=r"Class [\w\.]+ not found"):
        REGISTER.get_class("nme.not_package.not_module.NotClass")
    with pytest.raises(ValueError, match=r"Class [\w\.]+ not found"):
        REGISTER.get_class("nme_not.not_package.not_module.NotClass")


def test_allow_errors(clean_register):
    @register_class
    class _SampleClass1:
        pass

    @register_class(allow_errors_in_values=True)
    class _SampleClass2:
        pass

    assert not REGISTER.allow_errors_in_values(_SampleClass1)
    assert REGISTER.allow_errors_in_values(_SampleClass2)
