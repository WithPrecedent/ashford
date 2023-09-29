"""
configuration: settings for ashford
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
import dataclasses
from typing import Any, Type

import camina
    

KEYER: Callable[[object | Type[Any]], str] = camina.namify
METHOD_NAMER: Callable[[object | Type[Any]], str] = lambda x: f'from_{KEYER(x)}'
REMOVABLE_PREFIXES: list[str] = ['project_']


@dataclasses.dataclass
class MISSING_VALUE(object):
    """Sentinel object for a missing data or parameter.
    
    This follows the same pattern as the '_MISSING_TYPE' class in the builtin
    dataclasses library. 
    https://github.com/python/cpython/blob/3.10/Lib/dataclasses.py#L182-L186
    
    Because None is sometimes a valid argument or data option, this class
    provides an alternative that does not create the confusion that a default of 
    None can sometimes lead to.
    
    """
    pass


# MISSING, instance of MISSING_VALUE, should be used for missing values as an 
# alternative to None. This provides a fuller repr and traceback.
MISSING = MISSING_VALUE()  
