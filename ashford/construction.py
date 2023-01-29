"""
construction: easy-to-use factory mixins
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
    CombinedFactory (abc.ABC): base class for ashford factory mixins. It 
        requires subclasses have a 'create' classmethod.
    InstanceFactory (base.AbstractFactory): mixin that stores all subclass 
        instances in the 'instances' class attribute and returns stored 
        instances when the 'create' classmethod is called.
    LibraryFactory (base.AbstractFactory): mixin that stores all subclasses and 
        subclass instances in the 'library' class attribute and returns stored 
        subclasses and/or instances when the 'create' classmethod is called.
    SourceFactory (base.AbstractFactory): mixin that calls the appropriate creation 
        method based on the type of passed first argument to 'create' and the
        types stored in the keys of the 'sources' class attribute.
    StealthFactory (base.AbstractFactory): mixin that returns stored subclasses when the 
        'create' classmethod is called without having a 'subclasses' class 
        attribute like SubclassFactory.
    SubclassFactory (base.AbstractFactory): mixin that stores all subclasses in the 
        'subclasses' class attribute and returns stored subclasses when the 
        'create' classmethod is called.
    TypeFactory (base.AbstractFactory): mixin that calls the appropriate creation 
        method based on the type of passed first argument to 'create' and the
        snakecase name of the type. This factory is prone to significant 
        key errors unless you are sure of the snakecase names of all possible 
        submitted type names. SourceFactory avoids this problem by allowing you
        to declare corresponding types and string names.
            
ToDo:

"""

from __future__ import annotations
import abc
from collections.abc import Hashable, Mapping, MutableMapping, MutableSequence
import copy
import dataclasses
import inspect
from typing import Any, ClassVar, Optional, Type, Union

from . import base
from . import framework
from . import registration


""" Factories with Registries """    
 
@dataclasses.dataclass
class RegistrarFactory(base.AbstractFactory):
    """Mixin supporting creation of subclasses and/or instances."""
        
    """ Class Methods """

    @classmethod
    def create(
        cls, 
        source: str, 
        parameters: Optional[MutableMapping[Hashable, Any]] = None) -> (
            RegistrarFactory):
        """Creates a subclass or instance based on 'source' and 'parameters'.
        
        Args:
            source (str): key for item stored in 'registry'.
            parameters: Optional[MutableMapping[Hashable, Any]]: keyword 
                arguments to add to a created instance. If left as None, a copy
                of a stored instance is returned. If passed, 'parameters' will
                be injected as attributes on the copied instance. Defaults to 
                None.
            
        Returns:
            RegistrarFactory: a RegistrarFactory subclass instance created based 
                on 'source' and any passed arguments.
                
        """
        return cls.registry.withdraw(item = source, parameters = parameters)
        
  
@dataclasses.dataclass
class InstanceFactory(registration.InstanceRegistrar, base.AbstractFactory):
    """Mixin which automatically registers and creates subclass instances.
    
    Attributes:
        registry (ClassVar[InstanceRegistry[str, object]]): stores subclass
            instances. Defaults to an instance of InstanceRegistry.
            
    """
    registry: ClassVar[registration.InstanceRegistry[str, object]] = (
        registration.InstanceRegistry())
        
    """ Class Methods """

    @classmethod
    def create(
        cls, 
        source: str, 
        parameters: Optional[MutableMapping[Hashable, Any]] = None) -> (
            InstanceFactory):
        """Creates a subclass or instance based on 'source' and 'parameters'.
        
        Args:
            source (str): key for item stored in 'registry'.
            parameters: Optional[MutableMapping[Hashable, Any]]: keyword 
                arguments to add to a created instance. If left as None, a copy
                of a stored instance is returned. If passed, 'parameters' will
                be injected as attributes on the copied instance. Defaults to 
                None.
            
        Returns:
            InstanceFactory: an InstanceFactory subclass instance created based 
                on 'source' and any passed arguments.
                
        """
        instance = copy.deepcopy(cls.registry.withdraw(item = source))
        return cls._finalize_product(item = instance, parameters = parameters) 
        

@dataclasses.dataclass
class SubclassFactory(registration.SubclassRegistrar, base.AbstractFactory):
    """Mixin which automatically registers and stores subclasses.
    
    Attributes:
        registry (ClassVar[registration.SubclassRegistry[str, Type[Any]]]): 
            stores subclasses. Defaults to an instance of SubclassRegistry.
            
    """
    registry: ClassVar[registration.SubclassRegistry[str, Type[Any]]] = (
        registration.SubclassRegistry())
        
    """ Class Methods """

    @classmethod
    def create(
        cls, 
        source: str, 
        parameters: Optional[MutableMapping[Hashable, Any]] = None) -> (
            Type[SubclassFactory] | SubclassFactory):
        """Creates a subclass or instance based on 'source' and 'parameters'.
        
        Args:
            source (str): key for item stored in 'registry'.
            parameters: Optional[MutableMapping[Hashable, Any]]: keyword 
                arguments to pass to a newly created instance. If left as None,
                a subclass is returned. If passed (pass an empty dict if no
                parameters are needed), an instance, instead of a subclass is
                returned. Defaults to None.
                
        Returns:
            Type[SubclassFactory] | SubclassFactory: a subclass or subclass
                instance, depending upon whether 'parameters' are passed.
                
        """
        subclass = copy.deepcopy(cls.registry.withdraw(item = source))
        return cls._finalize_product(item = subclass, parameters = parameters)
                            
  
@dataclasses.dataclass
class CombinedFactory(registration.CombinedRegistrar, base.AbstractFactory):
    """Mixin which automatically registers and stores subclasses and instances.
    
    Attributes:
        registry (ClassVar[registration.CombinedRegistry[str, object | 
            Type[Any]]]): stores subclasses and instances. Defaults to an 
            instance of CombinedRegistry.
            
    """
    registry: ClassVar[registration.CombinedRegistry[
        str, Union[object, Type[Any]]]] = registration.CombinedRegistry()
    
    """ Class Methods """

    @classmethod
    def create(
        cls, 
        source: str, 
        parameters: Optional[MutableMapping[Hashable, Any]] = None) -> (
            CombinedFactory):
        """Creates an instance based on 'source' and 'parameters'.
        
        Args:
            source (str): key for item stored in 'registry'.
            parameters: Optional[MutableMapping[Hashable, Any]]: keyword 
                arguments to pass to a newly created instance. If passed, they 
                will either be passed as arguments, or, if the stored item is
                already an instance, added as attributes. Defaults to None.
                
        Returns:
            CombinedFactory: a subclass instance.
                
        """
        item = copy.deepcopy(cls.registry.withdraw(item = source))
        product = cls._finalize_product(item = item, parameters = parameters)
        if inspect.isclass(product):
            return product()
        else:
            return product
          

""" Factories without Registries """
               
@dataclasses.dataclass
class SourceFactory(base.AbstractFactory, abc.ABC):
    """Mixin that returns subclasses using 'sources' class attribute.

    Unlike the above factories, this one does not require an additional class 
    attribute to be added to store registered subclasses. Instead, it requires
    subclasses to add creation methods using a common naming format.
    
    This factory acts as a dispatcher to call other methods based on the type
    passed. Unlike TypeFactory, SourceFactory is more forgiving by allowing the
    type passed to a subtype of the type listed as a key in the 'sources' class
    attribute.
    
    Attributes:
        sources (ClassVar[Mapping[Type, str]]): keys are types of the data 
            sources for object creation. Values are the corresponding str name 
            of the type which should have a class method called 
            'from_{str name of type}' (or a different naming convention if 
            'framework.METHOD_NAMER' is changed). Because the 'create' method 
            will call the first method for which 'source' matches a key, you 
            should put specific types before general types in 'sources'.
    
    """
    sources: ClassVar[Mapping[Type, str]] = {}
    
    """ Class Methods """

    @classmethod
    def create(
        cls, 
        source: Any, 
        parameters: Optional[MutableMapping[Hashable, Any]] = None) -> (
            SourceFactory):
        """Creates an instance based on 'source' and 'parameters'.
        
        Args:
            source (Any): source to determine type to call the appropriate
                construction method.
            parameters: Optional[MutableMapping[Hashable, Any]]: keyword 
                arguments to pass to a newly created instance. If passed, they 
                will either be passed as arguments, or, if the stored item is
                already an instance, added as attributes. Defaults to None.
                
        Returns:
            SourceFactory: an instance.
                
        """
        parameters = parameters or {}
        for kind, suffix in cls.sources.items():
            if isinstance(source, kind):
                method_name = framework.METHOD_NAMER(item = suffix)
                try:
                    method = getattr(cls, method_name)
                except AttributeError:
                    raise AttributeError(f'{method_name} does not exist')
                return method(source, **parameters)
        raise KeyError(
            f'source does not match any recognized types')
      

@dataclasses.dataclass
class StealthFactory(base.AbstractFactory):
    """Mixin that returns a subclass without requiring a storage attribute.
    
    Unlike the other factories, this one does not require any attributes. 
    Instead, it relies on pre-existing data and lazily adds keys to create 
    a dict facade.
    
    This factory uses the subclasses stored in '__subclasses__' dunder attribute
    that is automatically created with every class. It creates a dict on the fly
    with key names being snakecase of the stored subclasses '__name__' 
    attributes.
    
    """
        
    """ Class Methods """

    @classmethod
    def create(
        cls, 
        source: str, 
        parameters: Optional[MutableMapping[Hashable, Any]] = None) -> (
            StealthFactory | Type[StealthFactory]):
        """Returns a subclass or instance based on 'source' and 'parameters.
        
        A subclass in the '__subclasses__' attribute is selected based on the
        naming convention in 'ashford.NAMER'.
        
        Args:
            source (str): name corresponding to a subclass stored in the
                '__subclasses__' attribute.
            parameters: Optional[MutableMapping[Hashable, Any]]: keyword 
                arguments to pass to a newly created instance. If left as None,
                a subclass is returned. If passed (pass an empty dict if no
                parameters are needed), an instance, instead of a subclass is
                returned. Defaults to None.
                       
        Raises:
            KeyError: If a corresponding subclass does not exist for 'source.'

        Returns:
            StealthFactory | Type[StealthFactory]: a class or instance,
                depending if 'parameters' are passed.
            
        """
        options = {
            framework.NAMER(s.__name__): s for s in cls.__subclasses__}
        try:
            item = options[source]
        except KeyError:
            raise KeyError(f'No subclass {source} was found')
        return cls._finalize_product(item = item, parameters = parameters)

                           
@dataclasses.dataclass
class TypeFactory(base.AbstractFactory, abc.ABC):
    """Mixin that returns subclass using the type or str name of the type.

    Unlike other factories, this one does not require an additional class 
    attribute to be added to store registered subclasses. Instead, it requires
    subclasses to add creation methods using a common naming format.
       
    This factory acts as a dispatcher to call other methods based on the type
    or name of the type passed. By default, using the '_get_create_method_name'
    method, the format for such methods should be 'from_{str name of type}'.
    
    """
    
    """ Class Methods """

    @classmethod
    def create(
        cls, 
        source: str, 
        parameters: Optional[MutableMapping[Hashable, Any]] = None) -> (
            TypeFactory | Type[TypeFactory]):
        """Returns a subclass or instance based on 'source' and 'parameters.
        
        For create to work properly, there should be a corresponding classmethod
        named f'from_{snake-case str name of type}'. If you would prefer a 
        different naming format, you can subclass TypeFactory and override the 
        '_get_create_method_name' classmethod.

        Raises:
            AttributeError: If an appropriate method does not exist for the
                data type of 'source.'

        Returns:
            TypeFactory: instance of a TypeFactory.
            
        """
        parameters = parameters or {}
        suffix = framework.NAMER(type(source))
        method_name = framework.METHOD_NAMER(item = suffix)
        try:
            method = getattr(cls, method_name)
        except AttributeError:
            raise AttributeError(f'{method_name} does not exist')
        return method(source, **parameters)
