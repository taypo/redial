import os

import urwid
from redial.config import Config
from redial.hostinfo import HostInfo
from redial.tree.node import Node
from redial.ui.dialog import AddHostDialog
from redial.ui.footer import FooterButton
from redial.ui.tree import UIParentNode, UITreeWidget, UITreeNode, UITreeListBox
from redial.ui.palette import palette


class RedialApplication:

    def __init__(self):
        # TODO write two static methods config.save and config.load
        self.sessions = Config().load_from_file()
        top_node = UIParentNode(self.sessions, key_handler=self.on_key_press)
        self.walker = urwid.TreeWalker(top_node)
        self.listbox = UITreeListBox(self.walker)
        header = urwid.Text("Redial")
        footer = self.init_footer()

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
            raise urwid.ExitMainLoop()
        elif key == "enter":
            if isinstance(w.get_node(), UITreeNode):
                self.command = w.get_node().get_value().hostinfo.get_ssh_command()
                raise urwid.ExitMainLoop()
        elif key == "f7":
            AddHostDialog(folder_node, Node("", "session", HostInfo("")), self.save_and_reload).show(self.loop)
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

    def save_and_reload(self):
        Config().save_to_file(self.sessions)
        # todo set focus
        self.walker.set_focus(UIParentNode(self.sessions, key_handler=self.on_key_press))
        self.loop.widget = self.view

    # TODO move to footer.py
    def init_footer(self):
        connect_button = FooterButton(u"\u23ce", "Connect", "enter", self.on_footer_click)
        mc_button = FooterButton("F5", "Browse", "f5", self.on_footer_click)
        add_folder_button = FooterButton("F6", "New Folder", "f6", self.on_footer_click)
        add_button = FooterButton("F7", "New Conn.", "f7", self.on_footer_click)
        delete_button = FooterButton("F8", "Remove", "f8", self.on_footer_click)
        edit_button = FooterButton("F9", "Edit", "f9", self.on_footer_click)
        quit_button = FooterButton("Q", "Quit", "q", self.on_footer_click)
        # TODO keys that dont depend on selected node should be handled differently

        return urwid.GridFlow([connect_button,
                               mc_button,
                               # TODO join add buttons to one
                               add_folder_button,
                               add_button,
                               delete_button,
                               edit_button,
                               quit_button], 18, 1, 0, 'center')

    # TODO move to footer.py
    def on_footer_click(self, button: FooterButton):
        button.on_click(self.listbox.get_focus())


def run():
    app = RedialApplication()
    app.run()

    # TODO restart application after connection closes
    if app.command:
        os.system(app.command)


if __name__ == "__main__":
    run()
