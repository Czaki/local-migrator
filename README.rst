***********************
Napari Migration Engine
***********************

.. image:: https://codecov.io/gh/Czaki/nme/branch/main/graph/badge.svg?token=KGEGEQYYRH
  :target: https://codecov.io/gh/Czaki/nme
  :alt: Codecov

.. image:: https://github.com/Czaki/nme/actions/workflows/tests.yml/badge.svg
  :target: https://github.com/Czaki/nme/actions/workflows/tests.yml
  :alt: Test

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
  :target: https://github.com/psf/black
  :alt: Code Style


This is support package for simplify data serialization and
persistance data between sessions and versions.


Basic usage
###########

If You only need to serialize data, then you could use only JSON hooks

.. code-block:: python

    import json

    from pydantic import BaseModel
    from nme import NMEEncoder, nme_object_hook


    class SampleModel(BaseModel):
        field1: int
        field2: str


    data = SampleModel(field1=4, field2="abc")

    with open("sample.json", "w") as f_p:
        json.dump(data, f_p, cls=NMEEncoder)

    with open("sample.json") as f_p:
        data2 = json.load(f_p, object_hook=nme_object_hook)

    assert data == data2
