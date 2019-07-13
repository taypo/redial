import urwid


def do_nothing(key): pass


class FooterButton(urwid.Button):

    def __init__(self, sc, caption, key, callback=do_nothing):
        super(FooterButton, self).__init__("")
        self.key = key
        urwid.connect_signal(self, 'click', callback)
        self._w = urwid.AttrWrap(urwid.Text([('fbutton_sc', " " + sc + " "), " ", ('fbutton', caption)]), 'fbutton')

    def on_click(self, widget_on_focus):
        widget_on_focus[0].keypress(0, self.key)
