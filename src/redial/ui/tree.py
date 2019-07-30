import os

import urwid


class UITreeWidget(urwid.TreeWidget):
    def __init__(self, node):
        self.__super.__init__(node)
        self.key_handler = node.key_handler
        # set style for node type
        self._w = urwid.AttrWrap(self._w, node.get_value().nodetype, node.get_value().nodetype + "_focus")

    def get_display_text(self):
        return self.get_node().get_value().name

    def selectable(self):
        return True

    def keypress(self, size, key):
        return self.key_handler(key, self)


class UITreeListBox(urwid.TreeListBox):
    pass


class UITreeNode(urwid.TreeNode):
    """ Data storage object for leaf nodes """

    def __init__(self, value, parent=None, key=None, depth=None, key_handler=None):
        urwid.TreeNode.__init__(self, value, parent=parent, key=key, depth=depth)
        self.key_handler = key_handler

    def load_widget(self):
        return UITreeWidget(self)


class UIParentNode(urwid.ParentNode):
    """ Data storage object for interior/parent nodes """
    def __init__(self, value, parent=None, key=None, depth=None, key_handler=None):
        urwid.ParentNode.__init__(self, value, parent=parent, key=key, depth=depth)
        self.key_handler = key_handler

    def load_widget(self):
        return UITreeWidget(self)

    def load_child_keys(self):
        data = self.get_value()
        return range(len(data.children))

    def load_child_node(self, key):
        """Return either an UITreeNode or UIParentNode"""
        child_data = self.get_value().children[key]
        child_depth = self.get_depth() + 1
        if 'folder' in child_data.nodetype:
            child_class = UIParentNode
        else:
            child_class = UITreeNode
        return child_class(child_data, parent=self, key=key, depth=child_depth, key_handler=self.key_handler)

