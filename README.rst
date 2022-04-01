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

.. image:: https://readthedocs.org/projects/nme/badge/?version=latest
  :target: https://nme.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

.. image:: https://badge.fury.io/py/nme.svg
  :target: https://badge.fury.io/py/nme
  :alt: PyPI version


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


Migrations
##########
The main idea of this package is simplify data migration between versions,
and allow to define migration information next to data structure definition.


To register this information there is ``register_class`` decorator.
It has 4 parameters:

* ``version`` - version of data structure
* ``migration_list`` - list of tuple (``version``. ``migration_function``).
* ``old_paths`` - list of fully qualified python paths to previous class
  definitions. This is to allow move class during code refactoring.
* ``use_parent_migrations`` - if True, then parent class migrations
  will be used.


Lets imagine that we have such code

.. code-block:: python

    from nme import NMEEncoder, nme_object_hook

    class SampleModel(BaseModel):
        field1: int
        field_ca_1: str
        field_ca_2: float

    with open("sample.json", "w") as f_p:
        json.dump(data, f_p, cls=NMEEncoder)

But there is decision to mov both ``ca`` field to sub structure:

.. code-block:: python

    class CaModel(BaseModel)
        field_1: str
        field_2: float

    class SampleModel(BaseModel):
        field1: int
        field_ca: CaModel


Then with ``nme`` code may look:

.. code-block:: python

    from nme import nme_object_hook, register_class

    class CaModel(BaseModel)
        field_1: str
        field_2: float

    def ca_migration_function(dkt):
        dkt["field_ca"] = CaModel(field1=dkt.pop("field_ca_1"),
                                  field2=dkt.pop("field_ca_2"))
        return dkt

    @register_class("0.0.1", [("0.0.1", ca_migration_function)])
    class SampleModel(BaseModel):
        field1: int
        field_ca: CaModel

    with open("sample.json") as f_p:
        data = json.load(f_p, object_hook=nme_object_hook)


CBOR support
############

Also ``cbor2`` encoder (``nme_object_encoder``) and object hook
(``nme_cbor_decoder``) are available.

.. code-block:: python

    import cbor2
    from pydantic import BaseModel
    from nme import nme_cbor_encoder, nme_cbor_decoder


    class SampleModel(BaseModel):
        field1: int
        field2: str


    data = SampleModel(field1=4, field2="abc")

    with open("sample.cbor", "wb") as f_p:
        cbor2.dump(data, f_p, default=nme_cbor_encoder)

    with open("sample.cbor", "rb") as f_p:
        data2 = cbor2.load(f_p, object_hook=nme_cbor_decoder)

    assert data == data2



Additional functions
####################

* ``rename_key(from_key: str, to_key: str, optional=False) -> Callable[[Dict], Dict]`` - helper
  function for rename field migrations.

* ``update_argument(argument_name:str)(func: Callable) -> Callable`` - decorator to keep backward
  compatibility by converting ``dict`` argument to some class base on function type annotation


Additional notes
################

This package is extracted from `PartSeg`_
project for simplify reuse it in another projects.


.. _PartSeg: https://github.com/4DNucleome/PartSeg
