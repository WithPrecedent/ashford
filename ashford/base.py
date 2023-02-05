"""
base: ashford base classes
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
    AbstractFactory (abc.ABC): base class for all factories. A 'create' class 
        method is required for subclasses.
    AbstractRegistrar (abc.ABC): base class for all classes that automatically 
        register subclasses and/or instances. A 'register' class method is 
        provided for the default registration method.
    AbstractRegistry (abc.ABC): base class for storing registered subclasses 
        and/or instances. 'deposit' and 'withdraw' methods are required for 
        subclasses. 

To Do:

        
"""
from __future__ import annotations
import abc
from collections.abc import Hashable, MutableMapping
import dataclasses
from typing import Any, ClassVar, Optional, Type, Union

from . import framework


@dataclasses.dataclass
class AbstractFactory(abc.ABC):
    """Base class for factory mixins."""
    
    """ Required Subclass Methods """

    @abc.abstractclassmethod
    def create(
        cls, 
        source: str, 
        parameters: Optional[MutableMapping[Hashable, Any]] = None) -> (
            AbstractFactory | Type[AbstractFactory]):
        """Creates a subclass or instance based on 'source' and 'parameters'.
        
        Args:
            source (str): key or data for item stored in 'registry'.
            parameters: Optional[MutableMapping[Hashable, Any]]: keyword 
                arguments for a created instance. If 'parameters' are passed,
                an instance is always returned. If left as None, whether an 
                instance or class is returned depends on what the subclass 
                method dictates. Defaults to None.
                
        Returns:
            AbstractFactory | Type[AbstractFactory]: a subclass or subclass 
                instance.
                
        """
        pass

        
@dataclasses.dataclass
class AbstractRegistrar(abc.ABC):
    """Base class for registration mixins.
    
    This should be subclassed by any class that you wish for automatic 
    registration to occur. Regardless of the type of Registrar, any registered
    items are stored in the 'registry' class attribute.
    
    Attributes:
        registry (ClassVar[AbstractRegistry[str, object | Type[Any]]]): stores 
            classes or instances with str keys.
            
    """
    registry: ClassVar[AbstractRegistry[str, Union[object, Type[Any]]]]

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
                in 'framework.NAMER' may be used.
        
        """
        try:
            cls.registry.deposit(item = item, name = name)
        except AttributeError:
            name = name or framework.NAMER(item)
            cls.registry[name] = item
        return


@dataclasses.dataclass
class AbstractRegistry(abc.ABC):
    """Base class for the storage of registered classes and/or instances.
    
    Args:
        contents (MutableMapping[Hashable, Any]): stored dictionary. Defaults 
            to an empty dict.
        default_factory (Optional[Any]): default value to return or default 
            callable to use to create the default value. Defaults to None.
                          
    """
    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    default_factory: Optional[Any] = None

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def deposit(
        self, 
        item: object | Type[Any],
        name: Optional[Hashable] = None) -> None:
        """Adds 'item' to 'contents'.

        Args:
            item (object | Type[Any]): class or instance to add to the registry.
            name (Optional[Hashable]): key to use to store 'item'. Defaults to
                None.
                
        """
        pass
    
    @abc.abstractmethod            
    def withdraw(self, item: Hashable) -> object | Type[Any]:
        """Returns an instance or class based on 'item'.
        
        Args:
            item (Hashable): key name corresponding to the stored item sought.
            
        Returns:
            object | Type[Any]: instance or class from stored items.
                
        """
        pass

    """ Dunder Methods """
    
    def __getitem__(self, key: Hashable) -> object | Type[Any]:
        """Returns a stored item.
        
        Args:
            key (Hashable): key name corresponding to the stored item sought.
            
        Returns:
            object | Type[Any]: instance or class created from stored items.
                
        """
        return self.withdraw(item = key)
    
    def __setitem__(self, key: Hashable, value: object | Type[Any]) -> None:
        """Stores 'value' with 'key'.
        
        Args:
            key(Hashable): key name for storing 'value'.
            value (object | Type[Any]): instance or class to store.
                
        """
        self.deposit(item = value, name = key)
        return
    