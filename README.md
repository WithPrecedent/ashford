[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![PyPI Latest Release](https://img.shields.io/pypi/v/ashford.svg)](https://pypi.org/project/ashford/) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![Documentation Status](https://readthedocs.org/projects/ashford/badge/?version=latest)](http://ashford.readthedocs.io/?badge=latest)




# Why ashford?

This package provides classes and decorators for a variety of Python implementations of registration, factories, and type validators.

<p align="center">
<img src="https://media.giphy.com/media/Fl7aszvRTsJhsAfyG2/giphy.gif" height="300"/>
</p>


## Registries
<p align="center">
<img src="https://media.giphy.com/media/tWY3sKzNDpwgzKwzMa/giphy.gif" height="300"/>
</p>

* `registered`: a decorator that stores a registry in a `registry` attribute of the function or class which is wrapped by the decorator.
* `Registrar`: a mixin for automatic subclass registration.


## Factories
<p align="center">
<img src="https://media.giphy.com/media/pKEF7XmUlRGFayOyLJ/giphy.gif" height="300"/>
</p>
* `InstanceFactory`: mixin that stores all subclass instances in the `instances` class attribute and returns stored instances when the `create` classmethod is called.
* `LibraryFactory`: mixin that stores all subclasses and subclass instances in the `library` class attribute and returns stored subclasses and/or instances when the `create` classmethod is called.
* `SourceFactory`: mixin that calls the appropriate creation method based on the type of passed first argument to `create` and the types stored in the keys of the `sources` class attribute.
* `StealthFactory`: mixin that returns stored subclasses when the `create` classmethod is called without having a `subclasses` class attribute like SubclassFactory.
* `SubclassFactory`: mixin that stores all subclasses in the `subclasses` class attribute and returns stored subclasses when the `create` classmethod is called.
* `TypeFactory`: mixin that calls the appropriate creation method based on the type of passed first argument to `create` and the snakecase name of the type. This factory is prone to significant key errors unless you are sure of the snakecase names of all possible submitted type names. SourceFactory avoids this problem by allowing you to declare corresponding types and string names.

## Validators


<p align="center">
<img src="https://media.giphy.com/media/emN3Lsx8elioidwcLS/giphy.gif" height="300"/>
</p>


* `bonafide`: decorator that validates or converts types based on type annotations of the wrapped function or dataclass (under construction)
* 
ashford`s framework supports a wide range of coding styles. You can create complex multiple inheritance structures with mixins galore or simpler, compositional objects. Even though the data structures are necessarily object-oriented, all of the tools to modify them are also available as functions, for those who prefer a more funcitonal approaching to programming. 

The project is also highly internally documented so that users and developers can easily make ashford work with their projects. It is designed for Python coders at all levels. Beginners should be able to follow the readable code and internal documentation to understand how it works. More advanced users should find complex and tricky problems addressed through efficient code.