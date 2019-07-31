import os
import signal

import urwid
from redial.config import Config
from redial.hostinfo import HostInfo
from redial.tree.node import Node
from redial.ui.dialog import AddHostDialog, MessageDialog, AddFolderDialog, RemoveHostDialog
from redial.ui.footer import init_footer
from redial.ui.tree import UIParentNode, UITreeWidget, UITreeNode, UITreeListBox, State
from redial.ui.palette import palette
from redial.utils import package_available
from functools import partial


EXIT_REDIAL = "__EXIT__"


def on_focus_change(listbox):
    State.focused = listbox.get_focus()[0]


class RedialApplication:

    def __init__(self):
        self.sessions = Config().load_from_file()
        top_node = UIParentNode(self.sessions, key_handler=self.on_key_press)
        self.walker = urwid.TreeWalker(top_node)
        self.listbox = UITreeListBox(self.walker)
        urwid.connect_signal(self.walker, "modified", lambda: on_focus_change(self.listbox))
        header = urwid.Text("Redial")
        footer = init_footer(self.listbox)

        self.view = urwid.Frame(
            urwid.AttrWrap(self.listbox, 'body'),
            header=urwid.AttrWrap(header, 'head'),
            footer=footer)

        # Set screen to 256 color mode
        screen = urwid.raw_display.Screen()
        screen.set_terminal_properties(256)
        self.loop = urwid.MainLoop(self.view, palette, screen)

        # instance attributes
        self.command = None

    def run(self):
        self.loop.run()

    def on_key_press(self, key: str, w: UITreeWidget):
        this_node = w.get_node().get_value()
        folder_node = this_node if (w.get_node().get_parent() is None or this_node.nodetype == "folder") \
            else w.get_node().get_parent().get_value()

        parent_node = None if w.get_node().get_parent() is None else w.get_node().get_parent().get_value()

        if key in 'qQ':
            self.command = EXIT_REDIAL
            raise urwid.ExitMainLoop()

        elif key == "enter":
            if isinstance(w.get_node(), UITreeNode):
                self.command = w.get_node().get_value().hostinfo.get_ssh_command()
                raise urwid.ExitMainLoop()

        elif key == "f5" and w.is_leaf:
            if package_available(package_name="mc"):
                self.command = this_node.hostinfo.get_mc_command()
                raise urwid.ExitMainLoop()
            else:
                MessageDialog("Error", "Please install mc (Midnight Commander) package"
                                       " to use this feature", self.close_dialog).show(self.loop)

        elif key == "f6":
            AddFolderDialog(folder_node, Node("", "folder"), self.save_and_focus).show(self.loop)

        elif key == "f7":
            AddHostDialog(folder_node, Node("", "session", HostInfo("")), self.save_and_focus).show(self.loop)

        elif key == "f8":
            if this_node.nodetype == "folder":
                # TODO implement removing folder
                MessageDialog("Error", "Folders can not be removed", self.close_dialog).show(self.loop)
            else:
                RemoveHostDialog(parent_node, this_node, self.save_and_focus).show(self.loop)

        elif key == "f9" and w.is_leaf:
            AddHostDialog(parent_node, this_node, self.save_and_focus).show(self.loop)

        elif key in ["meta down", "ctrl down"]:
            if parent_node is None: return
            i = parent_node.children.index(this_node)
            if i == len(parent_node.children) - 1: return  # at bottom
            parent_node.children[i], parent_node.children[i + 1] = parent_node.children[i + 1], parent_node.children[i]

            Config.save_to_file(self.sessions)
            self.walker.set_focus(UIParentNode(self.sessions, key_handler=self.on_key_press))
            self.listbox.set_focus_to_node(this_node)

        elif key in ["meta up", "ctrl up"]:
            if parent_node is None: return
            i = parent_node.children.index(this_node)
            if i == 0: return  # at top
            parent_node.children[i], parent_node.children[i - 1] = parent_node.children[i - 1], parent_node.children[i]

            Config.save_to_file(self.sessions)
            self.walker.set_focus(UIParentNode(self.sessions, key_handler=self.on_key_press))
            self.listbox.set_focus_to_node(this_node)
        else:
            return key

    def save_and_focus(self, focus: Node):
        Config().save_to_file(self.sessions)
        self.walker.set_focus(UIParentNode(self.sessions, key_handler=self.on_key_press))
        self.listbox.set_focus_to_node(focus)
        self.loop.widget = self.view

    def close_dialog(self):
        self.loop.widget = self.view


def run():

    app = RedialApplication()

    signal.signal(signal.SIGINT, partial(sigint_handler, app))

    while True:
        app.run()

        if app.command:
            if app.command == EXIT_REDIAL:
                break
            else:
                if os.system(app.command) != 0:
                    break


def sigint_handler(app, signum, frame):
    app.command = EXIT_REDIAL
    raise urwid.ExitMainLoop()


if __name__ == "__main__":
    run()
