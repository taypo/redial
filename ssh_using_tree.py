import os
import signal

import urwid

from tree.node import Node
from utils import read_ssh_config


class selection: pass


class ExampleTreeWidget(urwid.TreeWidget):
    """ Display widget for leaf nodes """

    def __init__(self, node):
        self.__super.__init__(node)
        # insert an extra AttrWrap for our own use
        self._w = urwid.AttrWrap(self._w, None)
        self.flagged = False
        self.update_w()

    def get_display_text(self):
        return self.get_node().get_value()['name']

    def selectable(self):
        return True

    def keypress(self, size, key):
        """allow subclasses to intercept keystrokes"""
        key = self.__super.keypress(size, key)

        if key in ("-", "left") and not self.is_leaf:
            self.expanded = False
            self.update_expanded_icon()

        if key:
            key = self.unhandled_keys(size, key)
        return key

    def unhandled_keys(self, size, key):
        """
        Override this method to intercept keystrokes in subclasses.
        Default behavior: Toggle flagged on space, ignore other keys.
        """
        if key == "enter":
            if isinstance(self.get_node(), ExampleNode):
                host_name = self.create_host_name_from_tree_path()
                selection.ssh = host_name
                exit_program()

            self.flagged = not self.flagged
            self.update_w()
        else:
            return key

    def create_host_name_from_tree_path(self):
        host_parts = []
        parent = self.get_node().get_parent()
        while parent is not None:
            parent_name = parent.get_value()['name']
            host_parts.append(parent_name)
            parent = parent.get_parent()

        host_name = self.get_display_text()
        for part in host_parts:
            host_name = part + "/" + host_name

        return host_name.replace("./", "")

    def update_w(self):
        """Update the attributes of self.widget based on self.flagged.
        """
        if self.flagged:
            self._w.attr = 'flagged'
            self._w.focus_attr = 'flagged focus'
        else:
            self._w.attr = 'body'
            self._w.focus_attr = 'focus'


class ExampleTreeListBox(urwid.TreeListBox):

    def keypress(self, size, key):
        if key == "left":
            widget, pos = self.body.get_focus()
            self.keypress(size, "-")
            parent_widget, parent_pos = self.body.get_focus()

            if pos == parent_pos and size[1] > 2:
                self.move_focus_to_parent(size)
        elif key in ('q', 'Q'):
            exit_program()

        else:
            self.__super.keypress(size, key)


class ExampleNode(urwid.TreeNode):
    """ Data storage object for leaf nodes """

    def load_widget(self):
        return ExampleTreeWidget(self)

    def load_parent(self):
        parentname, myname = os.path.split(self.get_value())
        parent = ExampleParentNode(parentname)
        parent.set_child_node(self.get_key(), self)
        return parent


class ExampleParentNode(urwid.ParentNode):
    """ Data storage object for interior/parent nodes """

    def load_widget(self):
        return ExampleTreeWidget(self)

    def load_child_keys(self):
        data = self.get_value()
        return range(len(data['children']))

    def load_child_node(self, key):
        """Return either an ExampleNode or ExampleParentNode"""
        childdata = self.get_value()['children'][key]
        childdepth = self.get_depth() + 1
        if 'children' in childdata:
            childclass = ExampleParentNode
        else:
            childclass = ExampleNode
        return childclass(childdata, parent=self, key=key, depth=childdepth)

    def load_parent(self):
        parentname, myname = os.path.split(self.get_value())
        parent = ExampleParentNode(parentname)
        parent.set_child_node(self.get_key(), self)
        return parent


class ExampleTreeBrowser:
    palette = [
        ('body', 'black', 'light gray'),
        ('flagged', 'black', 'dark green', ('bold', 'underline')),
        ('focus', 'light gray', 'dark blue', 'standout'),
        ('flagged focus', 'yellow', 'dark cyan',
         ('bold', 'standout', 'underline')),
        ('head', 'yellow', 'black', 'standout'),
        ('foot', 'light gray', 'black'),
        ('key', 'light cyan', 'black', 'underline'),
        ('title', 'white', 'black', 'bold'),
        ('dirmark', 'black', 'dark cyan', 'bold'),
        ('flag', 'dark gray', 'light gray'),
        ('error', 'dark red', 'light gray'),
    ]

    footer_text = [
        ('title', "SSH Manager"), "    ",
        ('key', "UP"), ",", ('key', "DOWN"), ",",
        ('key', "PAGE UP"), ",", ('key', "PAGE DOWN"),
        "  ",
        ('key', "+"), ",",
        ('key', "-"), "  ",
        ('key', "LEFT"), "  ",
        ('key', "Q"),
    ]

    def __init__(self, data=None):
        self.topnode = ExampleParentNode(data)
        self.listbox = ExampleTreeListBox(urwid.TreeWalker(self.topnode))
        self.listbox.offset_rows = 1
        self.header = urwid.Text("")
        self.footer = urwid.AttrWrap(urwid.Text(self.footer_text),
                                     'foot')
        self.view = urwid.Frame(
            urwid.AttrWrap(self.listbox, 'body'),
            header=urwid.AttrWrap(self.header, 'head'),
            footer=self.footer)

    def main(self):
        """Run the program."""
        self.loop = urwid.MainLoop(self.view, self.palette,
                                   unhandled_input=self.unhandled_input)
        self.loop.run()

    def unhandled_input(self, k):
        if k in ('q', 'Q'):
            raise urwid.ExitMainLoop()


def sigint_handler(signum, frame):
    exit_program()


def exit_program():
    raise urwid.ExitMainLoop()


def get_example_tree():
    path1 = "sub1/grandsub1/file1"
    path2 = "sub2/grandsub1/file1"
    path3 = "sub2/grandsub1/file2"
    path4 = "sub3/grandsub1/file1"
    path5 = "sub3/grandsub2/file1"

    paths = [path1, path2, path3, path4, path5]

    root = Node('parent')

    for path in paths:
        parts = path.split("/")
        prev_part = root
        for part in parts:
            part = prev_part.child(part)
            prev_part = part

    return root.as_dict()


def construct_tree():
    hosts = read_ssh_config()

    configs = [host.full_name for host in hosts]

    root = Node('.')

    for config in configs:
        prev_part = root
        parts = config.split("/")
        for part_idx in range(len(parts)):
            if part_idx == len(parts) - 1:
                part = prev_part.child(parts[part_idx], type="session")
            else:
                part = prev_part.child(parts[part_idx], type="folder")

            prev_part = part

    return root.as_dict()


def main():
    signal.signal(signal.SIGINT, sigint_handler)
    selection.ssh = ""
    # sample = get_example_tree()
    hosts = construct_tree()
    ExampleTreeBrowser(hosts).main()

    os.system("clear")

    if selection.ssh != "":
        print("ssh " + selection.ssh)
        os.system("ssh " + selection.ssh)


if __name__ == "__main__":
    main()
