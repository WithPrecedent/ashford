"""
framework: functions for changing ashford settings
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

        
ToDo:


"""
from __future__ import annotations
from collections.abc import Callable
from typing import Any, Type

from . import configuration
    

def set_keyer(keyer: Callable[[object | Type[Any]], str]) -> None:
    """Sets the global default function used to name items.

    Args:
        keyer (Callable[[object | Type[Any]], str]): function that returns a 
            str name of any item passed.

    Raises:
        TypeError: if 'keyer' is not callable.
        
    """
    if isinstance(keyer, Callable):
        configuration.KEYER = keyer
    else:
        raise TypeError('keyer argument must be a callable')

def set_method_keyer(keyer: Callable[[object | Type[Any]], str]) -> None:
    """Sets the global default function used to name factory methods.

    Args:
        keyer (Callable[[object | Type[Any]], str]): function that returns a 
            str name of any item passed.

    Raises:
        TypeError: if 'keyer' is not callable.
        
    """
    if isinstance(keyer, Callable):
        configuration.METHOD_NAMER = keyer
    else:
        raise TypeError('keyer argument must be a callable')
    