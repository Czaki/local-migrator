Examples
========

Class inheritance and migrations
################################

By default ``local-migrator`` uses migrations of parent class if defined:

Lets see this code sample:

.. code-block:: python

    import json
    from datetime import date
    from pydantic import BaseModel
    from local_migrator import Encoder

    class Person(BaseModel):
        name: str
        birth_date: date

    class Employee(Person):
        company: str

    data = Employee(name="John Smith", birth_date=date(1980, 1, 15), company="napari")

    with open("employee.json", "w") as f:
        json.dump(data, f, cls=Encoder)

Assume that one would like to split ``Person.name`` into
two fields: ``names`` and ``last_name``.
Also there is a need to load data from previous version. Following code will do it:


.. code-block:: python

    import json
    from datetime import date
    from pydantic import BaseModel
    from local_migrator import object_hook, register_class

    def _migrate_person(dkt):
        dkt = dict(dkt) # copy for safety
        name_list = dkt["name"].rsplit(" ", 1)
        if len(name_list) == 1:
            dkt["names"] = name_list[0]
            dkt["last_name"] = ""
        else:
            dkt["names"], dkt["last_name"] = name_list
        return dkt

    @register_class("0.0.1", migrations=[("0.0.1", _migrate_person)])
    class Person(BaseModel):
        names: str
        last_name: str
        birth_date: date

    class Employee(Person):
        company: str

    data = Employee(names="John", last_name="Smith", birth_date=date(1980, 1, 15), company="napari")

    with open("employee.json",) as f:
        data2 = json.load(f, object_hook=object_hook)

    assert data == data2

:py:func:`register_class` has a ``use_parent_migrations`` argument by
 default set to ``True``. If set to ``False``, parents class migration
 will be ignored. This may be usefully in some rare examples, when
 fixing old data structures.


``update_argument``
###################

The :py:func:`nme.update_argument` is a helper function that allow update
the :py:class:`dict` argument of a function to class based
(for example :py:class:`pydantic.BaseModel` based)
keeping backward compatibility.

Lets have function:

.. code-block:: python

    from typing import Dict

    def my_function(arg: Dict[str, int]):
        return arg.get("a", 1) + arg.get("b", 2)

    assert my_function({"a":5}) == 7

And assume that we would like to use ``nme`` for serialize argument of this
function and have option to use migration engine.

To keep backward compatibility we can wrote following code:

.. code-block:: python

    from typing import Dict
    from pydantic import BaseModel
    from local_migrator import update_argument

    class MyArgument(BaseModel):
        a: int = 1
        b: int = 2

    @update_argument("arg")
    def my_function(arg: MyArgument):
        return arg.a + arg.b

    assert my_function({"a":5}) == 7
    assert my_function(MyArgument(a=5)) == 7

``update_argument`` use :py:mod:`inspect` module to
determine argument class.

CBOR support
############

``cbor2`` encoder (``cbor_encoder``) and object hook
(``cbor_decoder``) are available.

.. code-block:: python

    import cbor2
    from pydantic import BaseModel
    from local_migrator import cbor_encoder, cbor_decoder


    class SampleModel(BaseModel):
        field1: int
        field2: str


    data = SampleModel(field1=4, field2="abc")

    with open("sample.cbor", "wb") as f_p:
        cbor2.dump(data, f_p, default=cbor_encoder)

    with open("sample.cbor", "rb") as f_p:
        data2 = cbor2.load(f_p, object_hook=cbor_decoder)

    assert data == data2
