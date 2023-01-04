"""
base: base classes for ashford
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2022, Corey Rayburn Yung
License: Apache-2.0

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

Contents:
    Keystones (abc.ABC): stores base classes, defaults, and subclasses for
        Keystone.
    Keystone (abc.ABC): mixin for any class in a package that should be
        automatically registered and sorted by base Keystone subclass. 

To Do:

        
"""
from __future__ import annotations
import abc
from collections.abc import MutableMapping
import contextlib
import dataclasses
import inspect
from typing import Any, ClassVar, Optional, Type

import camina


@dataclasses.dataclass
class Factory(abc.ABC):
    """Base class for factory mixins."""
    
    """ Required Subclass Methods """

    @abc.abstractclassmethod
    def create(
        cls,
        source: Any, 
        **kwargs: Any) -> Type[Factory] | Factory:
        """Returns a subclass or subclass instance.

        Args:
            source (Any): argument indicating creation method to use.

        Returns:
            Type[Factory] | Factory: subclass or subclass instance of 
                SourceFactory.
            
        """
        pass


@dataclasses.dataclass
class Registrar(abc.ABC):
    """Base class for registration mixins."""
    
    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass in 'registry'."""
        # Because Registrar will often be used as a mixin, it is important to
        # call other base class '__init_subclass__' methods, if they exist.
        try:
            super().__init_subclass__(*args, **kwargs) # type: ignore
        except AttributeError:
            pass
        cls.register(item = cls)

    """ Public Methods """
    
    @abc.abstractclassmethod
    def register(cls, item: Type[Any], name: Optional[str] = None) -> None:
        """Adds 'item' to 'registry'.
        
        A separate 'register' method is included so that virtual subclasses can
        also be registered.
        
        Args:
            item (Type[Any]): a class to add to the registry.
            name (Optional[str]): name to use as the key when 'item' is stored
                in 'registry'. Defaults to None. If not passed, the 'namify'
                method will be used to 
        
        """
        # if abc.ABC not in cls.__bases__:
        # The default key for storing cls relies on the 'namify' method, 
        # which usually will use the snakecase name of 'item'.
        key = name or camina.namify(cls)
        cls.registry[key] = item
        return   
  