"""
test_ashford: tests classes and functions in ashford
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

ToDo:
    
"""
from __future__ import annotations
import abc
import dataclasses

import ashford


@dataclasses.dataclass
class Settings(ashford.Keystone, abc.ABC):
    pass


@dataclasses.dataclass
class Configuration(Settings):
    pass


@dataclasses.dataclass
class FileManager(ashford.Keystone):
    pass

    
def test_unified():
    assert hasattr(ashford.Keystones, 'file_manager') 
    assert hasattr(ashford.Keystones, 'settings')
    assert not hasattr(ashford.Keystones, 'configuration')
    assert ashford.Keystones.settings.contents == {
        'configuration': Configuration}
    assert list(ashford.Keystones.bases.keys()) == ['settings', 'file_manager']
    assert ashford.Keystones.defaults.contents == {
        'settings': 'configuration',
        'file_manager': 'file_manager'}
    return
 
if __name__ == '__main__':
    test_unified()
   