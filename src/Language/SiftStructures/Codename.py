from SiftTypes import SiftType, SiftTypes

class Codename(SiftType):
    """ Codename is a SiftType which is an Alias. 
    The alias can reference multiple things; a URL, the result of some request, the result of some filter, or select statement, or otherwise. 
    Preceeded by a pipe (|) symbol.

    Args:
        - name: str -> The alias for the codename.
        - references: SiftType -> The actual object or result that the Codename references.   

    """
    
    def __init__(self, name: str, referencing: SiftType):
        super().__init__(SiftTypes.CODENAME)
        assert(isinstance(name, str)) 
        assert(isinstance(referencing, SiftType))
        self._references: SiftType = referencing
        self._name: str = name
        pass

    def __str__(self):
        return f'Codename(Name: {self._name}, References: {str(self._references)})'
    
    def __repr__(self):
        return f'Codename({self._name}, {repr(self._references)})'
    def __eq__(self, value):
        """ The equality operator to compare two Codename objects.

        Args:
            - value: Codename -> The codename object to compare against.
        Returns:
            - bool: True if the value's ._name attribute is equal to this object's ._name attribute. False otherwise.
        """
        
        if not isinstance(value, Codename):
            raise TypeError(f"Codename's equality operator was called with a type which was not of Codename; here is the type: {type(value)}")
        return self._name == value._name
    def name(self):
        return self._name
    def references(self):
        return self._references