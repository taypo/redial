import os
import signal

import urwid

from redial.config import Config
from redial.hostinfo import HostInfo
from redial.tree.node import Node
from redial.ui.footer import FooterButton
from redial.ui.dialog import AddHostDialog, RemoveHostDialog, MessageDialog, AddFolderDialog
from redial.ui.palette import palette
from redial.utils import package_available


# TODO get rid of this if possible
class State: pass


def reset_layout():
    raise urwid.ExitMainLoop()


def reload_data():
    State.walker.set_focus(UIParentNode(State.sessions))
    State.loop.widget = State.body


def on_focus_change():
    State.focused = State.listbox.get_focus()[0]


class UITreeWidget(urwid.TreeWidget):
    """ Display widget for leaf nodes """

    def __init__(self, node):
        self.__super.__init__(node)
        # set style for node type
        self._w = urwid.AttrWrap(self._w, node.get_value().nodetype, node.get_value().nodetype + "_focus")

    def get_display_text(self):
        if State.focused and State.focused.get_node() == self.get_node():
            return self.get_node().get_value().name + " " + self.get_node().get_value().hostinfo.ip
        else:
            return self.get_node().get_value().name

    def selectable(self):
        return True

    def keypress(self, size, key):
        """allow subclasses to intercept keystrokes"""
        key = self.__super.keypress(size, key)

        this_node = self.get_node().get_value()
        parent_node = this_node if (self.get_node().get_parent() is None or this_node.nodetype == "folder") \
            else self.get_node().get_parent().get_value()

        if key == "enter":
            if isinstance(self.get_node(), UITreeNode):
                close_ui_and_run(this_node.hostinfo.get_ssh_command())

        if key in ("-", "left") and not self.is_leaf:
            self.expanded = False
            self.update_expanded_icon()

        elif key == "f5" and self.is_leaf:
            if package_available(package_name="mc"):
                close_ui_and_run(this_node.hostinfo.get_mc_command())
            else:
                MessageDialog(State, "Error", "Please install mc (Midnight Commander) package"
                                              " to use this feature", reset_layout).show()

        elif key == "f6":
            AddFolderDialog(State, parent_node, Node("", "folder"), reload_data).show()

        elif key == "f7":
            AddHostDialog(State, parent_node, Node("", "session", HostInfo("")), reload_data).show()

        elif key == "f8":
            if this_node.nodetype == "folder":
                # TODO implement removing folder
                MessageDialog(State, "Error", "Folders can not be removed", reload_data).show()
            else:
                RemoveHostDialog(State, parent_node, this_node, reload_data).show()
        elif key == "f9" and self.is_leaf:
            AddHostDialog(State, parent_node, this_node, reload_data).show()
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
            if key not in ['home', 'end']:
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
    
    def get_widget(self, reload=False):
        return super().get_widget(True)


class UIParentNode(urwid.ParentNode):
    """ Data storage object for interior/parent nodes """

    def load_widget(self):
        return UITreeWidget(self)

    def load_child_keys(self):
        data = self.get_value()
        return range(len(data.children))

    def load_child_node(self, key):
        """Return either an UITreeNode or UIParentNode"""
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
        walker = urwid.TreeWalker(self.topnode)
        State.walker = walker
        urwid.connect_signal(walker, "modified", on_focus_change)
        self.listbox = UITreeListBox(walker)
        State.listbox = self.listbox
        self.listbox.offset_rows = 1
        self.header = urwid.Text("Redial")
        self.footer = self.initFooter()
        self.loop = None
        self.view = urwid.Frame(
            urwid.AttrWrap(self.listbox, 'body'),
            header=urwid.AttrWrap(self.header, 'head'),
            footer=self.footer)

    def initFooter(self):
        connectButton = FooterButton(u"\u23ce", "Connect", "enter", self.on_footer_click)
        mcButton = FooterButton("F5", "Browse", "f5", self.on_footer_click)
        addFolderButton = FooterButton("F6", "New Folder", "f6", self.on_footer_click)
        addButton = FooterButton("F7", "New Conn.", "f7", self.on_footer_click)
        deleteButton = FooterButton("F8", "Remove", "f8", self.on_footer_click)
        editButton = FooterButton("F9", "Edit", "f9", self.on_footer_click)
        quitButton = FooterButton("Q", "Quit", "q", self.on_footer_click)
        # TODO keys that dont depend on selected node should be handled differently

        return urwid.GridFlow([connectButton,
                               mcButton,
                               # TODO join add buttons to one
                               addFolderButton,
                               addButton,
                               deleteButton,
                               editButton,
                               quitButton], 18, 1, 0, 'center')

    def main(self):
        # Set screen to 256 color mode
        if State.last_focus is not None:
            self.listbox.set_focus(State.last_focus)
        screen = urwid.raw_display.Screen()
        screen.set_terminal_properties(256)
        self.loop = urwid.MainLoop(self.view, palette, screen)
        State.loop = self.loop
        State.body = self.view
        self.loop.run()

    def on_footer_click(self, button: FooterButton):
        button.on_click(self.listbox.get_focus())


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
    # TODO below two should be simplified.
    State.last_focus = None
    State.focused = None

    # read configuration
    State.config = Config()
    State.sessions = State.config.get_sessions()

    while True:
        # init selection
        State.command = ""
        State.exit = False

        # run UI
        app = RedialApplication(State.sessions)
        app.main()

        # exit or call other program
        os.system("clear")
        if State.exit:
            break

        if State.command:
            _, State.last_focus = app.listbox.get_focus()
            os.system(State.command)
            State.command = ""


if __name__ == "__main__":
    run()
