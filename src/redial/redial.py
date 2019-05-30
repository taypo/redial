import os
import signal

import urwid

from redial.config import Config
from redial.ui.footer import FooterButton
from redial.ui.dialog import AddHostDialog,RemoveHostDialog,MessageDialog
from redial.ui.palette import palette


# TODO get rid of this if possible
class State: pass


def reset_layout():
    raise urwid.ExitMainLoop()


class UITreeWidget(urwid.TreeWidget):
    """ Display widget for leaf nodes """

    def __init__(self, node):
        self.__super.__init__(node)
        # set style for node type
        self._w = urwid.AttrWrap(self._w, node.get_value().nodetype, node.get_value().nodetype + "_focus")

    def get_display_text(self):
        return self.get_node().get_value().name

    def selectable(self):
        return True

    def keypress(self, size, key):
        """allow subclasses to intercept keystrokes"""
        key = self.__super.keypress(size, key)

        this_node = self.get_node().get_value()
        parent_node = self.get_node().get_value() if (self.get_node().get_parent() is None) \
            else self.get_node().get_parent().get_value()

        if key == "enter":
            if isinstance(self.get_node(), UITreeNode):
                close_ui_and_run(this_node.hostinfo.get_ssh_command())

        if key in ("-", "left") and not self.is_leaf:
            self.expanded = False
            self.update_expanded_icon()

        elif key == "f5" and self.is_leaf:
            close_ui_and_run(this_node.hostinfo.get_mc_command())

        elif key == "f7":
            AddHostDialog(State, parent_node, reset_layout).show()

        elif key == "f8":
            if this_node.nodetype == "folder":
                # TODO implement removing folder
                MessageDialog(State, "Error", "Folders can not be removed", reset_layout).show()
            else:
                RemoveHostDialog(State, parent_node, this_node, reset_layout).show()
        # TODO implement edit
        # elif key == "f9":
        #    AddHostDialog(State, parent_node, reset_layout).show()
        elif key in ('q', 'Q'):
            close_ui_and_exit()
        return key


class UITreeListBox(urwid.TreeListBox):

    def keypress(self, size, key):
        if key == "left":
            widget, pos = self.body.get_focus()
            self.keypress(size, "-")
            parent_widget, parent_pos = self.body.get_focus()

            if pos == parent_pos and size[1] > 2:
                self.move_focus_to_parent(size)

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
        deleteButton = FooterButton("F8", "Remove")
        editButton = FooterButton("F9", "Edit")
        helpButton = FooterButton("F1", "Help")
        quitButton = FooterButton("Q", "Quit")
        return urwid.GridFlow([connectButton,
                               mcButton,
                               # copySshKeyButton,
                               addButton,
                               deleteButton,
                               # editButton,
                               # helpButton,
                               quitButton], 18, 1, 0, 'center')

    def main(self):
        # Set screen to 256 color mode
        screen = urwid.raw_display.Screen()
        screen.set_terminal_properties(256)

        self.loop = urwid.MainLoop(self.view, palette, screen)
        State.loop = self.loop
        State.body = self.view
        self.loop.run()


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
