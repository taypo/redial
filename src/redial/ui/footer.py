import urwid

def do_nothing(key): pass

class FooterButton(urwid.Button):
    def __init__(self, sc, caption, callback = do_nothing):
        super(FooterButton, self).__init__("")
        urwid.connect_signal(self, 'click', callback)
        self._w = urwid.AttrWrap(urwid.Text([('fbutton_sc', " " + sc + " "), " ", ('fbutton', caption)]), 'fbutton')
