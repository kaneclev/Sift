class SiftNode:
    """ base class for all sift lang """
    pass

class TargetNode(SiftNode):
    def __init__(self, alias, url):
        self.alias = alias
        self.url = url
        pass
    def __repr__(self):
        return f"TargetNode(alias={self.alias}, url={self.url})"
    
class ActionBlockNode(SiftNode):
    def __init__(self, alias, actions):
        self.alias = alias
        self.actions = actions
        pass
    def __repr__(self):
        return f"ActionBlockNode(alias={self.alias}, actions={self.actions})"
    
class SiftActionNode(SiftNode):
    def __init__(self, content_type=None, filters=None, codename=None):
        self.content_type = content_type
        self.filters = filters or []
        self.codename = codename

    def __repr__(self):
        return f"SiftActionNode(content_type={self.content_type}, filters={self.filters}, codename={self.codename})"
