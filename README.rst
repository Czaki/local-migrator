**************
Local Migrator
**************

.. image:: https://codecov.io/gh/Czaki/local-migrator/branch/main/graph/badge.svg?token=KGEGEQYYRH
  :target: https://codecov.io/gh/Czaki/local-migrator
  :alt: Codecov

.. image:: https://github.com/Czaki/local-migrator/actions/workflows/tests.yml/badge.svg
  :target: https://github.com/Czaki/local-migrator/actions/workflows/tests.yml
  :alt: Test

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
  :target: https://github.com/psf/black
  :alt: Code Style

.. image:: https://readthedocs.org/projects/local-migrator/badge/?version=latest
  :target: https://local-migrator.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

.. image:: https://badge.fury.io/py/local-migrator.svg
  :target: https://badge.fury.io/py/local-migrator
  :alt: PyPI version

.. image:: https://anaconda.org/conda-forge/local-migrator/badges/version.svg
   :target: https://anaconda.org/conda-forge/local-migrator
   :alt: Conda-forge version


This support package simplifies data persistence between user sessions
and software version updates.

The main idea of this package is simplify data migration between versions,
and allow to define migration information next to data structure definition.


Basic usage (data serialization)
################################

If You only need to serialize data, then you could use only JSON hooks

.. code-block:: python

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


Migrations
##########

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

    from local_migrator import Encoder, object_hook

    class SampleModel(BaseModel):
        field1: int
        field_ca_1: str
        field_ca_2: float

    with open("sample.json", "w") as f_p:
        json.dump(data, f_p, cls=Encoder)

But there is decision to move both ``ca`` field to sub structure:

.. code-block:: python

    class CaModel(BaseModel):
        field_1: str
        field_2: float

    class SampleModel(BaseModel):
        field1: int
        field_ca: CaModel


Then with ``local_migrator`` code may look:

.. code-block:: python

    from local_migrator import object_hook, register_class

    class CaModel(BaseModel):
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
        data = json.load(f_p, object_hook=object_hook)

Assume that there is decision to rename ``field1`` to ``id``.
Then code may look:

.. code-block:: python

    from local_migrator import object_hook, register_class, rename_key

    class CaModel(BaseModel):
        field_1: str
        field_2: float

    def ca_migration_function(dkt):
        dkt["field_ca"] = CaModel(field1=dkt.pop("field_ca_1"),
                                  field2=dkt.pop("field_ca_2"))
        return dkt

    @register_class("0.0.2", [("0.0.1", ca_migration_function), ("0.0.2", rename_key("field1", "id"))])
    class SampleModel(BaseModel):
        id: int
        field_ca: CaModel

    with open("sample.json") as f_p:
        data = json.load(f_p, object_hook=object_hook)


More examples could be found in `examples`_ section of documentation

Additional functions
####################

* ``rename_key(from_key: str, to_key: str, optional=False) -> Callable[[Dict], Dict]`` - helper
  function for rename field migrations.

* ``update_argument(argument_name:str)(func: Callable) -> Callable`` - decorator to keep backward
  compatibility by converting ``dict`` argument to some class base on function type annotation


Contributing
############

Contributions are encouraged! Please create pull request or open issue.
For PR please remember to add tests and documentation.


Additional notes
################

This package is originally named ``nme`` but was rename to clarify its purpose.

This package is extracted from `PartSeg`_
project for simplify reuse it in another projects.


.. _PartSeg: https://github.com/4DNucleome/PartSeg
.. _examples: https://local-migrator.readthedocs.io/en/latest/examples.html
