from redial.hostinfo import HostInfo


class Node(object):
    def __init__(self, name, nodetype="folder", hostinfo: HostInfo = None):
        self.name = name
        self.children = []
        self.nodetype = nodetype
        self.hostinfo = hostinfo

    def add_child(self, node: 'Node'):
        child_found = [c for c in self.children if c.name == node.name]
        if child_found:
            return child_found[0]
        else:
            self.children.append(node)
            return node
