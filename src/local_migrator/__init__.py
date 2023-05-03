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


def cbor_decoder(decoder, value):  # noqa: ARG001
    """
    Cbor decoder hook. Use :py:func:`nme_object_hook` to decode objects.

    :param decoder: cbor2.Decoder
    :param value: object to be decoded

    Examples::

        with open(path_to_file, "rb") as f_p:
            data = cbor2.load(f_p, object_hook=nme_cbor_decoder)

    """
    return object_hook(value)


nme_object_hook = object_hook
NMEEncoder = Encoder
nme_cbor_encoder = cbor_encoder
nme_cbor_decoder = cbor_decoder


__all__ = (
    "class_to_str",
    "check_for_errors_in_dkt_values",
    "register_class",
    "object_hook",
    "nme_object_hook",
    "rename_key",
    "MigrationInfo",
    "MigrationRegistration",
    "Encoder",
    "NMEEncoder",
    "REGISTER",
    "update_argument",
    "cbor_encoder",
    "cbor_decoder",
    "nme_cbor_encoder",
    "nme_cbor_decoder",
    "__version__",
)
