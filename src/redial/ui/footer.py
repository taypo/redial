import urwid


def do_nothing(key): pass


class FooterButton(urwid.Button):

    def __init__(self, sc, caption, key, callback=do_nothing):
        super(FooterButton, self).__init__("")
        self.key = key
        urwid.connect_signal(self, 'click', callback)
        self._w = urwid.AttrWrap(urwid.Text([('fbutton_sc', " " + sc + " "), " ", ('fbutton', caption)]), 'fbutton')

    def on_click(self, widget_on_focus):
        widget_on_focus[0].keypress((0, ), self.key)


def init_footer(listbox):
    connect_button = FooterButton(u"\u23ce", "Connect", "enter", lambda button: button.on_click(listbox.get_focus()))
    sshkey_button = FooterButton("F3", "Copy SSH Key", "f3", lambda button: button.on_click(listbox.get_focus()))
    mc_button = FooterButton("F5", "Browse", "f5", lambda button: button.on_click(listbox.get_focus()))
    add_folder_button = FooterButton("F6", "New Folder", "f6", lambda button: button.on_click(listbox.get_focus()))
    add_button = FooterButton("F7", "New Conn.", "f7", lambda button: button.on_click(listbox.get_focus()))
    delete_button = FooterButton("F8", "Remove", "f8", lambda button: button.on_click(listbox.get_focus()))
    edit_button = FooterButton("F9", "Edit", "f9", lambda button: button.on_click(listbox.get_focus()))
    quit_button = FooterButton("Q", "Quit", "q", lambda button: button.on_click(listbox.get_focus()))
    # TODO keys that dont depend on selected node should be handled differently

    return urwid.GridFlow([connect_button,
                           sshkey_button,
                           mc_button,
                           # TODO join add buttons to one
                           add_folder_button,
                           add_button,
                           delete_button,
                           edit_button,
                           quit_button], 18, 1, 0, 'center')
