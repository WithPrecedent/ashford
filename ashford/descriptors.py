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
    Factory (abc.ABC): base class for all factories. A 'create' class 
        method is required for subclasses.
    Registrar (abc.ABC): base class for all classes that automatically 
        register subclasses and/or instances. A 'register' class method is 
        provided for the default registration method.
    Registry (abc.ABC): base class for storing registered subclasses 
        and/or instances. 'deposit' and 'withdraw' methods are required for 
        subclasses. 
    Validator (abc.ABC): base class for descriptors that validate stored
        items of a class instance. A 'validate' method must be provided by
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
class Descriptor(abc.ABC):
    """Base class for ashford descriptors.
    
    Attributes:
        attribute_name (str): name of the validator attribute in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
            This attribute contains the name of an attribute in 'owner' (and not 
            the descriptor) where the data for a descriptor will be stored.
        owner (object): object of which this validator is an attribute.
            
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
class Getter(Descriptor):
    """Base class for an attribute non-data descriptor.

    The core code of this class is adapted from the official Python HOWTOs:
    https://docs.python.org/3/howto/descriptor.html
    
    Unlike the class in the Python docs, this one stores additional attributes
    for use by subclasses that do more than very basic type validation. It 
    also can store a default value or default callable if there is no stored
    value.
    
    Attributes:
        attribute_name (str): name of the validator attribute in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
        owner (object): object of which this validator is an attribute.
            
    """
        
    """ Dunder Methods """

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
        return getattr(owner, self.private_name)     
    
    def __set_name__(self, owner: object, name: str) -> None:
        """Stores 'owner' object as 'owner' attribute.

        Args:
            owner (object): object of which this validator is an attribute.
            name (str): name of this attribute in 'owner'. 
            
        """
        self.attribute_name = name
        self.private_name = f'_{name}'
        self.owner = owner
        return


@dataclasses.dataclass
class Setter(abc.ABC):
    """Base class for an attribute data descriptor.

    The core code of this class is adapted from the official Python HOWTOs:
    https://docs.python.org/3/howto/descriptor.html
    
    Unlike the class in the Python docs, this one stores additional attributes
    for use by subclasses that do more than very basic type validation. It 
    also can store a default value or default callable if there is no stored
    value.
    
    Attributes:
        attribute_name (str): name of the validator attribute in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
        owner (object): object of which this validator is an attribute.
            
    """
 
    """ Dunder Methods """

    def __set__(self, owner: object, value: Any) -> None:
        """Stores 'value' in 'private_name' of 'owner'.

        Args:
            owner (object): object of which this validator is an attribute.
            value (Any): item to store, after being validated.
            
        """
        validated = self.validate(item = value, parent = owner)
        setattr(owner, self.private_name, validated)
        return    
    
    def __set_name__(self, owner: object, name: str) -> None:
        """Stores 'owner' object as 'owner' attribute.

        Args:
            owner (object): object of which this validator is an attribute.
            name (str): name of this attribute in 'owner'. 
            
        """
        self.attribute_name = name
        self.private_name = f'_{name}'
        self.owner = owner
        return
    
    
@dataclasses.dataclass
class Validator(abc.ABC):
    """Base class for a validator descriptor.

    The core code of this class is adapted from the official Python HOWTOs:
    https://docs.python.org/3/howto/descriptor.html
    
    Unlike the class in the Python docs, this one stores additional attributes
    for use by subclasses that do more than very basic type validation. It 
    also can store a default value or default callable if there is no stored
    value.
    
    Attributes:
        attribute_name (str): name of the validator attribute in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
        owner (object): object of which this validator is an attribute.
            
    """
    
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
        
    """ Dunder Methods """

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
        return getattr(owner, self.private_name)  

    def __set__(self, owner: object, value: Any) -> None:
        """Stores 'value' in 'private_name' of 'owner'.

        Args:
            owner (object): object of which this validator is an attribute.
            value (Any): item to store, after being validated.
            
        """
        validated = self.validate(item = value, parent = owner)
        setattr(owner, self.private_name, validated)
        return    
    
    def __set_name__(self, owner: object, name: str) -> None:
        """Stores 'owner' object as 'owner' attribute.

        Args:
            owner (object): object of which this validator is an attribute.
            name (str): name of this attribute in 'owner'. 
            
        """
        self.attribute_name = name
        self.private_name = f'_{name}'
        self.owner = owner
        return
