"""
unified: package-level registration and factory system
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2023, Corey Rayburn Yung
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
    Library (storage.Anthology): base class for storing Keystone 
        subclasses and/or subclass instances.
    Librarian (object): stores base classes, defaults, and subclasses for
        Keystone.
    Keystone (abc.ABC): mixin for any class in a package that should be
        automatically registered and sorted by base Keystone subclass. 

To Do:

        
"""
from __future__ import annotations
import abc
from collections.abc import Hashable, MutableMapping, MutableSequence
import contextlib
import dataclasses
import inspect
from typing import Any, ClassVar, Optional, Type

import camina

from . import configuration
from . import factories
from . import registrars
from . import validators



@dataclasses.dataclass
class Keystone(abc.ABC):
    """Mixin for core package base classes.
    
    Attributes:
        registry (ClassVarLibrarian]): stores subclasses and/or instances. 
            
    """
    registry: ClassVar[Librarian]

    """ Class Methods """
    
    @classmethod
    def set_registry(cls, registry: Librarian | Type[Librarian]) -> None:
        """Assigns 'registry' class attribute to 'registry' argument.
        
        Args:
            registry (registry: Librarian | Type[Librarian]): registry to store 
                Keystone subclasses and/or subclass instances.
            
        Raises:
            TypeError: if 'registry' is not a subclass or subclass instance of 
                Librarian.
            
        """
        if issubclass(registry, Librarian):
            cls.registry = registry()
        elif isinstance(registry, Librarian):
            cls.registry = registry
        else:
            raise TypeError(
                'registry must be a subclass or subclass instance of Librarian')
        return

       
@dataclasses.dataclass
class CuratorKeystone(
    Keystone, registrars.Curator, factories.AnthologyFactory, abc.ABC):
    """Mixin for core package base classes.
    
    Attributes:
        registry (ClassVar[Librarian]): stores subclasses and instances. 
            Defaults to an empty CorpusLibrarian.
            
    """
    registry: ClassVar[Librarian] = Librarian()
  
         
@dataclasses.dataclass
class InstancerKeystone(
    Keystone, registrars.Instancer, factories.AnthologyFactory, abc.ABC):
    """Mixin for core package base classes.
    
    Attributes:
        registry (ClassVar[Librarian]): stores subclass instances. Defaults to 
            an empty AnthologyLibrarian.
            
    """
    registry: ClassVar[Librarian] = Librarian()
     
  
@dataclasses.dataclass
class SubclasserKeystone(
    Keystone, registrars.Subclasser, factories.AnthologyFactory, abc.ABC):
    """Mixin for core package base classes.
    
    Attributes:
        registry (ClassVar[Librarian]): stores subclasses. Defaults to 
            an empty AnthologyLibrarian.
            
    """
    registry: ClassVar[Librarian] = Librarian()
     