# ashford

| | |
| --- | --- |
| Version | [![PyPI Latest Release](https://img.shields.io/pypi/v/ashford.svg?style=for-the-badge&color=steelblue&label=PyPI&logo=PyPI&logoColor=yellow)](https://pypi.org/project/ashford/) [![GitHub Latest Release](https://img.shields.io/github/v/tag/WithPrecedent/ashford?style=for-the-badge&color=navy&label=GitHub&logo=github)](https://github.com/WithPrecedent/ashford/releases)
| Status | [![Build Status](https://img.shields.io/github/actions/workflow/status/WithPrecedent/ashford/ci.yml?branch=main&style=for-the-badge&color=cadetblue&label=Tests&logo=pytest)](https://github.com/WithPrecedent/ashford/actions/workflows/ci.yml?query=branch%3Amain) [![Development Status](https://img.shields.io/badge/Development-Active-seagreen?style=for-the-badge&logo=git)](https://www.repostatus.org/#active) [![Project Stability](https://img.shields.io/pypi/status/ashford?style=for-the-badge&logo=pypi&label=Stability&logoColor=yellow)](https://pypi.org/project/ashford/)
| Documentation | [![Hosted By](https://img.shields.io/badge/Hosted_by-Github_Pages-blue?style=for-the-badge&color=navy&logo=github)](https://WithPrecedent.github.io/ashford)
| Tools | [![Documentation](https://img.shields.io/badge/MkDocs-magenta?style=for-the-badge&color=deepskyblue&logo=markdown&labelColor=gray)](https://squidfunk.github.io/mkdocs-material/) [![Linter](https://img.shields.io/endpoint?style=for-the-badge&url=https://raw.githubusercontent.com/charliermarsh/Ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/Ruff) [![Dependency Manager](https://img.shields.io/badge/PDM-mediumpurple?style=for-the-badge&logo=affinity&labelColor=gray)](https://PDM.fming.dev) [![Pre-commit](https://img.shields.io/badge/pre--commit-darkolivegreen?style=for-the-badge&logo=pre-commit&logoColor=white&labelColor=gray)](https://github.com/TezRomacH/python-package-template/blob/master/.pre-commit-config.yaml) [![CI](https://img.shields.io/badge/GitHub_Actions-navy?style=for-the-badge&logo=githubactions&labelColor=gray&logoColor=white)](https://github.com/features/actions) [![Editor Settings](https://img.shields.io/badge/Editor_Config-paleturquoise?style=for-the-badge&logo=editorconfig&labelColor=gray)](https://editorconfig.org/) [![Repository Template](https://img.shields.io/badge/snickerdoodle-bisque?style=for-the-badge&logo=cookiecutter&labelColor=gray)](https://www.github.com/WithPrecedent/ashford) [![Dependency Maintainer](https://img.shields.io/badge/dependabot-navy?style=for-the-badge&logo=dependabot&logoColor=white&labelColor=gray)](https://github.com/dependabot)
| Compatibility | [![Compatible Python Versions](https://img.shields.io/pypi/pyversions/ashford?style=for-the-badge&color=steelblue&label=Python&logo=python&logoColor=yellow)](https://pypi.python.org/pypi/ashford/) [![Linux](https://img.shields.io/badge/Linux-lightseagreen?style=for-the-badge&logo=linux&labelColor=gray&logoColor=white)](https://www.linux.org/) [![MacOS](https://img.shields.io/badge/MacOS-snow?style=for-the-badge&logo=apple&labelColor=gray)](https://www.apple.com/macos/) [![Windows](https://img.shields.io/badge/windows-blue?style=for-the-badge&logo=Windows&labelColor=gray&color=orangered)](https://www.microsoft.com/en-us/windows?r=1)
| Stats | [![PyPI Download Rate (per month)](https://img.shields.io/pypi/dm/ashford?style=for-the-badge&color=steelblue&label=Downloads%20💾&logo=pypi&logoColor=yellow)](https://pypi.org/project/ashford) [![GitHub Stars](https://img.shields.io/github/stars/WithPrecedent/ashford?style=for-the-badge&color=navy&label=Stars%20⭐&logo=github)](https://github.com/WithPrecedent/ashford/stargazers) [![GitHub Contributors](https://img.shields.io/github/contributors/WithPrecedent/ashford?style=for-the-badge&color=navy&label=Contributors%20🙋&logo=github)](https://github.com/WithPrecedent/ashford/graphs/contributors) [![GitHub Issues](https://img.shields.io/github/issues/WithPrecedent/ashford?style=for-the-badge&color=navy&label=Issues%20📘&logo=github)](https://github.com/WithPrecedent/ashford/graphs/contributors) [![GitHub Forks](https://img.shields.io/github/forks/WithPrecedent/ashford?style=for-the-badge&color=navy&label=Forks%20🍴&logo=github)](https://github.com/WithPrecedent/ashford/forks)
| | |

-----

## What is ashford?

This package provides classes and decorators for a variety of Python implementations of registration, factories, and type validators.

<p align="center">
<img src="https://media.giphy.com/media/Fl7aszvRTsJhsAfyG2/giphy.gif" height="300"/>
</p>


## Why use ashford?

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

ashford`s framework supports a wide range of coding styles. You can create complex multiple inheritance structures with mixins galore or simpler, compositional objects. Even though the data structures are necessarily object-oriented, all of the tools to modify them are also available as functions, for those who prefer a more funcitonal approaching to programming. 

The project is also highly internally documented so that users and developers can easily make ashford work with their projects. It is designed for Python coders at all levels. Beginners should be able to follow the readable code and internal documentation to understand how it works. More advanced users should find complex and tricky problems addressed through efficient code.

## Getting started

### Requirements

[TODO: List any OS or other restrictions and pre-installation dependencies]

### Installation

To install `ashford`, use `pip`:

```sh
pip install ashford
```

### Usage

[TODO: Describe common use cases, with possible example(s)]

## Contributing

Contributors are always welcome. Feel free to grab an [issue](https://www.github.com/WithPrecedent/ashford/issues) to work on or make a suggested improvement. If you wish to contribute, please read the [Contribution Guide](https://www.github.com/WithPrecedent/ashford/contributing.md) and [Code of Conduct](https://www.github.com/WithPrecedent/ashford/code_of_conduct.md).

## Similar Projects

[TODO: If they exist, it is always nice to acknowledge other similar efforts]

## Acknowledgments

[TODO: Mention any people or organizations that warrant a special acknowledgment]

## License

Use of this repository is authorized under the [Apache Software License 2.0](https://www.github.com/WithPrecedent/ashford/blog/main/LICENSE).
