from importlib import metadata

from ._class_register import (
    REGISTER,
    MigrationInfo,
    MigrationRegistration,
    class_to_str,
    register_class,
    rename_key,
    update_argument,
)
from ._serialize_hooks import Encoder, check_for_errors_in_dkt_values, object_encoder, object_hook
from .version import version as __version__

try:
    nme_version = metadata.version("nme")
except metadata.PackageNotFoundError:
    pass
else:  # pragma: no cover
    from packaging.version import parse

    if parse(nme_version) <= parse("0.1.6"):
        raise ImportError("local_migrator is incompatible with nme<=0.1.6. You need to upgrade or uninstall nme.")
    del parse
    del nme_version

del metadata


def cbor_encoder(encoder, value):
    """
    Cbor encoder hook. Use :py:func:`nme_object_encoder` to encode objects.

    :param encoder: cbor2.Encoder
    :param value: object to be encoded

    Examples::

        with open(path_to_file, "wb") as f_p:
            cbor2.dump(data, f_p, default=nme_cbor_encoder)
    """
    res = object_encoder(value)
    if res is None:
        raise TypeError(f"Cannot encode {value} of class {type(value)}")
    return encoder.encode(res)


def cbor_decoder(*args):
    """
    Cbor decoder hook. Use :py:func:`nme_object_hook` to decode objects.

    Callback signature changed across cbor2 releases:

    * Older versions call it as ``(decoder, value)``.
    * Newer versions call it as ``(value, immutable)``.

    This wrapper supports both conventions.

    :param args: callback arguments from cbor2

    Examples::

        with open(path_to_file, "rb") as f_p:
            data = cbor2.load(f_p, object_hook=nme_cbor_decoder)

    """
    value = None
    for arg in args:
        if isinstance(arg, dict):
            value = arg
            break
    if value is None:  # pragma: no cover
        raise TypeError(f"Cannot decode CBOR object with arguments: {args!r}")
    return object_hook(value)


nme_object_hook = object_hook
NMEEncoder = Encoder
nme_cbor_encoder = cbor_encoder
nme_cbor_decoder = cbor_decoder


__all__ = (
    "REGISTER",
    "Encoder",
    "MigrationInfo",
    "MigrationRegistration",
    "NMEEncoder",
    "__version__",
    "cbor_decoder",
    "cbor_encoder",
    "check_for_errors_in_dkt_values",
    "class_to_str",
    "nme_cbor_decoder",
    "nme_cbor_encoder",
    "nme_object_hook",
    "object_hook",
    "register_class",
    "rename_key",
    "update_argument",
)
