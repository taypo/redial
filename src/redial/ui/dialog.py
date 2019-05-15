import urwid

from redial.utils import append_to_config
from redial.hostinfo import HostInfo


class AddHostDialog:

    def __init__(self, loop: urwid.MainLoop, on_close):
        self.loop = loop
        self.on_close = on_close

        # Form Fields
        self.connection_name = urwid.Edit("Connection Name: ")
        self.ip = urwid.Edit("IP: ")
        self.username = urwid.Edit("Username: ")
        self.port = urwid.Edit("Port: ", "22")

    def show(self):
        # Header
        header_text = urwid.Text(('banner', 'Add Connection'), align='center')
        header = urwid.AttrMap(header_text, 'banner')



        # Footer
        save_btn = urwid.Button('Save', self.on_save)
        save_btn = urwid.AttrWrap(save_btn, 'selectable', 'focus')

        cancel_btn = urwid.Button('Cancel', self.on_cancel)
        cancel_btn = urwid.AttrWrap(cancel_btn, 'selectable', 'focus')

        footer = urwid.GridFlow([save_btn, cancel_btn], 12, 1, 1, 'center')

        body = urwid.Filler(
            urwid.Pile([self.connection_name, self.ip, self.username, self.port, footer])
        )

        # Layout
        layout = urwid.Frame(
            body,
            header=header
        )

        w = urwid.Overlay(
            urwid.LineBox(layout),
            self.loop.widget,
            align='center',
            width=40,
            valign='middle',
            height=10
        )

        self.loop.widget = w

    def on_save(self, args):
        host_info = HostInfo(self.connection_name.edit_text)
        host_info.ip = self.ip.edit_text
        host_info.port = self.port.edit_text
        host_info.username = self.username.edit_text
        append_to_config(host_info)

        self.on_close()

    def on_cancel(self, args):
        self.on_close()
