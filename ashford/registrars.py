"""
registrars: tools to register classes and/or instances
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
    Instancer (base.Registrar): automatically registers instances in a 
        Anthology.
    Subclasser (base.Registrar): automatically registers subclasses in a
        Anthology.
    Curator (base.Registrar): automatically registers subclasses and 
        instances in an Corpus.
           
To Do:
    Add decorators for each registry type (using the commented out code as a 
        template)
        
"""
from __future__ import annotations
from collections.abc import Hashable, Iterator, MutableMapping, MutableSequence
import contextlib
import copy
import dataclasses
# import functools
import inspect
from typing import Any, ClassVar, Optional, Type

import camina

from . import base
from . import configuration
from . import registries


@dataclasses.dataclass
class Instancer(base.Registrar):
    """Base class for subclass registration mixins.
    
    Attributes:
        registry (ClassVar[MutableMapping[Hashable, object]]): stores subclass 
            instances. Defaults to an instance of Anthology.
            
    """
    registry: ClassVar[MutableMapping[Hashable, object]] = (
        registries.Anthology())

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Automatically registers a subclass instance."""
        # Because Instancer is used as a mixin, it is important to call other 
        # base class '__post_init__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        # Automatically registers a new instance.
        try:
            self.__class__.registry.deposit(item = self)
        except AttributeError:
            key = configuration.KEYER(self)
            self.__class__.registry[key] = self

    """ Class Methods """
        
    @classmethod
    def register(
        cls, 
        item: object | Type[Any], 
        name: Optional[str] = None) -> None:
        """Adds 'item' to a registry.
        
        Args:
            item (object | Type[Any]): an instance or class to add to the 
                registry.
            name (Optional[str]): name to use as the key when 'item' is stored
                in the registry. Defaults to None. If not passed, the function
                in 'configuration.KEYER' may be used.
        
        """
        cls.registry[name] = item
        return
   

@dataclasses.dataclass
class Subclasser(base.Registrar):
    """Base class for subclass registration mixins.
    
    Attributes:
        registry (ClassVar[MutableMapping[Hashable, Type[Any]]): stores 
            subclasses. Defaults to an instance of Anthology.
            
    """
    registry: ClassVar[MutableMapping[Hashable, Type[Any]]] = (
        registries.Anthology())

    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        """Automatically registers subclass."""
        # Because Subclasser will be used as a mixin, it is important to call 
        # other base class '__init_subclass__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs) 
        # Automatically registers a new subclass.
        try:
            cls.registry.deposit(item = cls)
        except AttributeError:
            key = configuration.KEYER(cls)
            cls.registry[key] = cls

    """ Class Methods """
        
    @classmethod
    def register(
        cls, 
        item: object | Type[Any], 
        name: Optional[str] = None) -> None:
        """Adds 'item' to a registry.
        
        Args:
            item (object | Type[Any]): an instance or class to add to the 
                registry.
            name (Optional[str]): name to use as the key when 'item' is stored
                in the registry. Defaults to None. If not passed, the function
                in 'configuration.KEYER' may be used.
        
        """
        cls.registry[name] = item
        return
    
 
@dataclasses.dataclass
class Curator(Instancer, Subclasser):
    """Base class for combined registration mixins.
    
    Attributes:
        registry (ClassVar[MutableMapping[Hashable, Any]]): stores subclasses 
            and subclass instances. Defaults to an instance of Corpus.
            
    """
    registry: ClassVar[MutableMapping[Hashable, Any]] = registries.Corpus()
