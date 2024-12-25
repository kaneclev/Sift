from typing import List
from SiftURL import SiftURL
from Codename import Codename
from SiftTypes import SiftTypes, SiftType
class Target:
    def __init__(self, codename: Codename, url: SiftURL):
        super().__init__(SiftTypes.TARGET)
        self.codename: Codename = codename
        self.url: SiftURL = url
        pass
    def __eq__(self, value):
        """ Equality operator for the Target object.

        Args:
            - value: Target -> The other Target object to compare against.
        Returns:
            - bool: True if BOTH the target's URL AND the target's codename are equal to the value's.
        """
        if not isinstance(value, Target):
            raise TypeError(f'Cannot compare the current Target object against an object of type {type(value)}')
        
        return (self.url == value.url) and (self.codename == value.codename)