class TreeNode:
    def __init__(self, name):
        self.name = name
        self.children = []
    def add_child(self, child):
        if child:
            self.children.append(child)
    def prune(self):
        new_children = []
        for child in self.children:
            if child:
                returned_child = child.prune()
                if returned_child:
                    new_children.append(returned_child)
        self.children = new_children
        if len(self.children) > 0:
            return self
        else:
            return None
    def print(self, tabs = 0):
        print(("\t" * tabs) + self.name)
        for child in self.children:
            child.print(tabs = tabs + 1)

class TreeLeaf:
    def __init__(self, value = None):
        self.value = value
    def prune(self):
        return self
    def print(self, tabs = 0):
        print(("\t" * tabs) + self.value)
