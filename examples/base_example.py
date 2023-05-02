import json

from pydantic import BaseModel

from local_migrator import Encoder, object_hook


class SampleModel(BaseModel):
    field1: int
    field2: str


data = SampleModel(field1=4, field2="abc")

with open("sample.json", "w") as f_p:
    json.dump(data, f_p, cls=Encoder)

with open("sample.json") as f_p:
    data2 = json.load(f_p, object_hook=object_hook)

assert data == data2
