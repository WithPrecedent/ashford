"""
registry: classes and functions for registration
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
    registered (object): a decorator for automatic registration of wrapped 
        classes and functions.
    Registrar (object): automatically stores subclasses in 'registry' class 
        attribute and allows virtual subclass registration using the 'register'
        class method.
        
"""
from __future__ import annotations
from collections.abc import (
    Callable, Hashable, Iterator, MutableMapping, Sequence)
import copy
import dataclasses
import functools
import inspect
from typing import Any, ClassVar, Optional, Type

import camina


@dataclasses.dataclass  # type: ignore
class CombinedRegistrar(MutableMapping):
    """Stores classes instances and classes in a chained mapping.
    
    When searching for matches, instances are prioritized over classes.
    
    Args:
        classes (Catalog): a catalog of stored classes. Defaults to any empty
            Catalog.
        instances (Catalog): a catalog of stored class instances. Defaults to an
            empty Catalog.
                 
    """
    classes: camina.Catalog[str, Type[Any]] = dataclasses.field(
        default_factory = camina.Catalog)
    instances: camina.Catalog[str, object] = dataclasses.field(
        default_factory = camina.Catalog)
        
    """ Public Methods """
    
    def deposit(
        self, 
        item: Type[Any] | object,
        name: Optional[Hashable] = None) -> None:
        """Adds 'item' to 'classes' and/or 'instances'.

        If 'item' is a class, it is added to 'classes.' If it is an object, it
        is added to 'instances' and its class is added to 'classes'. The key
        used to store instances and classes are different if the instance has
        a 'name' attribute (which is used as the key for the instance).
        
        Args:
            item (Type[Any] | object): class or instance to add to the 
                Library instance.
            name (Optional[Hashable]): key to use to store 'item'. If not
                passed, a key will be created using the 'namify' method.
                Defaults to None
                
        """
        key = name or camina.namify(item)
        if inspect.isclass(item):
            self.classes[key] = item
        elif isinstance(item, object):
            self.instances[key] = item
            # Key for the class will be different because it is inferred from
            # the class and not any attributes.
            self.deposit(item = item.__class__)
        else:
            raise TypeError(f'item must be a class or a class instance')
        return
    
    def delete(self, item: Hashable) -> None:
        """Removes an item from 'instances' or 'classes.'
        
        If 'item' is found in 'instances', it will not also be removed from 
        'classes'.

        Args:
            item (Hashable): key name of item to remove.
            
        Raises:
            KeyError: if 'item' is neither found in 'instances' or 'classes'.

        """
        try:
            del self.instances[item]
        except KeyError:
            try:
                del self.classes[item]
            except KeyError:
                raise KeyError(f'{item} is not found in the Library')
        return    

    def withdraw(
        self, 
        item: Hashable | Sequence[Hashable], 
        parameters: Optional[MutableMapping[Hashable, Any]] = None) -> (
            Type[Any] | object):
        """Returns instance or class of first match of 'item' from catalogs.
        
        The method prioritizes the 'instances' catalog over 'classes' and any
        passed names in the order they are listed.
        
        An instance will be returned so long as 'parameters' is not None. 
        
        Args:
            item (Hashable | Sequence[Hashable]): key name(s) of stored 
                item(s) sought.
            parameters (Optional[MutableMapping[Hashable, Any]]]): keyword 
                arguments to pass to a newly created instance or, if the stored 
                item is already an instance to be manually added as attributes. 
                If not passed, the found item will be returned unaltered. 
                Defaults to None.
            
        Raises:
            KeyError: if 'item' does not match a key to a stored item in either
                'instances' or 'classes'.
            
        Returns:
            Type[Any] | object: returns a class or instance if 'parameters' 
                are None, depending upon with Catalog the matching item is 
                found. If 'parameters' are passed, an instance is always 
                returned.
            
        """
        items = camina.listify(item)
        item = None
        for key in items:
            for catalog in ['instances', 'classes']:
                try:
                    item = getattr(self, catalog)[key]
                    break
                except KeyError:
                    pass
            if item is not None:
                break
        if item is None:
            raise KeyError(f'No matching item for {item} was found')
        if parameters is not None:
            if ('name' in item.__annotations__.keys() 
                    and 'name' not in parameters):
                parameters['name'] = items[0]
            if inspect.isclass(item):
                return item(**parameters)
            else:
                instance = copy.deepcopy(item)
                for key, value in parameters.items():
                    setattr(instance, key, value)
                return instance
        return item # type: ignore
    
    """ Dunder Methods """

    def __getitem__(self, key: Hashable) -> Any:
        """Returns value for 'key' in 'contents'.

        Args:
            key (Hashable): key in 'contents' for which a value is sought.

        Returns:
            Any: value stored in 'contents'.

        """
        return self.withdraw(item = key)

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """sets 'key' in 'contents' to 'value'.

        Args:
            key (Hashable): key to set in 'contents'.
            value (Any): value to be paired with 'key' in 'contents'.

        """
        self.deposit(item = value, name = key)
        return
    
    def __delitem__(self, item: Hashable) -> None:
        """Deletes 'item' from 'contents'.
        
        Args:
            item (Any): item or key to delete in 'contents'.
        
        Raises:
            KeyError: if 'item' is not in 'contents'.
            
        """
        self.delete(item = item)
        return
    
    def __iter__(self) -> Iterator[Any]:
        """Returns iterable of 'contents'.

        Returns:
            Iterator: of 'contents'.

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
class SubclassRegistrar(object):
    """Mixin which automatically registers subclasses.
    
    Args:
        registry (ClassVar[MutableMapping[str, Type[Any]]]): key names are str
            names of a subclass (snake_case by default) and values are the 
            subclasses. Defaults to an empty dict.  
            
    """
    registry: ClassVar[MutableMapping[str, Type[Any]]] = {}
    
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
    
    @classmethod
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
    
    
""" Registration Decorator """

@dataclasses.dataclass
class registered(object):
    """Decorator that automatically registers wrapped class or function.
    
    registered violates the normal python convention of naming classes in 
    capital case because it is only designed to be used as a callable decorator, 
    where lowercase names are the norm.
    
    All registered functions and classes are stored in the 'registry' class 
    attribute of the wrapped item (even if it is a function). So, it is 
    accessible with '{wrapped item name}.registry'. If the wrapped item is a 
    class is subclassed, those subclasses will be registered as well via the 
    '__init_subclass__' method which is copied from the Registrar class.
        
    Wrapped functions and classes are automatically added to the stored registry
    with the 'namer' function. Virtual subclasses can be added using the
    'register' method which is automatically added to the wrapped function or
    class.
 
    Args:
        wrapped (Callable[..., Optional[Any]]): class or function to be stored.
        default (dict[str, Callable[..., Optional[Any]]]): any items to include
             in the registry without requiring additional registration. Defaults
             to an empty dict.
        namer (Callable[[Any], str]): function to infer key names of wrapped
            functions and classes. Defaults to the 'namify' function in ashford.
    
    """
    wrapped: Callable[..., Optional[Any]]
    defaults: dict[str, Callable[..., Optional[Any]]] = dataclasses.field(
        default_factory = dict)
    namer: Callable[[Any], str] = camina.namify
    
    """ Initialization Methods """
        
    def __call__(
        self, 
        *args: Any, 
        **kwargs: Any) -> Callable[..., Optional[Any]]:
        """Allows class to be called as a decorator.
        
        Returns:
            Callable[..., Optional[Any]]: callable after it has been registered.
        
        """
        # Updates 'wrapped' for proper introspection and traceback.
        functools.update_wrapper(self, self.wrapped)
        # Copies key attributes and functions to wrapped item.
        self.wrapped.register = self.register
        self.wrapped.registry = self.__class__.registry
        if inspect.isclass(self.wrapped):
            self.wrapped.__init_subclass__ = Registrar.__init_subclass__
        return self.wrapped(*args, **kwargs)        

    """ Properties """
    
    @property
    def registry(self) -> MutableMapping[str, Type[Any]]:
        """Returns internal registry.
        
        Returns:
            MutableMapping[str, Type[Any]]: dict of str keys and values of
                registered items.
                
        """
        if self.defaults:
            complete = copy.deepcopy(self._registry)
            complete.update(self.defaults)
            return complete 
        else:
            return self._registry
    
    """ Public Methods """
    
    @classmethod
    def register(cls, item: Type[Any], name: Optional[str] = None) -> None:
        """Adds 'item' to 'registry'.
        
        """
        # The default key for storing cls is its snakecase name.
        key = name or cls.namer(cls)
        cls.registry[key] = item
        return
