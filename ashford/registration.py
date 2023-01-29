"""
registration: dicts for storing subclasses and/or instances
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
    Registry(base.AbstractRegistry, camina.Dictionary): registry that stores
        subclass instances.
    Registry(base.AbstractRegistry, camina.Dictionary): registry that stores
        subclasses.
    CombinedRegistry (base.AbstractRegistry, camina.ChainDictionary): a chained registry 
        that stores both subclasses and subclass instances. 
           
To Do:
    Add decorators for each registry type (using the commented out code as a 
        template)
        
"""
from __future__ import annotations
from collections.abc import (
    Callable, Hashable, Iterator, MutableMapping, MutableSequence)
import contextlib
import copy
import dataclasses
import functools
import inspect
from typing import Any, ClassVar, Optional, Type, Union

import camina

from . import base
from . import framework

    
@dataclasses.dataclass
class Registry(base.AbstractRegistry, camina.Dictionary):
    """Base class for the storage of registered instances or subclasses.
    
    Args:
        contents (MutableMapping[Hashable, object]): stored dictionary. Defaults 
            to an empty dict.
        default_factory (Optional[Any]): default value to return or default 
            callable to use to create the default value. Defaults to None.
                          
    """
    contents: MutableMapping[Hashable, object] = dataclasses.field(
        default_factory = dict)
    default_factory: Optional[Any] = None

    """ Instance Methods """
    
    def deposit(self, item: object, name: Optional[Hashable] = None) -> None:
        """Adds 'item' to 'contents'.

        Args:
            item (object): instance to add to the registry.
            name (Optional[Hashable]): key to use to store 'item'. If not
                passed, a key will be created using 'framework.namer'.
                Defaults to None
                
        """
        key = name or framework.namer(item)
        self.add({key: item})
        return

    def withdraw(
        self, 
        item: Hashable,
        parameters: Optional[MutableMapping[Hashable, Any]] = None) -> object:
        """Creates an instance based on 'item' and 'parameters'.
        
        Args:
            item (Hashable): key name corresponding to the stored item sought.
            parameters: Optional[MutableMapping[Hashable, Any]]: keyword 
                arguments to add to a created instance. If left as None, a copy
                of a stored instance is returned. If passed, 'parameters' will
                be injected as attributes on the copied instance. Defaults to 
                None.
            
        Returns:
            object: instance created from stored items.
                
        """
        stored = copy.deepcopy(self[item])
        return self._finalize_product(item = stored, parameters = parameters)

    
@dataclasses.dataclass
class Instancer(base.AbstractRegistrar):
    """Base class for subclass registration mixins.
    
    Attributes:
        registry (ClassVar[Registry[str, object]]): stores subclass
            instances. Defaults to an instance of Registry.
            
    """
    registry: ClassVar[Registry[str, object]] = Registry()

    """ Initialization Methods """
    
    def __post_init__(self) -> None:
        """Automatically registers a subclass instance."""
        # Because InstanceRegistrar is used as a mixin, it is important to
        # call other base class '__post_init__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__post_init__() 
        self.register(item = self)


@dataclasses.dataclass
class Subclasser(base.AbstractRegistrar):
    """Base class for subclass registration mixins.
    
    Attributes:
        registry (ClassVar[Registry[str, Type[Any]]]): stores 
            subclasses. Defaults to an instance of Registry.
            
    """
    registry: ClassVar[Registry[str, Type[Any]]] = Registry()

    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        """Automatically registers subclass."""
        # Because SubclassRegistrar will be used as a mixin, it is important to 
        # call other base class '__init_subclass__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs) 
        # Automatically registers a new subclass
        cls.registry.register(item = cls)

        
@dataclasses.dataclass  
class Anthology(base.AbstractRegistry, camina.ChainDictionary):
    """Stores classes instances and classes in a chained mapping.
    
    When searching for matches, instances are prioritized over classes.
    
    The class limits the number of chained Registry instances to 2. 
    Instances are stored in the first slot of 'contents'. And, subclasses are 
    stored in the second.
    
    Args:
        contents (MutableSequence[Registry[Hashable, Any]]): list of stored 
            Registry instances. This is equivalent to the 'maps' attribute 
            of a collections.ChainMap instance but uses a different name for 
            compatibility with other mappings in Ashford. A separate 'maps' 
            property is included which points to 'contents' to ensure 
            compatibility in the opposite direction.
        default_factory (Optional[Any]): default value to return or default 
            callable to use to create the default value.
        return_first (Optional[bool]): whether to only return the first match
            found (True) or to search all of the stored Registry instances
            (False). Defaults to True.
                    
    """
    contents: MutableSequence[Registry[Hashable, Any]] = dataclasses.field(
        default_factory = list)
    default_factory: Optional[Any] = None
    return_first: Optional[bool] = True    
                 
    """ Initialization Methods """
                
    def __post_init__(self) -> None:
        """Automatically initializes 'contents' attribute."""
        with contextlib.suppress(AttributeError):
            super().__post_init__() 
        if not self.contents:
            self.contents.append(Registry())
            self.contents.append(Registry())
    
    """ Properties """
        
    def instances(self) -> Registry:
        """Returns stored instances.

        Returns:
            Registry: with stored instances.
            
        """
        return self.contents[0] 
    
    def subclasses(self) -> Registry:
        """Returns stored subclasses.

        Returns:
            Registry: with stored subclasses.
            
        """
        return self.contents[1] 

    """ Instance Methods """
    
    def deposit(
        self, 
        item: object | Type[Any], 
        name: Optional[Hashable] = None) -> None:
        """Adds 'item' to 'contents'.

        If 'item' is a class, it will be registered in the 'subclasses' 
        registry. If 'item' is an instance, it will be registered in the 
        'instances' registry and its class will be registered in the 
        'subclasses' registry. However, if an instance is passed with a 'name'
        argument, the 'name' will only be used for storing 'item' in the
        'instances' registry (and the key name will be inferred for the
        'subclasses' registry).

        Args:
            item (object | Type[Any]): subclass or instance to add to the 
                registry.
            name (Optional[Hashable]): key to use to store 'item'. If not
                passed, a key will be created using 'framework.namer'.
                Defaults to None
                
        """
        if inspect.isclass(item):
            self.deposit_subclass(item = item, name = name)
        else:
            self.deposit_instance(item = item, name = name)
            self.deposit_subclass(item = item.__class__)
        return
    
    def deposit_instance(
        self, 
        item: object, 
        name: Optional[Hashable] = None) -> None:
        """Adds 'item' to 'contents'.

        Args:
            item (object): instance to add to the registry.
            name (Optional[Hashable]): key to use to store 'item'. If not
                passed, a key will be created using 'framework.namer'.
                Defaults to None
                
        """
        self.instances.deposit(item = item, name = name)
        return
        
    def deposit_subclass(
        self, 
        item: Type[Any], 
        name: Optional[Hashable] = None) -> None:
        """Adds 'item' to 'contents'.

        Args:
            item (Type[Any]): subclass to add to the registry.
            name (Optional[Hashable]): key to use to store 'item'. If not
                passed, a key will be created using 'framework.namer'.
                Defaults to None
                
        """
        self.subclasses.deposit(item = item, name = name)
        return
     
    def withdraw(self, item: Hashable) -> Type[Any]:
        """Returns subclass from 'contents'.
        
        Args:
            item (Hashable): key name corresponding to the stored item sought.
            
        Returns:
            Type[Any]: subclass matching 'item'.
            
        """
        return self[item]    
    
    """ Dunder Methods """
    
    def __iter__(self) -> Iterator[Any]:
        """Returns iterable of 'classes' and 'instances'.

        Returns:
            Iterator: of 'classes' and 'instances'.

        """
        combined = copy.deepcopy(self.instances)
        return iter(combined.update(self.classes))

    def __len__(self) -> int:
        """Returns combined length of 'instances' and 'classes'.

        Returns:
            int: combined length of 'instances' and 'classes'.

        """
        return len(self.instances) + len(self.classes)


@dataclasses.dataclass
class Librarian(Instancer, Subclasser):
    """Base class for combined registration mixins.
    
    Attributes:
        registry (ClassVar[Anthology]): stores subclasses and subclass 
            instances. Defaults to an instance of Anthology.
            
    """
    registry: ClassVar[Anthology] = Anthology()

    
# """ Registration Decorator """

# @dataclasses.dataclass
# class registered(object):
#     """Decorator that automatically registers wrapped class or function.
    
#     registered violates the normal python convention of naming classes in 
#     capital case because it is only designed to be used as a callable decorator, 
#     where lowercase names are the norm.
    
#     All registered functions and classes are stored in the 'registry' class 
#     attribute of the wrapped item (even if it is a function). So, it is 
#     accessible with '{wrapped item name}.registry'. If the wrapped item is a 
#     class is subclassed, those subclasses will be registered as well via the 
#     '__init_subclass__' method which is copied from the Registrar class.
        
#     Wrapped functions and classes are automatically added to the stored registry
#     with the 'namer' function. Virtual subclasses can be added using the
#     'register' method which is automatically added to the wrapped function or
#     class.
 
#     Args:
#         wrapped (Callable[..., Optional[Any]]): class or function to be stored.
#         default (dict[str, Callable[..., Optional[Any]]]): any items to include
#              in the registry without requiring additional registration. Defaults
#              to an empty dict.
#         namer (Callable[[Any], str]): function to infer key names of wrapped
#             functions and classes. Defaults to the 'namify' function in ashford.
    
#     """
#     wrapped: Callable[..., Optional[Any]]
#     defaults: dict[str, Callable[..., Optional[Any]]] = dataclasses.field(
#         default_factory = dict)
#     namer: Callable[[Any], str] = dataclasses.field(default = framework.NAMER)
    
#     """ Initialization Methods """
        
#     def __call__(
#         self, 
#         *args: Any, 
#         **kwargs: Any) -> Callable[..., Optional[Any]]:
#         """Allows class to be called as a decorator.
        
#         Returns:
#             Callable[..., Optional[Any]]: callable after it has been registered.
        
#         """
#         # Updates 'wrapped' for proper introspection and traceback.
#         functools.update_wrapper(self, self.wrapped)
#         # Copies key attributes and functions to wrapped item.
#         self.wrapped.register = self.register
#         self.wrapped.registry = self.__class__.registry
#         if inspect.isclass(self.wrapped):
#             self.wrapped.__init_subclass__ = base.AbstractRegistrar.__init_subclass__
#         return self.wrapped(*args, **kwargs)        

#     """ Properties """
    
#     @property
#     def registry(self) -> MutableMapping[str, Type[Any]]:
#         """Returns internal registry.
        
#         Returns:
#             MutableMapping[str, Type[Any]]: dict of str keys and values of
#                 registered items.
                
#         """
#         if self.defaults:
#             complete = copy.deepcopy(self._registry)
#             complete.update(self.defaults)
#             return complete 
#         else:
#             return self._registry
    
#     """ Public Methods """
    
#     @classmethod
#     def register(cls, item: Type[Any], name: Optional[str] = None) -> None:
#         """Adds 'item' to 'registry'.
        
#         """
#         # The default key for storing cls is its snakecase name.
#         key = name or cls.namer(cls)
#         cls.registry[key] = item
#         return
