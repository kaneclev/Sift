from SiftTypes import SiftType, SiftTypes
from Codename import Codename
class SiftURL(SiftType):
    def __init__(self, url: str, codename: Codename):
        super().__init__(SiftTypes.URL)
        self._value: str = url
        self._codename: Codename = codename
        pass
    def __eq__(self, value):
        """ Equality operator for the SiftURL.
        
        Args:
            - _value: SiftURL -> The other URL object to compare against.
        Returns:
            - bool -> True if this URL's '_value' parameter (the actual string URL, NOT the codename)
        """
        
        if not isinstance(value, SiftURL):
            raise TypeError(f'Cannot compare equality between type of {value} and SiftURL.')
        return (self._value == value._value)
    
    def url(self):
        return self._value
    
    def codename(self): 
        return self._codename