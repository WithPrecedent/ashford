"""
validation: validation mixins and decorators
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
    bonafide
    
ToDo:
    Create validation decorators (using the commented out code as the template)
        decorators)
    
"""
from __future__ import annotations
import abc
from collections.abc import Hashable, MutableMapping
import dataclasses
import functools
import numbers
from typing import Any, Callable, Optional, Type

import camina

from . import base
from . import configuration


""" Base Validators """

@dataclasses.dataclass
class TypeValidator(base.Validator):
    """Base class for a type validator descriptor.
    
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
class ValueValidator(base.Validator):
    """Base class for a type validator descriptor.
    
    Attributes:
        attribute_name (str): name of the validator attribute in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
        owner (object): object of which this validator is an attribute.
            
    """
    pass    

      
""" Type Validators """

@dataclasses.dataclass
class BonafideDict(TypeValidator):
    """Validates or converts stored data as a dict type.
    
    Attributes:
        attribute_name (str): name of the validator attribute in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
        owner (object): object of which this validator is an attribute.
            
    """

    """ Instance Methods """

    def validate(self, item: Any) -> Any:
        """Validates 'item' or creates a new instance.

        Args:
            item (Any): object to validate.

        Returns:
            Any: validated object.
            
        """   
        return camina.dictify(item)   
           

@dataclasses.dataclass
class BonafideFloat(TypeValidator):
    """Validates or converts stored data as a float type.
    
    Attributes:
        attribute_name (str): name of the validator attribute in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
        owner (object): object of which this validator is an attribute.
            
    """

    """ Instance Methods """

    def validate(self, item: Any) -> Any:
        """Validates 'item' or creates a new instance.

        Args:
            item (Any): object to validate.

        Returns:
            Any: validated object.
            
        """   
        return camina.to_float(item)    
        

@dataclasses.dataclass
class BonafideInteger(TypeValidator):
    """Validates or converts stored data as a int type.
    
    Attributes:
        attribute_name (str): name of the validator attribute in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
        owner (object): object of which this validator is an attribute.
            
    """

    """ Instance Methods """

    def validate(self, item: Any) -> Any:
        """Validates 'item' or creates a new instance.

        Args:
            item (Any): object to validate.

        Returns:
            Any: validated object.
            
        """   
        return camina.to_int(item)   
         

@dataclasses.dataclass
class BonafideIterable(TypeValidator):
    """Validates or converts stored data as an iterable.
    
    Attributes:
        attribute_name (str): name of the validator attribute in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
        owner (object): object of which this validator is an attribute.
            
    """

    """ Instance Methods """

    def validate(self, item: Any) -> Any:
        """Validates 'item' or creates a new instance.

        Args:
            item (Any): object to validate.

        Returns:
            Any: validated object.
            
        """   
        return camina.iterify(item) 

    
@dataclasses.dataclass
class BonafideList(TypeValidator):
    """Validates or converts stored data as a list type.
    
    Attributes:
        attribute_name (str): name of the validator attribute in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
        owner (object): object of which this validator is an attribute.
            
    """

    """ Instance Methods """

    def validate(self, item: Any) -> Any:
        """Validates 'item' or creates a new instance.

        Args:
            item (Any): object to validate.

        Returns:
            Any: validated object.
            
        """   
        return camina.listify(item)   
          

@dataclasses.dataclass
class BonafideNumber(TypeValidator):
    """Validates or converts stored data as a numerical type.
    
    Attributes:
        attribute_name (str): name of the validator attribute in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
        owner (object): object of which this validator is an attribute.
            
    """

    """ Instance Methods """

    def validate(self, item: Any) -> Any:
        """Validates 'item' or creates a new instance.

        Args:
            item (Any): object to validate.

        Returns:
            Any: validated object.
            
        """   
        return camina.numify(item)   
                    

@dataclasses.dataclass
class BonafidePath(TypeValidator):
    """Validates or converts stored data as a pathlib.Path type.
    
    Attributes:
        attribute_name (str): name of the validator attribute in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
        owner (object): object of which this validator is an attribute.
            
    """

    """ Instance Methods """

    def validate(self, item: Any) -> Any:
        """Validates 'item' or creates a new instance.

        Args:
            item (Any): object to validate.

        Returns:
            Any: validated object.
            
        """   
        return camina.pathlibify(item)          
         

@dataclasses.dataclass
class BonafideString(TypeValidator):
    """Validates or converts stored data as a str type.
    
    Attributes:
        attribute_name (str): name of the validator attribute in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
        owner (object): object of which this validator is an attribute.
            
    """

    """ Instance Methods """

    def validate(self, item: Any) -> Any:
        """Validates 'item' or creates a new instance.

        Args:
            item (Any): object to validate.

        Returns:
            Any: validated object.
            
        """   
        return camina.to_str(item)   
        

@dataclasses.dataclass
class BonafideTuple(TypeValidator):
    """Validates or converts stored data as a tuple type.
    
    Attributes:
        attribute_name (str): name of the validator attribute in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
        owner (object): object of which this validator is an attribute.
            
    """

    """ Instance Methods """

    def validate(self, item: Any) -> Any:
        """Validates 'item' or creates a new instance.

        Args:
            item (Any): object to validate.

        Returns:
            Any: validated object.
            
        """   
        return camina.tuplify(item)   
  

""" Value Validators """

@dataclasses.dataclass
class BonafideMaximum(ValueValidator):
    """Validates a number as less than or equal to a maximum.

    Args:
        maximum (numbers.Number): number which the stored value must be equal to
             or less than.
        allow_equal (Optional[bool]): whether to allow a value to be equivalent
            to 'maximum'. Defaults to True.
                        
    Attributes:
        attribute_name (str): name of the validator attribute in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
        owner (object): object of which this validator is an attribute.
            
    """
    maximum: numbers.Number
    allow_equal: Optional[bool] = True
        
    """ Instance Methods """

    def validate(
        self, 
        item: numbers.Number, 
        raise_error: Optional[bool] = True) -> numbers.Number:
        """Validates value of 'item'.

        Args:
            item (numbers.Number): object to validate.
            raise_error (Optional[bool]): whether to raise an error if the value
                meets the criteria or return the 'maxinum'. Defaults to True.
                        
        Raises:
            ValueError: if item is greater than 'maximum' and  'raise_error' is
                True.

        Returns:
            Any: validated object or 'maximum' if 'raise_error' is False.
            
        """
        if self.allow_equal:
            if item <= self.maximum:
                return item
            elif raise_error:
                raise ValueError(
                    f'item must be less than or equal to {self.maximum}')
            else:
                return self.maximum
        else:
            if item < self.maximum:
                return item
            elif raise_error:
                raise ValueError(f'item must be less than {self.maximum}')
            else:
                return self.maximum
        

@dataclasses.dataclass
class BonafideMinimum(ValueValidator):
    """Validates a number as greater than or equal to a minimum.

    Args:
        minimum (numbers.Number): number which the stored value must be equal to
             or greater than.
        allow_equal (Optional[bool]): whether to allow a value to be equivalent
            to 'minimum'. Defaults to True.
             
    Attributes:
        attribute_name (str): name of the validator attribute in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
        owner (object): object of which this validator is an attribute.
            
    """
    minimum: numbers.Number
    allow_equal: Optional[bool] = True
        
    """ Instance Methods """

    def validate(
        self, 
        item: numbers.Number, 
        raise_error: Optional[bool] = True) -> numbers.Number:
        """Validates value of 'item'.

        Args:
            item (numbers.Number): object to validate.
            raise_error (Optional[bool]): whether to raise an error if the value
                meets the criteria or return the 'miminum'. Defaults to True.
            
        Raises:
            ValueError: if item is less than 'minimum' and 'raise_error' is
                True.

        Returns:
            Any: validated object or 'minimum' if 'raise_error' is False.
            
        """
        if self.allow_equal:
            if item >= self.minimum:
                return item
            elif raise_error:
                raise ValueError(
                    f'item must be greater than or equal to {self.minimum}')
            else:
                return self.minimum
        else:
            if item > self.minimum:
                return item
            elif raise_error:
                raise ValueError(f'item must be greater than {self.minimum}')
            else:
                return self.minimum
            
            
@dataclasses.dataclass
class BonafideRange(ValueValidator):
    """Validates a number as between a minimum and maximum value.

    Args:
        maximum (numbers.Number): number which the stored value must be equal to
             or less than.
        minimum (numbers.Number): number which the stored value must be equal to
             or greater than.
        allow_equal (Optional[bool]): whether to allow a value to be equivalent
            to 'minimum'. Defaults to True.
             
    Attributes:
        attribute_name (str): name of the validator attribute in 'owner'. 
        private_name (str): 'attribute_name' with a leading underscore added.
        owner (object): object of which this validator is an attribute.
            
    """
    maximum: numbers.Number
    minimum: numbers.Number
    allow_equal: Optional[bool] = True
        
    """ Instance Methods """

    def validate(self, item: numbers.Number) -> numbers.Number:
        """Validates value of 'item'.

        Args:
            item (numbers.Number): object to validate.
            
        Raises:
            ValueError: if item is less than 'minimum' or greater than 
                'maximum'.

        Returns:
            Any: validated object.
            
        """
        if self.allow_equal:
            if self.maximum >= item >= self.minimum:
                return item
            else:
                raise ValueError(
                    f'item must be greater than or equal to {self.minimum} '
                    f'and less than or equal to {self.maximum}')
        else:
            if self.maximum > item > self.minimum:
                return item
            else:
                raise ValueError(
                    f'item must be greater than {self.minimum} '
                    f'and less than {self.maximum}')

