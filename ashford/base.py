"""
base: base classes for ashford
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
    Descriptor (abc.ABC): interface for descriptors. '__get__' and '__set__' 
        methods are required for all subclasses. A fully-featured '__set_name__'
        method is provided which creates 'attribute_name', 'owner', and 
        'private_name' attributes.
    Factory (abc.ABC): interface for factories. A 'create' class method is 
        required for subclasses.
    Registrar (abc.ABC): interface for classes that automatically register 
        classes and/or instances. A 'register' class method is provided for the 
        default registration method in the 'registry' class attribute.
    Registry (MutableMapping): interface for storing registered classes and/or 
        instances. In addition to all dict and defaultdict methods, 'deposit' 
        and 'withdraw' methods are provided for additional setting and getting
        functionality. Any compatible mutable mapping can be used for internal
        storage in the 'contents' attribute.
    Validator (abc.ABC): interface for type and value validators. Subclasses 
        must provide their own 'validate' methods.

To Do:

        
"""
from __future__ import annotations
import abc
from collections.abc import Hashable, MutableMapping, Sequence
import dataclasses
import inspect
from typing import Any, ClassVar, Optional, Type, Union

from . import configuration

       
@dataclasses.dataclass
class Descriptor(abc.ABC):
    """Base class for descriptors.
    
    Since Python currently lacks an abstract base class for descriptors, this
    class sets the basic interface for one while offering a fully-featured 
    '__set_name__' method. Since '__delete__' isn't a strict requirement for
    a descriptor (typical use cases simply rely on a call to '__get__'), it is
    not included as a subclass requirement.
    
    Attributes:
        attribute_name (str): name of the attribute for the Descriptor instance 
            in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
            This attribute contains the name of an attribute in 'owner' (and not 
            the descriptor) where the data for a descriptor will be stored.
        owner (object): object of which the Descriptor instance is an attribute.
            
    """
    
    """ Required Subclass Methods """

    @abc.abstractmethod
    def __get__(
        self, 
        owner: object, 
        objtype: Optional[Type[Any]] = None) -> Any:
        """Returns item stored in 'private_name'.
        Args:
            owner (object): object of which this validator is an attribute.
            objtype (Optional[Type[Any]]): class of 'owner'. Defaults to None.

        Returns:
            Any: stored item.
            
        """
        pass  
    
    @abc.abstractmethod
    def __set__(self, owner: object, value: Any) -> None:
        """Stores 'value' in 'private_name' of 'owner'.

        Args:
            owner (object): object of which this validator is an attribute.
            value (Any): item to store, after being validated.
            
        """
        pass    
        
    """ Dunder Methods """
    
    def __set_name__(self, owner: object, name: str) -> None:
        """Creates attributes based on 'owner' and 'item'

        Args:
            owner (object): object of which this validator is an attribute.
            name (str): name of this attribute in 'owner'. 
            
        """
        self.attribute_name = name
        self.private_name = f'_{name}'
        self.owner = owner
        return


@dataclasses.dataclass
class Factory(abc.ABC):
    """Base class for factories."""
    
    """ Required Subclass Methods """

    @abc.abstractclassmethod
    def create(cls, source: str, **kwargs: Any) -> Any:
        """Creates a subclass or instance based on 'source' and 'parameters'.
        
        Args:
            source (str): key or data for item stored in 'registry'.
                
        Returns:
            Any: created item(s).
                
        """
        pass

    
@dataclasses.dataclass
class Registrar(abc.ABC):
    """Base class for registrars.
    
    A registrar is the class that sends an item to a registry. Its functionality
    is separated from the actual registry to facilitate mixing-and-matching of
    different registry types with varied automated registrar processes in 
    ashford. If you wish to handle registration manually outside of the ashford
    ecosystem, a Registrar is not strictly needed. 
    
    Attributes:
        registry (ClassVar[Registry[Hashable, object | Type[Any]]]): stores 
            classes or instances with hashable keys.
            
    """
    registry: ClassVar[Registry[Hashable, Union[object, Type[Any]]]]

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
class Registry(MutableMapping):
    """Base class for class and/or instance registries.
    
    Any dict-like object can be used for the internal storage of Registry. All 
    of the required dict-like methods are included with a couple notable changes
    from an ordinary Python dict:
        1) When returning 'keys', 'values' and 'items', this class returns them
            as tuples instead of KeysView, ValuesView, and ItemsView.
        2) It includes the same functionality as 'defaultdict' in the python 
            standard library, including a 'setdefault' method.
        3) Its primary methods for setting and getting stored data are 'deposit'
            and 'withdraw' respectively. Those are also called by the class's
            '__setitem__' and '__getitem__' dunder methods. The reason for a 
            separate 'deposit' method is that allows for optional automatic 
            naming of stored items if a key name is not passed. A separate
            'withdraw' method is included so that users can pass parameters to
            instance the return item (or have those parameters injected as
            attributes to the return item).
    
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
    
    """ Class Methods """
    
    @classmethod
    def fromkeys(
        cls, 
        keys: Sequence[Hashable], 
        value: Any, 
        **kwargs: Any) -> Registry:
        """Emulates the 'fromkeys' class method from a python dict.

        Args:
            keys (Sequence[Hashable]): items to be keys in a new Registry.
            value (Any): the value to use for all values in a new Registry.

        Returns:
            Registry: formed from 'keys' and 'value'.
            
        """
        return cls(contents = dict.fromkeys(keys, value), **kwargs)     
     
    """ Instance Methods """

    def delete(self, item: Hashable) -> None:
        """Deletes 'item' in 'contents'.

        Args:
            item (Hashable): key in 'contents' to delete the key/value pair.

        """
        del self.contents[item]
        return

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
        name = name or configuration.KEYER(item)
        self.contents[name] = item
        return

    def get(self, key: Hashable, default: Optional[Any] = None) -> Any:
        """Returns value in 'contents' or default options.
        
        Args:
            key (Hashable): key for value in 'contents'.
            default (Optional[Any]): default value to return if 'key' is not 
                found in 'contents'.
        
        Raises:
            KeyError: if 'key' is not in the Registry and 'default' and the
                'default_factory' attribute are both None.
        
        Returns:
            Any: value matching key in 'contents' or 'default_factory' value. 
            
        """
        try:
            return self[key]
        except (KeyError, TypeError):
            if default is None:
                if self.default_factory is None:
                    raise KeyError(f'{key} is not in the registry')
                else:
                    try:
                        return self.default_factory()
                    except TypeError:
                        return self.default_factory
            else:
                try:
                    return self.default()
                except TypeError:
                    return default
                
    def items(self) -> tuple[tuple[Hashable, Any], ...]:
        """Emulates python dict 'items' method.
        
        Returns:
            tuple[tuple[Hashable], Any]: a tuple equivalent to dict.items(). 
            
        """
        return tuple(zip(self.keys(), self.values()))

    def keys(self) -> tuple[Hashable, ...]:
        """Returns 'contents' keys as a tuple.
        
        Returns:
            tuple[Hashable, ...]: a tuple equivalent to dict.keys().
            
        """
        return tuple(self.contents.keys())

    def setdefault(self, value: Any) -> None:
        """sets default value to return when 'get' method is used.
        
        Args:
            value (Any): default value to return when 'get' is called and the
                'default' parameter to 'get' is None.
            
        """
        self.default_factory = value 
        return
      
    def values(self) -> tuple[Any, ...]:
        """Returns 'contents' values as a tuple.
        
        Returns:
            tuple[Any, ...]: a tuple equivalent to dict.values().
            
        """
        return tuple(self.contents.values())
            
    def withdraw(
        self, 
        item: Hashable, 
        parameters: Optional[MutableMapping[Hashable, Any]]) -> (
            object | Type[Any]):
        """Returns an instance or class based on 'item'.
        
        Args:
            item (Hashable): key name corresponding to the stored item sought.
            parameters: Optional[MutableMapping[Hashable, Any]]: keyword 
                arguments for a created instance. If 'parameters' are passed,
                an instance is always returned. If left as None, 'item' will
                be returned as is.
                           
        Returns:
            object | Type[Any]: instance or class from stored items.
                
        """
        value = self.get(key = item)
        if value is configuration.MISSING:
            raise KeyError(f'{item} is not in the registry')
        elif parameters is None:
            return item  
        elif inspect.isclass(item):
            return item(**parameters)
        else:
            for key, value in parameters.items():
                setattr(item, key, value)
            return item
    
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

    
@dataclasses.dataclass
class Validator(abc.ABC):
    """Base class for type or value validators."""
    
    """ Required Subclass Methods """

    @abc.abstractmethod
    def validate(self, item: Any) -> Any:
        """Returns a validated 'item'.

        Args:
            item (Any): object to validate.

        Returns:
            Any: validated object.
            
        """   
        pass   
