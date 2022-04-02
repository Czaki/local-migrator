from ._class_register import (
    REGISTER,
    MigrationInfo,
    MigrationRegistration,
    class_to_str,
    register_class,
    rename_key,
    update_argument,
)
from ._serialize_hooks import NMEEncoder, nme_object_encoder, nme_object_hook
from .version import version as __version__


def nme_cbor_encoder(encoder, value):
    """
    Cbor encoder hook. Use :py:func:`nme_object_encoder` to encode objects.

    :param encoder: cbor2.Encoder
    :param value: object to be encoded

    Examples::

        with open(path_to_file, "wb") as f_p:
            cbor2.dump(data, f_p, default=nme_cbor_encoder)
    """
    res = nme_object_encoder(value)
    if res is None:
        raise TypeError(f"Cannot encode {value} of class {type(value)}")
    return encoder.encode(res)


def nme_cbor_decoder(decoder, value):
    """
    Cbor decoder hook. Use :py:func:`nme_object_hook` to decode objects.

    :param decoder: cbor2.Decoder
    :param value: object to be decoded

    Examples::

        with open(path_to_file, "rb") as f_p:
            data = cbor2.load(f_p, object_hook=nme_cbor_decoder)

    """
    return nme_object_hook(value)


__all__ = (
    "class_to_str",
    "register_class",
    "nme_object_hook",
    "rename_key",
    "MigrationInfo",
    "MigrationRegistration",
    "NMEEncoder",
    "REGISTER",
    "update_argument",
    "nme_cbor_encoder",
    "nme_cbor_decoder",
    "__version__",
)
