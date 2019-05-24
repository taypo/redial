import os
import signal

import urwid

from redial.config import Config
from redial.ui.footer import FooterButton
from redial.ui.dialog import AddHostDialog
from redial.ui.palette import palette

# TODO get rid of this if possible
class State: pass


def reset_layout():
    raise urwid.ExitMainLoop()
    #selection.loop.widget = selection.body
    #selection.loop.draw_screen()


class UITreeWidget(urwid.TreeWidget):
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

        if key in ("-", "left") and not self.is_leaf:
            self.expanded = False
            self.update_expanded_icon()
        elif key == "f5" and self.is_leaf:
            hostinfo = self.get_node().get_value().hostinfo
            # TODO move to util. username might be empty, other settings port etc.
            close_ui_and_run("mc . sh://" + hostinfo.username + "@" + hostinfo.ip + ":" + hostinfo.port + "/home/" + hostinfo.username)
        elif key == "f7":
            AddHostDialog(State.loop, reset_layout).show()

        if key:
            key = self.unhandled_keys(size, key)
        return key

    def unhandled_keys(self, size, key):
        if key == "enter":
            if isinstance(self.get_node(), UITreeNode):
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


class UITreeListBox(urwid.TreeListBox):

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


class UITreeNode(urwid.TreeNode):
    """ Data storage object for leaf nodes """

    def load_widget(self):
        return UITreeWidget(self)

    def load_parent(self):
        parentname, myname = os.path.split(self.get_value())
        parent = UIParentNode(parentname)
        parent.set_child_node(self.get_key(), self)
        return parent


class UIParentNode(urwid.ParentNode):
    """ Data storage object for interior/parent nodes """

    def load_widget(self):
        return UITreeWidget(self)

    def load_child_keys(self):
        data = self.get_value()
        return range(len(data.children))

    def load_child_node(self, key):
        """Return either an ExampleNode or ExampleParentNode"""
        childdata = self.get_value().children[key]
        childdepth = self.get_depth() + 1
        if 'folder' in childdata.nodetype:
            childclass = UIParentNode
        else:
            childclass = UITreeNode
        return childclass(childdata, parent=self, key=key, depth=childdepth)

    def load_parent(self):
        parentname, myname = os.path.split(self.get_value())
        parent = UIParentNode(parentname)
        parent.set_child_node(self.get_key(), self)
        return parent


class RedialApplication:

    def __init__(self, data=None):
        self.topnode = UIParentNode(data)
        self.listbox = UITreeListBox(urwid.TreeWalker(self.topnode))
        self.listbox.offset_rows = 1
        self.header = urwid.Text("Redial")
        self.footer = self.initFooter()
        self.loop = None
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

        self.loop = urwid.MainLoop(self.view, palette, screen,
                                   unhandled_input=self.unhandled_input)
        State.loop = self.loop
        State.body = self.view
        self.loop.run()

    def unhandled_input(self, k):
        if k in ('q', 'Q'):
            raise urwid.ExitMainLoop()


def sigint_handler(signum, frame):
    close_ui_and_exit()


def close_ui_and_run(command):
    State.command = command
    raise urwid.ExitMainLoop()


def close_ui_and_exit():
    State.exit = True
    raise urwid.ExitMainLoop()


def run():
    signal.signal(signal.SIGINT, sigint_handler)

    while True:
        # init selection
        State.command = ""
        State.exit = False

        # read configuration
        State.config = Config()
        sessions = State.config.get_sessions()

        # run UI
        RedialApplication(sessions).main()

        # exit or call other program
        os.system("clear")
        if State.exit:
            break

        if State.command:
            os.system(State.command)
            State.command = ""


if __name__ == "__main__":
    run()
