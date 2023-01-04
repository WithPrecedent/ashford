"""
unified: package-level registration and factory system
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
class Keystones(abc.ABC):
    """Stores Keystone subclasses.
    
    For each Keystone, a class attribute is added with the snakecase name of 
    that Keystone. In that class attribute, an camina.Dictionary is the value 
    and it stores all Keystone subclasses of that type (again using snakecase 
    names as keys).
    
    Attributes:
        bases (ClassVar[camina.Dictionary]): dictionary of all direct Keystone 
            subclasses. Keys are snakecase names of the Keystone subclass and
            values are the base Keystone subclasses.
        defaults (ClassVar[camina.Dictionary]): dictionary of the default class
            for each of the Keystone subclasses. Keys are snakecase names of the
            base type and values are Keystone subclasses.
        All direct Keystone subclasses will have an attribute name added
        dynamically.
        
    """
    bases: ClassVar[camina.Dictionary] = camina.Dictionary()
    defaults: ClassVar[camina.Dictionary] = camina.Dictionary()
        
    """ Public Methods """
    
    @classmethod
    def add(cls, item: Type[Keystone]) -> None:
        """Adds a new keystone attribute with an empty dictionary.

        Args:
            item (Type[Keystone]): direct Keystone subclass from which the name 
                of a new attribute should be derived.
            
        """
        name = cls._get_name(item = item)
        cls.bases[name] = item
        setattr(cls, name, camina.Dictionary())
        if abc.ABC not in item.__bases__:
            cls.set_default(item = item, base = name)
        else:
            cls.defaults[name] = None
        return
    
    @classmethod
    def classify(cls, item: str | Type[Keystone] | Keystone) ->str:
        """Returns the str name of the Keystone of which 'item' is.

        Args:
            item (str | Type[Keystone] | Keystone): Keystone subclass, subclass
                instance, or its str name.

        Raises:
            ValueError: if 'item' does not match a subclass of any Keystone 
                type.
            
        Returns:
            str: snakecase str name of the Keystone base type of which 'item' is 
                a subclass or subclass instance.
                
        """
        if isinstance(item, str):
            for key in cls.bases.keys():
                subtype_dict = getattr(cls, key)
                for name in subtype_dict.keys():
                    if item == name:
                        return key
        else:
            if not inspect.isclass(item):
                item = item.__class__
            for key, value in cls.bases.items():
                if issubclass(item, value):
                    return key
        raise ValueError(f'{item} is not a subclass of any Keystone')
              
    @classmethod
    def register(
        cls, 
        item: Type[Keystone],
        name: Optional[str] = None) -> None:
        """Registers 'item' in the appropriate class attribute registry.
        
        Args:
            item (Type[Keystone]): Keystone subclass to register.
            name (Optional[str], optional): key name to use in storing 'item'. 
                Defaults to None.
            
        """
        name = name or cls._get_name(item = item, name = name)
        keystone = cls.classify(item)
        getattr(cls, keystone)[name] = item
        if cls.defaults[keystone] is None and abc.ABC not in item.__bases__:
            cls.set_default(item = item, base = keystone)
        return
              
    @classmethod
    def set_default(
        cls, 
        item: Type[Keystone],
        name: Optional[str] = None,
        base: Optional[str] = None) -> None:
        """Registers 'item' as the default subclass of 'base'.
        
        If 'base' is not passed, the 'classify' method will be used to determine
        the appropriate base.
        
        Args:
            item (Type[Keystone]): Keystone subclass to make the default.
            name (Optional[str], optional): key name to use in the 'defaults'
                dictionary. Defaults to None.
            base (Optional[str]): key name to use in storing 'item'. Defaults to 
                None.
            
        """
        key = base or cls.classify(item)
        name = cls._get_name(item = item, name = name)
        cls.defaults[key] = name
        return
    
    @classmethod
    def validate(
        cls,
        item: object,
        attribute: str,
        parameters: Optional[MutableMapping[str, Any]] = None) -> object:
        """Creates or validates 'attribute' in 'item'.

        Args:
            item (object): object (often a Project or Manager instance) of which
                a Keystone in 'attribute' needs to be validated or 
                created. 
            attribute (str): name of the attribute' in item containing a value
                to be validated or which provides information to create an
                appropriate instance.
            parameters (Optional[MutableMapping[str, Any]]): parameters to pass
                to or inject in the Keystone subclass instance.

        Raises:
            ValueError: if the value of 'attribute' in 'item' does match any
                known subclass or subclass instance of that Keystone
                subtype.

        Returns:
            object: completed, linked instance.
            
        """    
        parameters = parameters or {}   
        instance = None
        # Get current value of 'attribute' in 'item'.
        value = getattr(item, attribute)
        # Get the corresponding base class.
        base = cls.bases[attribute]
        # Gets the relevant registry for 'attribute'.
        registry = getattr(cls, attribute)
        # Adds parameters to 'value' is already an instance of the appropriate 
        # base type.
        if isinstance(value, base):
            for parameter, argument in parameters.items():
                setattr(value, parameter, argument)  
            instance = value
        # Selects default class for 'attribute' if none exists.
        elif value is None:
            name = cls.defaults[attribute]
            if name:
                value = registry[name]
            else:
                raise ValueError(
                    f'Neither a value for {attribute} nor a default class '
                    f'exists')
        # Uses str value to select appropriate subclass.
        elif isinstance(value, str):
            name = getattr(item, attribute)
            value = registry[name]
        # Gets name of class if it is already an appropriate subclass.
        elif inspect.issubclass(value, base):
            name = camina.namify(value)
        else:
            raise ValueError(f'{value} is not a recognized keystone')
        # Creates a subclass instance.
        if instance is None:
            instance = value.create(name = name, **parameters)
        setattr(item, attribute, instance)
        return item         

    """ Private Methods """
    
    @classmethod
    def _get_name(
        cls, 
        item: Type[Keystone],
        name: Optional[str] = None) -> None:
        """Returns 'name' or str name of item.
        
        By default, the method uses camina.namify to create a snakecase name. If
        the resultant name begins with 'project_', that substring is removed. 

        If you want to use another naming convention, just subclass and override
        this method. All other methods will call this method for naming.
        
        Args:
            item (Type[Keystone]): item to name.
            name (Optional[str], optional): optional name to use. A 'project_'
                prefix will be removed, if it exists. Defaults to None.

        Returns:
            str: name of 'item' or 'name' (with the 'project' prefix removed).
            
        """
        name = name or camina.namify(item)
        if name.startswith('project_'):
            name = name[8:]
        return name        
            
         
@dataclasses.dataclass
class Keystone(abc.ABC):
    """Mixin for core package base classes."""

    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass in Keystones."""
        # Because Keystone will be used as a mixin, it is important to call 
        # other base class '__init_subclass__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs) # type: ignore
        if Keystone in cls.__bases__:
            Keystones.add(item = cls)
        else:
            Keystones.register(item = cls)
            
    """ Required Subclass Methods """
    
    @abc.abstractclassmethod
    def create(
        cls, 
        name: Optional[str] = None,
        **kwargs: Any) -> Keystone:
        """Returns a subclass instance based on passed arguments.

        The reason for requiring a 'create' classmethod is that it allows for
        classes to gather objects needed for the instance, but not to 
        necessarily maintain permanent links to other objects. This facilitates 
        loose coupling and easier serialization without complex interdependence.
        
        Args:
            name (Optional[str]): name or key to lookup a subclass.

        Returns:
            Keystone: subclass instance based on passed arguments.
            
        """
        pass 
