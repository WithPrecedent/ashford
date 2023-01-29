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
    KeystoneFactory (storage.Registry): base class for storing Keystone 
        subclasses and/or subclass instances.
    Keystones (object): stores base classes, defaults, and subclasses for
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

from . import base
from . import construction
from . import framework


FACTORIES: dict[Hashable, base.AbstractRegistry] = {
    'combined': construction.CombinedFactory,
    'instances': construction.InstanceFactory,
    'subclasses': construction.SubclassFactory}


@dataclasses.dataclass
class KeystoneFactory(abc.ABC):
    """Mixin for Keystone factories.
    
    This should be added as a mixin to a Factory class, depending upon what is
    to be stored.
    
    Args:

                          
    """
    name: Optional[Hashable] = None
    default: Optional[Any] = None

    """ Initialization Methods """
            
    def __post_init__(self) -> None:
        """Automatically initializes 'name' attribute."""
        with contextlib.suppress(AttributeError):
            super().__post_init__() 
        self._validate_name()    

    """ Instance Methods """
    
    def deposit(
        self, 
        item: object | Type[Any],
        name: Optional[Hashable] = None) -> None:
        """Adds 'item' to 'classes' and/or 'instances'.

        Args:
            item (object | Type[Any]): class or instance to add to the registry.
            name (Optional[Hashable]): key to use to store 'item'. If not
                passed, a key will be created using 'framework.namer'.
                Defaults to None
                
        """
        if abc.ABC not in item.__bases__:
            self.default = item
        super().deposit(item = item, name = name)
        self._validate_name()
        return

    """ Private Methods """
    
    def _validate_name(self) -> None:
        """Sets 'name' attribute if it is None."""
        if self.name is None:
            if self.contents:
                first_item = self.contents[list(self.contents.keys())[0]]
                self.name = framework.namer(first_item)
            elif self.default:
                self.name = framework.namer(self.default)
        return

    
@dataclasses.dataclass
class Keystones(camina.ChainDictionary):
    """Stores Keystone subclasses.
    
    For each Keystone, an attribute is added with the snakecase name of that 
    Keystone. In that attribute, a dict-like object (determined by
    'default_factory') is the value and it stores all Keystone subclasses of 
    that type (again using snakecase names as keys).
    
    If you want to use a different naming convention besides snakecase, you can 
    either:
        1) subclass and override the '_get_name' method to only change the
            naming convention for Keystones; or 
        2) or call 'ashford.set_namer' to set the naming function used 
            throughout ashford.
    
    Args:
        contents (MutableSequence[KeystoneFactory[Hashable, Any]]): list of 
            stored KeystoneFactory instances.
        default_factory (Optional[Any]): default value to return or default 
            callable to use to create the default value.
        return_first (Optional[bool]): whether to only return the first match
            found (True) or to search all of the stored Dictionary instances
            (False). Defaults to False.
                        
    Attributes:
        All direct Keystone subclasses will have an attribute name added
        dynamically.
        
    """
    contents: MutableSequence[KeystoneFactory[Hashable, Any]] = (
        dataclasses.field(default_factory = list))
    default_factory: Type[Any] = None
    return_first: Optional[bool] = False
    factory: Optional[KeystoneFactory | str] = 'combined'  

    """ Initialization Methods """
            
    def __post_init__(self) -> None:
        """Sets up factory."""
        with contextlib.suppress(AttributeError):
            super().__post_init__() 
        self._validate_factory()  
              
    """ Properties """
    
    @property
    def bases(self) -> dict[Hashable, Hashable]:
        """Returns dict of stored subclass names and their associated bases.

        Returns:
            dict[Hashable, Hashable]: keys are the stored subclass names and the
                values are the names of the base class which they are derived
                from.
            
        """        
        bases = {}
        for registry in self.contents:
            bases.update(dict.fromkeys(registry.keys(), registry.name))
        return bases
    
    @property
    def collections(self) -> dict[Hashable, KeystoneFactory]:
        """Returns dict of stored registries.

        Returns:
            dict[Hashable, KeystoneFactory]: keys are the 'name' attributes of
                each stored map and values are the stored maps.
            
        """        
        return {m.name: m for m in self.contents}
    
    @property
    def defaults(self) -> dict[Hashable, KeystoneFactory]:
        """Returns dict of defaults for each stored registry.

        Returns:
            dict[Hashable, KeystoneFactory]: keys are the 'name' attributes of
                each stored map and values are 'default' attribute.
            
        """        
        return {m.name: m.default for m in self.contents}
        
    @property
    def names(self) -> list[Hashable]:
        """Returns list of names of stored registries.

        Returns:
            list[Hashable]: names taken from 'name' attributes of the stored
                registries.
            
        """        
        return [m.name for m in self.contents]
                 
    """ Instance Methods """
    
    def add(self, item: Type[Keystone]) -> None:
        """Adds a new keystone attribute with an empty dictionary.

        Args:
            item (Type[Keystone]): direct Keystone subclass from which the name 
                of a new attribute should be derived.
            
        """
        try:
            base = self.classify(item = item)
            self._add_to_existing(item = item, base = base)
        except KeyError:
            self._add_new_base(item = item)
        return
    
    def classify(self, item: str | Type[Keystone] | Keystone) -> str:
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
        if not inspect.isclass(item) and not isinstance(item, str):
            testable = item.__class__
        else:
            testable = item
        for i, registry in enumerate(self.contents):
            if isinstance(testable, str):
                match = registry.get(testable, None)
                if match is not None:
                    return self.labels[i]
            else:
                for value in registry.values():
                    if issubclass(testable, value):
                        return self.labels[i]
        raise ValueError(f'{item} is not a subclass of any Keystone')
              
    def register(
        self, 
        item: Type[Keystone],
        name: Optional[str] = None) -> None:
        """Registers 'item' in the appropriate class attribute registry.
        
        Args:
            item (Type[Keystone]): Keystone subclass to register.
            name (Optional[str], optional): key name to use in storing 'item'. 
                Defaults to None.
            
        """
        try:
            base = self.classify(item = item)
            registry = getattr(self, base)
            self._add_to_existing(item = item, base = base)
        except ValueError:
            new_registry = self._create_registry()
            base = name or self._get_name(item = item, name = name)
            setattr(self, base, new_registry)(name = base)
        registry = getattr(self, base)
        name = name or self._get_name(item = item, name = name)
        registry.deposit(item = item, name = name)      
        return
              
    def set_default(
        self, 
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
        key = base or self.classify(item)
        name = self._get_name(item = item, name = name)
        getattr(self, name, )
        return
    
    def validate(
        self,
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
        base = self.bases[attribute]
        # Gets the relevant registry for 'attribute'.
        registry = getattr(self, attribute)
        # Adds parameters to 'value' is already an instance of the appropriate 
        # base type.
        if isinstance(value, base):
            for parameter, argument in parameters.items():
                setattr(value, parameter, argument)  
            instance = value
        # Selects default class for 'attribute' if none exists.
        elif value is None:
            name = self.defaults[attribute]
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
            name = framework.NAMER(value)
        else:
            raise ValueError(f'{value} is not a recognized keystone')
        # Creates a subclass instance.
        if instance is None:
            instance = value.create(name = name, **parameters)
        setattr(item, attribute, instance)
        return item         

    """ Private Methods """

    def _add_new_base(self, item: Keystone) -> None:
        name = self._get_name(item = item)
        self.labels.append(name)
        self.contents.append(self.default_factory())
        # Automatically sets self to the default option if it is concrete.
        if abc.ABC not in item.__bases__:
            self.set_default(item = item, base = name)
        return 
    
    def _add_to_existing(self, item: Keystone, base: Hashable) -> None:
        name = self._get_name(item = item)
        index = self.labels.index(base)
        registry = self.contents[index]
        registry.deposit(item = item, name = name)      
        return

    def _create_registry(self) -> KeystoneFactory:
        """Dynamically creates a KeystoneFactory subclass based on 'factory'.

        Returns:
            KeystoneFactory: made with the appropriate storage and factory
                based on the 'factory' attribute. 
              
        """
        factory = FACTORIES[self.factory]
        return dataclasses.dataclass([KeystoneFactory, factory])
    
    def _get_name(
        self, 
        item: Type[Keystone],
        name: Optional[str] = None) -> None:
        """Returns 'name' or str name of item.
        
        By default, the method uses framework.namer to create a snakecase name. 
        If the resultant name begins with any prefix listed in 
        defaults.REMOVABLE_PREFIXES, that substring is removed. 

        If you want to use another naming convention, just subclass and override
        this method. All other methods will call this method for naming.
        
        Args:
            item (Type[Keystone]): item to name.
            name (Optional[str], optional): optional name to use. A 'project_'
                prefix will be removed, if it exists. Defaults to None.

        Returns:
            str: name of 'item' or 'name' (with the 'project' prefix removed).
            
        """
        name = name or framework.NAMER(item)
        if name.startswith(framework.REMOVABLE_PREFIXES):
            for prefix in framework.REMOVABLE_PREFIXES:
                name.dropprefix(prefix)
        return name        

    """ Dunder Methods """
    
    def __getattr__(self, attribute: Hashable) -> KeystoneFactory:
        """Returns KeystoneFactory that has a 'name' matching 'attribute'.

        Args:
            item (Hashable): _description_

        Returns:
            KeystoneFactory: _description_
            
        """
        return self.collections[attribute]            
  
         
@dataclasses.dataclass
class Keystone(abc.ABC):
    """Mixin for core package base classes.
    
    Attributes:
        registry (ClassVar[Type[Keystones]]: registry where Keystone subclasses 
            are stored.
            
    """
    registry: ClassVar[Optional[Keystones]] = None

    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass in Keystones."""
        # Because Keystone will be used as a mixin, it is important to call 
        # other base class '__init_subclass__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs) 
        # Initializes or validates 'registry' class attribute, if necessary.
        cls._validate_registry()
        # If 'cls' is a direct subclass of Keystone, it is added as a new type
        # within 'registry'.
        if Keystone in cls.__bases__:
            cls.registry.add(item = cls)
        # If 'cls' is not a direct subclass of Keystone (meaning that Keystone
        # is not an immediate parent), then cls is registered in 'registry'.
        else:
            cls.registry.register(item = cls)
            
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

    """ Class Methods """
    
    @classmethod
    def set_registry(cls, registry: Keystones | Type[Keystones]) -> None:
        """Assigns 'registry' class attribute to 'registry' argument.
        
        Args:
            registry (registry: Keystones | Type[Keystones]): registry to store 
                Keystone subclasses and/or subclass instances.
            
        Raises:
            TypeError: if 'registry' is not a subclass or subclass instance of 
                Keystones.
            
        """
        if issubclass(registry, Keystones):
            cls.registry = registry()
        elif isinstance(registry, Keystones):
            cls.registry = registry
        else:
            raise TypeError(
                'registry must be a subclass or subclass instance of Keystones')
        return
    
    """ Private Methods """
    
    @classmethod
    def _validate_registry(cls) -> None:
        """Sets 'registry' to default or instances it, if necessary.

        Raises:
            TypeError: if 'registry' is not a subclass or subclass instance of 
                Keystones.
        
        """
        if cls.registry is None:
            cls.set_registry(registry = Keystones)
        elif issubclass(cls.registry, Keystones):
            cls.registry = cls.registry()
        elif not isinstance(cls.registry, Keystones):
            raise TypeError(
                'registry must be a subclass or subclass instance of Keystones')            
        return
    