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
from . import construction
from . import registration
from . import validation


@dataclasses.dataclass
class Library(registration.Anthology):
    """Mixin for Keystone registries.
    
    This should be added as a mixin to a Anthology class, depending upon what is
    to be stored.
    
    Args:
        contents (MutableMapping[Hashable, Any]): stored dictionary. Defaults 
            to an empty Anthology instance.
        default_factory (Optional[Any]): default value to return or default 
            callable to use to create the default value. Defaults to None.
        name (Optional[Hashable]): name of Library, which is used by Librarian
            to access the Library instance. Defaults to None.
                                     
    """
    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = registration.Anthology)
    default_factory: Optional[Any] = None
    name: Optional[Hashable] = dataclasses.field(default = camina.Name())

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
        """Adds 'item' to 'contents'.

        Args:
            item (object | Type[Any]): class or instance to add to 'contents'.
            name (Optional[Hashable]): key to use to store 'item'. If not
                passed, a key will be created using 'configuration.KEYER'.
                Defaults to None.
                
        """
        self.contents[name] = item
        if not inspect.isabstract(item) and self.default_factory is None:
            self.default_factory = self.contents[name]
        self._validate_name()
        return

    """ Private Methods """
    
    def _validate_name(self) -> None:
        """Sets 'name' attribute if it is None."""
        if self.name is None:
            if self.contents:
                first_item = self.contents[list(self.contents.keys())[0]]
                self.name = configuration.KEYER(first_item)
            elif self.default_factory:
                self.name = configuration.KEYER(self.default)
        return

  
@dataclasses.dataclass
class Librarian(registration.Anthology, camina.ChainDictionary, abc.ABC):
    """Stores Keystone subclasses and/or instances.
    
    For each Keystone, an attribute is added with the snakecase name of that 
    Keystone. In that attribute, a dict-like object (determined by
    'default_factory') is the value and it stores all Keystone subclasses of 
    that type (again using snakecase names as keys).
    
    If you want to use a different naming convention besides snakecase, you can 
    either:
        1) subclass and override the '_get_name' method to only change the
            naming convention for Librarian; or 
        2) or call 'ashford.set_keyer' to set the naming function used 
            throughout ashford.
    
    Args:
        contents (MutableSequence[Library[Hashable, Any]]): list of 
            stored Library instances.
        default_factory (Optional[Any]): default value to return or default 
            callable to use to create the default value.
        return_first (Optional[bool]): whether to only return the first match
            found (True) or to search all of the stored Dictionary instances
            (False). Defaults to False.
                        
    Attributes:
        All direct Keystone subclasses will have an attribute name added
        dynamically.
        
    """
    contents: MutableSequence[Library] = (
        dataclasses.field(default_factory = list))
    default_factory: Type[Any] = None
    return_first: Optional[bool] = False
    storage: ClassVar[Type[Library]] = Library
                     
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
            bases |= dict.fromkeys(registry.keys(), registry.name)
        return bases
  
    @property
    def defaults(self) -> dict[Hashable, Library]:
        """Returns dict of defaults for each stored registry.

        Returns:
            dict[Hashable, Library]: keys are the 'name' attributes of
                each stored map and values are 'default' attribute.
            
        """        
        return {m.name: m.default_factory for m in self.contents}
    
    @property
    def libraries(self) -> dict[Hashable, Library]:
        """Returns dict of stored registries.

        Returns:
            dict[Hashable, Library]: keys are the 'name' attributes of
                each stored map and values are the stored maps.
            
        """        
        return {m.name: m for m in self.contents}
          
    @property
    def names(self) -> list[Hashable]:
        """Returns list of names of stored registries.

        Returns:
            list[Hashable]: names taken from 'name' attributes of the stored
                registries.
            
        """        
        return [m.name for m in self.contents]
                 
    """ Instance Methods """
    
    def add_library(self, name: Hashable) -> None:
        """Adds a new Library instance to 'contents'.

        Args:
            name (Hashable): name of Library, which will be passed to the new
                Library instance.

        """
        self.contents.append(self.storage(name = name))
        return   
        
    def classify(self, item: str | Type[Any] | object) -> str:
        """Returns the str name of the object of which 'item' is.

        Args:
            item (str | Type[Any] | object): object, class, or str name of an
                object or class.

        Raises:
            ValueError: if 'item' does not match a subclass of any recognized 
                type.
            
        Returns:
            str: snakecase str name of the base type of which 'item' is a 
                subclass or subclass instance.
                
        """
        if not inspect.isclass(item) and not isinstance(item, str):
            testable = item.__class__
        else:
            testable = item
        for name, library in self.libraries.items():
            if isinstance(testable, str):
                match = library.get(testable, None)
                if match is not None:
                    return name
            else:
                for value in library.values():
                    if issubclass(testable, value):
                        return name
        raise ValueError(f'{item} is not a subclass of any recognized type')
        
    def deposit(
        self, 
        item: object | Type[Any], 
        name: Optional[Hashable] = None) -> None:
        """Adds 'item' to 'contents'.

        Args:
            item (object | Type[Any]): item to add to the registry.
            name (Optional[Hashable]): key to use to store 'item'. If not
                passed, a key will be created using '_get_name'. Defaults to 
                None.
                
        """
        try:
            base = self.classify(item = item)
            self._deposit_to_existing(item = item, name = name, base = base)
        except ValueError:
            self._desposit_to_new(item = item, name = name)
        return
    
    # def validate(
    #     self,
    #     item: object,
    #     attribute: str,
    #     parameters: Optional[MutableMapping[Hashable, Any]] = None) -> object:
    #     """Creates or validates 'attribute' in 'item'.

    #     Args:
    #         item (object): object (often a Project or Manager instance) of which
    #             a Keystone in 'attribute' needs to be validated or 
    #             created. 
    #         attribute (str): name of the attribute' in item containing a value
    #             to be validated or which provides information to create an
    #             appropriate instance.
    #         parameters (Optional[MutableMapping[Hashable, Any]]): parameters to pass
    #             to or inject in the Keystone subclass instance.

    #     Raises:
    #         ValueError: if the value of 'attribute' in 'item' does match any
    #             known subclass or subclass instance of that Keystone
    #             subtype.

    #     Returns:
    #         object: completed, linked instance.
            
    #     """    
    #     parameters = parameters or {}   
    #     instance = None
    #     # Get current value of 'attribute' in 'item'.
    #     value = getattr(item, attribute)
    #     # Get the corresponding base class.
    #     base = self.bases[attribute]
    #     # Gets the relevant registry for 'attribute'.
    #     registry = getattr(self, attribute)
    #     # Adds parameters to 'value' is already an instance of the appropriate 
    #     # base type.
    #     if isinstance(value, base):
    #         for parameter, argument in parameters.items():
    #             setattr(value, parameter, argument)  
    #         instance = value
    #     # Selects default class for 'attribute' if none exists.
    #     elif value is None:
    #         name = self.defaults[attribute]
    #         if name:
    #             value = registry[name]
    #         else:
    #             raise ValueError(
    #                 f'Neither a value for {attribute} nor a default class '
    #                 f'exists')
    #     # Uses str value to select appropriate subclass.
    #     elif isinstance(value, str):
    #         name = getattr(item, attribute)
    #         value = registry[name]
    #     # Gets name of class if it is already an appropriate subclass.
    #     elif inspect.issubclass(value, base):
    #         name = configuration.KEYER(value)
    #     else:
    #         raise ValueError(f'{value} is not a recognized keystone')
    #     # Creates a subclass instance.
    #     if instance is None:
    #         instance = value.create(name = name, **parameters)
    #     setattr(item, attribute, instance)
    #     return item 
    
    """ Private Methods """
        
    def _deposit_to_existing(
        self, 
        item: object | Type[Any], 
        name: Optional[Hashable], 
        base: Hashable) -> None:
        """Adds 'item' to an existing Library in 'contents'.

        Args:
            item (object | Type[Any]): item to add to the registry.
            name (Optional[Hashable]): key to use to store 'item'. If not
                passed, a key will be created using '_get_name'.
            base (Hashable): name of the Library to add 'item' to.
                
        """        
        name = self._get_name(item = item, name = name)
        library = self.libraries[base]
        library.deposit(item = item, name = name)      
        return
    
    def _desposit_to_new(
        self, 
        item: object | Type[Any], 
        name: Optional[Hashable]) -> None:
        """Adds 'item' to a new Library in 'contents'.

        Args:
            item (object | Type[Any]): item to add to the registry.
            name (Optional[Hashable]): key to use to store 'item'. If not
                passed, a key will be created using '_get_name'.
                
        """        
        name = self._get_name(item = item, name = name)
        self.add_library(name = name)
        self.libraries[name][name] = item
        return 
    
    def _get_name(
        self, 
        item: Type[Any],
        name: Optional[str] = None) -> None:
        """Returns 'name' or str name of item.
        
        By default, the method uses configuration.KEYER to create a snakecase name. 
        If the resultant name begins with any prefix listed in 
        defaults.REMOVABLE_PREFIXES, that substring is removed. 

        If you want to use another naming convention, just subclass and override
        this method. All other methods will call this method for naming.
        
        Args:
            item (Type[Any]): item to name.
            name (Optional[str], optional): optional name to use. A 'project_'
                prefix will be removed, if it exists. Defaults to None.

        Returns:
            str: name of 'item' or 'name' (with the 'project' prefix removed).
            
        """
        name = name or configuration.KEYER(item)
        if name.startswith(tuple(configuration.REMOVABLE_PREFIXES)):
            for prefix in configuration.REMOVABLE_PREFIXES:
                name.dropprefix(prefix)
        return name   
     
    # """ Dunder Methods """
    
    # def __getattr__(self, attribute: Hashable) -> Library:
    #     """Returns Library that has a 'name' matching 'attribute'.

    #     Args:
    #         attribute (Hashable): name of attribute sought.

    #     Returns:
    #         Library: a Library instance stored in 'contents'.
            
    #     """
    #     return self.libraries[attribute]            

     
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
    Keystone, registration.Curator, construction.AnthologyFactory, abc.ABC):
    """Mixin for core package base classes.
    
    Attributes:
        registry (ClassVar[Librarian]): stores subclasses and instances. 
            Defaults to an empty CorpusLibrarian.
            
    """
    registry: ClassVar[Librarian] = Librarian()
  
         
@dataclasses.dataclass
class InstancerKeystone(
    Keystone, registration.Instancer, construction.AnthologyFactory, abc.ABC):
    """Mixin for core package base classes.
    
    Attributes:
        registry (ClassVar[Librarian]): stores subclass instances. Defaults to 
            an empty AnthologyLibrarian.
            
    """
    registry: ClassVar[Librarian] = Librarian()
     
  
@dataclasses.dataclass
class SubclasserKeystone(
    Keystone, registration.Subclasser, construction.AnthologyFactory, abc.ABC):
    """Mixin for core package base classes.
    
    Attributes:
        registry (ClassVar[Librarian]): stores subclasses. Defaults to 
            an empty AnthologyLibrarian.
            
    """
    registry: ClassVar[Librarian] = Librarian()
     