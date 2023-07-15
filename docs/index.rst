.. nme documentation master file, created by
   sphinx-quickstart on Fri Apr  1 00:32:04 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root ``toctree`` directive.

Welcome to local-migrator's documentation!
==========================================

``local-migrator`` is package for support of data persistance between sessions
and versions.
Currently it support for :py:mod:`json` and :py:mod:`cbor2` backends.

``local-migrator`` support serialize and deserialize following class and its subclasses:
(referring to :py:func:`local_migrator.object_encoder`):

* :py:class:`enum.Enum`
* :py:func:`dataclasses.dataclass`
* :py:class:`numpy.ndarray`
* :py:class:`pydantic.BaseModel`
* :py:class:`numpy.integer` (change to pure int)
* :py:class:`numpy.floating` (change to pure float)
* :py:class:`pathlib.Path` (Serialized to string)
* Any class with an :py:meth:`as_dict` method. This method should
  return a dictionary of valid constructor arguments.



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   examples
   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
