"""
registration: registration mixins and decorators
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
    Anthology (base.Registry, camina.Dictionary): registry that stores
        classes or instances.
    Corpus (base.Registry, camina.ChainDictionary): registry that 
        stores classes and instances.
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


""" Anthology Classes """
    
@dataclasses.dataclass
class Anthology(base.Registry, camina.Dictionary):
    """Stores registered instances or classes.
    
    Args:
        contents (MutableMapping[Hashable, Any]): stored dictionary. Defaults 
            to an empty dict.
        default_factory (Optional[Any]): default value to return or default 
            callable to use to create the default value. Defaults to None.
                          
    """
    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    default_factory: Optional[Any] = None

    """ Instance Methods """
    
    def deposit(
        self, 
        item: object | Type[Any],
        name: Optional[Hashable] = None) -> None:
        """Adds 'item' to 'contents'.

        Args:
            item (object | Type[Any]): class or instance to add to the registry.
            name (Optional[Hashable]): key to use to store 'item'. If not
                passed, a key will be created using 'configuration.KEYER'.
                Defaults to None.
                
        """
        name = name or configuration.KEYER(item)
        self.contents[name] = item
        return
            
    def withdraw(self, item: Hashable) -> object | Type[Any]:
        """Returns an instance or class based on 'item'.
        
        Args:
            item (Hashable): key name corresponding to the stored item sought.
            
        Returns:
            object | Type[Any]: instance or class from stored items.
                
        """
        try:
            return self.contents[item]
        except (KeyError, TypeError):
            if self.default_factory is None:
                raise KeyError(f'{item} is not in the registry')
            try:
                return self.default_factory()
            except TypeError:
                return self.default_factory
   
       
@dataclasses.dataclass  
class Corpus(base.Registry, camina.ChainDictionary):
    """Stores classes instances and classes in a chained mapping.
    
    When searching for matches, instances are prioritized over classes.
    
    The class should limit the number of chained Anthology instances to 2. 
    Instances are stored in the first slot of 'contents'. And, classes are 
    stored in the second.
    
    Args:
        contents (MutableSequence[MutableMapping[Hashable, Any]]): list of 
            stored Anthology instances. This is equivalent to the 'maps' 
            attribute of a collections.ChainMap instance but uses a different 
            name for compatibility with other mappings in Ashford. A separate 
            'maps' property is included which points to 'contents' to ensure 
            compatibility in the opposite direction.
        default_factory (Optional[Any]): default value to return or default 
            callable to use to create the default value.
        return_first (Optional[bool]): whether to only return the first match
            found (True) or to search all of the stored Anthology instances
            (False). Defaults to True.
        storage (Optional[Type[Anthology]]): the class to use for each registry
            stored in 'contents'.
                    
    """
    contents: MutableSequence[MutableMapping[Hashable, Any]] = (
        dataclasses.field(default_factory = list))
    default_factory: Optional[Any] = None
    return_first: Optional[bool] = True
    storage: Optional[Type[MutableMapping]] = Anthology  
                 
    """ Initialization Methods """
                
    def __post_init__(self) -> None:
        """Automatically initializes 'contents' attribute."""
        with contextlib.suppress(AttributeError):
            super().__post_init__() 
        if not self.contents:
            self.contents.append(self.storage())
            self.contents.append(self.storage())
    
    """ Properties """
     
    @property    
    def instances(self) -> Anthology:
        """Returns stored instances.

        Returns:
            Anthology: with stored instances.
            
        """
        return self.contents[0] 
     
    @property     
    def classes(self) -> Anthology:
        """Returns stored classes.

        Returns:
            Anthology: with stored classes.
            
        """
        return self.contents[1] 

    """ Instance Methods """
    
    def deposit(
        self, 
        item: object | Type[Any], 
        name: Optional[Hashable] = None) -> None:
        """Adds 'item' to 'contents'.

        If 'item' is a class, it will be registered in the 'classes' 
        registry. If 'item' is an instance, it will be registered in the 
        'instances' registry and its class will be registered in the 
        'classes' registry. However, if an instance is passed with a 'name'
        argument, the 'name' will only be used for storing 'item' in the
        'instances' registry (and the key name will be inferred for the
        'classes' registry).

        Args:
            item (object | Type[Any]): subclass or instance to add to the 
                registry.
            name (Optional[Hashable]): key to use to store 'item'. If not
                passed, a key will be created using 'configuration.KEYER'.
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
                passed, a key will be created using 'configuration.KEYER'.
                Defaults to None
                
        """
        name = name or configuration.KEYER(item)
        self.instances[name] = item
        return
        
    def deposit_subclass(
        self, 
        item: Type[Any], 
        name: Optional[Hashable] = None) -> None:
        """Adds 'item' to 'contents'.

        Args:
            item (Type[Any]): subclass to add to the registry.
            name (Optional[Hashable]): key to use to store 'item'. If not
                passed, a key will be created using 'configuration.KEYER'.
                Defaults to None
                
        """
        name = name or configuration.KEYER(item)
        self.classes[name] = item
        return
     
    def withdraw(self, item: Hashable) -> Type[Any]:
        """Returns subclass from 'contents'.
        
        Args:
            item (Hashable): key name corresponding to the stored item sought.
            
        Returns:
            Type[Any]: subclass matching 'item'.
            
        """
        matches = []
        for dictionary in self.contents:
            try:
                match = dictionary.get(item)
                if match is not None:
                    matches.append(match)
                if self.return_first:
                    return matches[0]
            except KeyError:
                pass
        if len(matches) == 0:
            raise KeyError(f'{item} is not found in the Corpus')
        if len(matches) > 1:
            return matches[0]
        else:
            return matches
        
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


""" Registrar Classes """
   
@dataclasses.dataclass
class Instancer(base.Registrar):
    """Base class for subclass registration mixins.
    
    Attributes:
        registry (ClassVar[MutableMapping[Hashable, object]]): stores subclass 
            instances. Defaults to an instance of Anthology.
            
    """
    registry: ClassVar[MutableMapping[Hashable, object]] = Anthology()

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
    registry: ClassVar[MutableMapping[Hashable, Type[Any]]] = Anthology()

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
    registry: ClassVar[MutableMapping[Hashable, Any]] = Corpus()

    
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
#     with the 'keyer' function. Virtual subclasses can be added using the
#     'register' method which is automatically added to the wrapped function or
#     class.
 
#     Args:
#         wrapped (Callable[..., Optional[Any]]): class or function to be stored.
#         default (dict[str, Callable[..., Optional[Any]]]): any items to include
#              in the registry without requiring additional registration. Defaults
#              to an empty dict.
#         keyer (Callable[[Any], str]): function to infer key names of wrapped
#             functions and classes. Defaults to the 'namify' function in ashford.
    
#     """
#     wrapped: Callable[..., Optional[Any]]
#     defaults: dict[str, Callable[..., Optional[Any]]] = dataclasses.field(
#         default_factory = dict)
#     keyer: Callable[[Any], str] = dataclasses.field(default = configuration.KEYER)
    
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
#             self.wrapped.__init_subclass__ = base.Registrar.__init_subclass__
#         return self.wrapped(*args, **kwargs)        

#     """ Properties """
    
#     @property
#     def registry(self) -> MutableMapping[Hashable, Type[Any]]:
#         """Returns internal registry.
        
#         Returns:
#             MutableMapping[Hashable, Type[Any]]: dict of str keys and values of
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
#         key = name or cls.keyer(cls)
#         cls.registry[key] = item
#         return
