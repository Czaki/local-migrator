from ._class_register import REGISTER, register_class, rename_key, update_argument
from ._json_hooks import NMEEncoder, nme_object_encoder, nme_object_hook


def nme_cbor_encoder(encoder, value):
    res = nme_object_encoder(value)
    if res is None:
        return encoder.encode(value)
    return encoder.encode(res)


def nme_cbor_decoder(decoder, value):
    return nme_object_hook(value)


__all__ = (
    "register_class",
    "nme_object_hook",
    "rename_key",
    "NMEEncoder",
    "REGISTER",
    "update_argument",
    "nme_cbor_encoder",
    "nme_cbor_decoder",
)
