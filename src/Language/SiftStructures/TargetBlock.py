from SiftTypes import SiftTypes, SiftType
from Targets import Target
from Codename import Codename
from SiftURL import SiftURL

class TargetBlock(SiftType):
    def __init__(self):
        super().__init__(SiftTypes.TARGET_BLOCK)
        self.targets: list[Target] = []

    def __len__(self):
        return len(self.targets)
    
    def __getitem__(self, index):
        return self.targets[index]
    
    def __contains__(self, value: Target):
        """ Contains method for the TargetBlock class.
        A TargetBlock is considered to 'contain' a particular target if there is an equality between the given target
        and at least one target within the Targets block.
        
        Args:
            - value: Target -> The Target object to test whether or not the TargetBlock contains it.
        Returns:
            - bool: True if there is at least one equality between a target in the current target block and the given Target object.
        """
        
        for targ in self.targets:
            if targ == value:
                return True
        return False
    
    def append(self, value: Target) -> int:
        """ Append method for the TargetBlock as it acts as a container.

        Args:
            - value: target -> Some object of type 'Target' to be added to this TargetBlock.
        Returns:
            - int: the index of the 'value' in the TargetBlock.        
        """
        
        self.targets.append(value)
        return len(self.targets) - 1
    
    def find(self, value: Target) -> int:
        """ Returns the index of the value of the Target object if it exists in the TargetBlock, otherwise -1.
        Whether a target exists in the TargetBlock is dependent on if there is some Target in the TargetBlock whose equality operator (target == value) returns true.
        Args:
            - value: Target -> The Target object to search for.
        Returns:
            - int: The index of the target object if it exists otherwise -1.
        """
        if not isinstance(value, Target):
            raise TypeError(f'The TargetBlock find method was invoked with an object not of type Target. Here was the unexpected type: {type(value)}')
        for idx, targ in enumerate(self.targets):
            if targ == value:
                return idx
        return -1
    
    def find(self, url: SiftURL) -> int:
        """ Returns the index of the value of the Target object if it exists in the TargetBlock, otherwise -1.
        Whether a target exists in the TargetBlock is dependent on if there is some Target in the TargetBlock whose URL is the same as the provided URL.
        Args:
            - value: Target -> The Target object to search for.
        Returns:
            - int: The index of the target object if it exists otherwise -1.
        """
        if not isinstance(url, SiftURL):
            raise TypeError(f"TargetBlock's find(SiftURL) method was called with a type that is not a SiftURL. Here's the type instead: {type(url)}")
        for idx, targ in enumerate(self.targets):
            if targ.url() == url:
                return idx
        return -1
    
    def find(self, codename: Codename):
        """ Returns the index of the value of the Target object if it exists in the TargetBlock, otherwise -1.
        Whether a target exists in the TargetBlock is dependent on if there is some Target in the TargetBlock whose codename is the same as the provided codename.
        Args:
            - value: Target -> The Target object to search for.
        Returns:
            - int: The index of the target object if it exists otherwise -1.
        """
        if not isinstance(codename, Codename):
            raise TypeError(f"TargetBlock's find(Codename) method was called with a type that is not a SiftURL. Here's the type instead: {type(codename)}")
        for idx, targ in enumerate(self.targets):
            if targ.codename() == codename:
                return idx
        return -1