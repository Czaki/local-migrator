import dataclasses
import enum
import json
from pathlib import Path

import numpy as np

from ._class_register import REGISTER, class_to_str

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    # allow to use in environment without pydantic.
    class BaseModel:  # type: ignore
        pass


try:
    from numpy import ndarray
except ImportError:  # pragma: no cover
    # allow to use in environment without numpy.
    class ndarray:  # type: ignore
        pass


def add_class_info(obj: type, dkt: dict) -> dict:
    dkt["__class__"] = class_to_str(obj.__class__)
    dkt["__class_version_dkt__"] = {
        class_to_str(sup_obj): str(REGISTER.get_version(sup_obj))
        for sup_obj in obj.__class__.__mro__
        if class_to_str(sup_obj)
        not in {
            "object",
            "pydantic.main.BaseModel",
            "pydantic.utils.Representation",
            "enum.Enum",
            "builtins.object",
            "typing.Generic",
        }
        and not class_to_str(sup_obj).startswith("collections.abc")
    }
    return dkt


class NMEEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, enum.Enum):
            dkt = {"value": o.value}
            return add_class_info(o, dkt)
        if dataclasses.is_dataclass(o):
            fields = dataclasses.fields(o)
            dkt = {x.name: getattr(o, x.name) for x in fields}
            return add_class_info(o, dkt)

        if isinstance(o, ndarray):
            return o.tolist()

        if isinstance(o, BaseModel):
            try:
                dkt = dict(o)
            except (ValueError, TypeError):
                dkt = o.dict()  # workaround for napari Colormap class
            return add_class_info(o, dkt)

        if hasattr(o, "as_dict"):
            dkt = o.as_dict()
            return add_class_info(o, dkt)

        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, Path):
            return str(o)
        return super().default(o)  # pragma: no cover


def nme_object_hook(dkt: dict):
    if "__error__" in dkt:
        dkt.pop("__error__")  # different environments without same plugins installed
    if "__class__" in dkt:
        cls_str = dkt.pop("__class__")
        version_dkt = dkt.pop("__class_version_dkt__") if "__class_version_dkt__" in dkt else {cls_str: "0.0.0"}
        try:
            dkt_migrated = REGISTER.migrate_data(cls_str, version_dkt, dkt)
            cls = REGISTER.get_class(cls_str)
            return cls(**dkt_migrated)
        except Exception as e:  # pylint: disable=W0703
            dkt["__class__"] = cls_str
            dkt["__class_version_dkt__"] = version_dkt
            dkt["__error__"] = str(e)

    return dkt
