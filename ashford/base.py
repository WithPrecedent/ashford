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
        register subclasses and/or instances. A 'register' class method provided 
        which relies on the 'deposit' method of the associated Registry.
    AbstractRegistry (abc.ABC): base class for storing registered subclasses 
        and/or instances. 'deposit' and 'withdraw' methods are required for 
        subclasses. 

To Do:

        
"""
from __future__ import annotations
import abc
from collections.abc import Hashable, MutableMapping
import dataclasses
import inspect
from typing import Any, ClassVar, Optional, Type, Union


@dataclasses.dataclass
class AbstractFactory(abc.ABC):
    """Base class for factory mixins."""
    
    """ Required Subclass Methods """

    @abc.abstractclassmethod
    def create(
        cls, 
        source: str, 
        parameters: Optional[MutableMapping[Hashable, Any]] = None) -> (
            Type[AbstractFactory] | AbstractFactory):
        """Creates a subclass or instance based on 'source' and 'parameters'.
        
        Args:
            source (str): key for item stored in 'registry'.
            parameters: Optional[MutableMapping[Hashable, Any]]: keyword 
                arguments for a created instance. If 'parameters' are passed,
                an instance is always returned. If left as None, whether an 
                instance or class is returned depends on what the subclass 
                method dictates. Defaults to None.
                
        Returns:
            Type[AbstractFactory] | AbstractFactory: a subclass or subclass 
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
            item (object | Type[Any]): an instance to add to the registry.
            name (Optional[str]): name to use as the key when 'item' is stored
                in the registry. Defaults to None. If not passed, the function
                in 'framework.namer' may be used (depending on the subclass
                'register' method).
        
        """
        cls.registry.deposit(item = item, name = name)
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
            name (Optional[Hashable]): key to use to store 'item'. If not
                passed, a key will be created using 'framework.namer'.
                Defaults to None
                
        """
        pass

    @abc.abstractmethod
    def withdraw(
        self, 
        item: Hashable,
        parameters: Optional[MutableMapping[Hashable, Any]] = None) -> (
            object | Type[Any]):
        """Creates an instance or class based on 'item' and 'parameters'.
        
        Args:
            item (Hashable): key name corresponding to the stored item sought.
            parameters: Optional[MutableMapping[Hashable, Any]]: keyword 
                arguments to add to a created instance. If passed, an instance
                will always be returned. If None, a class or instance may be
                returned, depending on the Registry subclass method. Defaults to
                None.
            
        Returns:
            object | Type[Any]: instance or class created from stored items.
                
        """
        pass

    """ Private Methods """
    
    def _finalize_product(
        self, 
        item: object | Type[Any], 
        parameters: Optional[MutableMapping[Hashable, Any]]) -> (
            object | Type[Any]):
        """Creates a class or instance based on passed arguments.
        
        Args:
            item (object | Type[Any]): subclass or subclass instance.
            parameters: Optional[MutableMapping[Hashable, Any]]: keyword 
                arguments for a created instance. If 'parameters' are passed,
                an instance is always returned. If left as None, 'item' will
                be returned as is.
                
        Returns:
            object | Type[Any]: a subclass or subclass instance.
                
        """ 
        if parameters is None:
            return item  
        elif inspect.isclass(item):
            return item(**parameters)
        else:
            for key, value in parameters.items():
                setattr(item, key, value)
            return item
            