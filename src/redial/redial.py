import urwid
from redial.config import Config
from redial.ui.footer import FooterButton
from redial.ui.tree import UIParentNode
from redial.ui.palette import palette


class RedialApplication:

    def __init__(self):
        # TODO write two static methods config.save and config.load
        self.sessions = Config().get_sessions()
        top_node = UIParentNode(self.sessions)
        walker = urwid.TreeWalker(top_node)
        self.listbox = urwid.TreeListBox(walker)
        header = urwid.Text("Redial")
        footer = self.init_footer()

        self.view = urwid.Frame(
            urwid.AttrWrap(self.listbox, 'body'),
            header=urwid.AttrWrap(header, 'head'),
            footer=footer)

    def run(self):
        # Set screen to 256 color mode
        screen = urwid.raw_display.Screen()
        screen.set_terminal_properties(256)
        loop = urwid.MainLoop(self.view, palette, screen)
        loop.run()

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


if __name__ == "__main__":
    run()
