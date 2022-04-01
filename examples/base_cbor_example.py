import cbor2
from pydantic import BaseModel

from nme import nme_cbor_decoder, nme_cbor_encoder


class SampleModel(BaseModel):
    field1: int
    field2: str


data = SampleModel(field1=4, field2="abc")

with open("sample.cbor", "wb") as f_p:
    cbor2.dump(data, f_p, default=nme_cbor_encoder)

with open("sample.cbor", "rb") as f_p2:
    data2 = cbor2.load(f_p2, object_hook=nme_cbor_decoder)

assert data == data2
