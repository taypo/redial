import os
import signal

import urwid

from redial.ui.footer import FooterButton
from redial.ui.dialog import AddHostDialog
from redial.tree.node import Node
from redial.utils import read_ssh_config


class selection: pass


def reset_layout():
    raise urwid.ExitMainLoop()
    #selection.loop.widget = selection.body
    #selection.loop.draw_screen()


# TODO rename example* class names
class ExampleTreeWidget(urwid.TreeWidget):
    """ Display widget for leaf nodes """

    def __init__(self, node):
        self.__super.__init__(node)
        # insert an extra AttrWrap for our own use
        self._w = urwid.AttrWrap(self._w, None)
        self.flagged = False
        self.update_w()

    def get_display_text(self):
        return self.get_node().get_value().name

    def selectable(self):
        return True

    def keypress(self, size, key):
        """allow subclasses to intercept keystrokes"""
        key = self.__super.keypress(size, key)
        selection.key = ""

        if key in ("-", "left") and not self.is_leaf:
            self.expanded = False
            self.update_expanded_icon()
        elif key == "f5" and self.is_leaf:
            hostinfo = self.get_node().get_value().hostinfo
            # TODO move to util. username might be empty, other settings port etc.
            close_ui_and_run("mc . sh://" + hostinfo.username + "@" + hostinfo.ip + ":/home/" + hostinfo.username)
        elif key == "f7":
            AddHostDialog(selection.loop, reset_layout).show()

        if key:
            key = self.unhandled_keys(size, key)
        return key

    def unhandled_keys(self, size, key):
        if key == "enter":
            if isinstance(self.get_node(), ExampleNode):
                hostname = self.create_host_name_from_tree_path()
                close_ui_and_run("ssh " + hostname)

            self.flagged = not self.flagged
            self.update_w()
        else:
            return key

    # TODO should not be needed. refactor
    def create_host_name_from_tree_path(self):
        host_parts = []
        parent = self.get_node().get_parent()
        while parent is not None:
            parent_name = parent.get_value().name
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
            close_ui_and_exit()

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
        return range(len(data.children))

    def load_child_node(self, key):
        """Return either an ExampleNode or ExampleParentNode"""
        childdata = self.get_value().children[key]
        childdepth = self.get_depth() + 1
        if 'folder' in childdata.nodetype:
            childclass = ExampleParentNode
        else:
            childclass = ExampleNode
        return childclass(childdata, parent=self, key=key, depth=childdepth)

    def load_parent(self):
        parentname, myname = os.path.split(self.get_value())
        parent = ExampleParentNode(parentname)
        parent.set_child_node(self.get_key(), self)
        return parent


class RedialApplication:
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
        ('fbutton', 'black', 'dark gray', '', 'g0', '#a8a'),
        ('fbutton_sc', 'dark red', 'black', 'bold', '#600', '#d86'),
    ]

    def __init__(self, data=None):
        self.topnode = ExampleParentNode(data)
        self.listbox = ExampleTreeListBox(urwid.TreeWalker(self.topnode))
        self.listbox.offset_rows = 1
        self.header = urwid.Text("Redial")
        self.footer = self.initFooter()
        self.view = urwid.Frame(
            urwid.AttrWrap(self.listbox, 'body'),
            header=urwid.AttrWrap(self.header, 'head'),
            footer=self.footer)

    def initFooter(self):
        connectButton = FooterButton(u"\u23ce", "Connect")
        mcButton = FooterButton("F5", "Browse")
        copySshKeyButton = FooterButton("F6", "Copy SSH Key")
        addButton = FooterButton("F7", "Add")
        deleteButton = FooterButton("F8", "Delete")
        helpButton = FooterButton("F9", "Help")
        quitButton = FooterButton("Q", "Quit")
        return urwid.GridFlow([connectButton,
                               mcButton,
                               # copySshKeyButton,
                               addButton,
                               # deleteButton,
                               # helpButton,
                               quitButton], 18, 1, 0, 'center')

    def main(self):
        # Set screen to 256 color mode
        screen = urwid.raw_display.Screen()
        screen.set_terminal_properties(256)

        self.loop = urwid.MainLoop(self.view, self.palette, screen,
                                   unhandled_input=self.unhandled_input)
        selection.loop = self.loop
        selection.body = self.view
        self.loop.run()

    def unhandled_input(self, k):
        if k in ('q', 'Q'):
            raise urwid.ExitMainLoop()


def sigint_handler(signum, frame):
    close_ui_and_exit()


def close_ui_and_run(command):
    selection.command = command
    raise urwid.ExitMainLoop()


def close_ui_and_exit():
    selection.exit = True
    raise urwid.ExitMainLoop()


def construct_tree():
    hosts = read_ssh_config()
    root = Node('.')

    for host in hosts:
        prev_part = root
        parts = host.full_name.split("/")
        for part_idx in range(len(parts)):
            if part_idx == len(parts) - 1:
                part = prev_part.add_child(Node(parts[part_idx], "session", host))
            else:
                part = prev_part.add_child(Node(parts[part_idx]))

            prev_part = part

    return root


def run():
    signal.signal(signal.SIGINT, sigint_handler)

    while True:
        # init selection
        selection.command = ""
        selection.exit = False

        # read configuration
        hosts = construct_tree()

        # run UI
        RedialApplication(hosts).main()

        # exit or call other program
        os.system("clear")
        if selection.exit:
            break

        if selection.command:
            os.system(selection.command)
            selection.command = ""


if __name__ == "__main__":
    run()
