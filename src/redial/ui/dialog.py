import urwid

from redial.hostinfo import HostInfo
from redial.tree.node import Node


class AddHostDialog:

    def __init__(self, state, parent: Node, target: Node, on_close):
        self.loop = state.loop
        self.config = state.config
        self.parent = parent
        self.target = target
        self.on_close = on_close

        # Form Fields
        self.connection_name = urwid.Edit("Connection Name: ", target.name)
        self.ip = urwid.Edit("IP: ", target.hostinfo.ip)
        self.username = urwid.Edit("Username: ", target.hostinfo.username)
        self.port = urwid.Edit("Port: ", "22", target.hostinfo.port)

    def show(self):
        # Header
        header_text = urwid.Text('Edit Connection' if self.target.name else "Add Connection", align='center')
        header = urwid.AttrMap(header_text, 'dialog')

        # Footer
        save_btn = urwid.Button('Save', self.on_save)
        save_btn = urwid.AttrWrap(save_btn, 'dialog_button', 'dialog_button_focus')

        cancel_btn = urwid.Button('Cancel', self.on_cancel)
        cancel_btn = urwid.AttrWrap(cancel_btn, 'dialog_button', 'dialog_button_focus')

        footer = urwid.GridFlow([save_btn, cancel_btn], 12, 1, 1, 'center')

        body = urwid.Filler(
            urwid.Pile([self.connection_name, self.ip, self.username, self.port, footer])
        )

        # Layout
        layout = urwid.Frame(
            body,
            header=header)

        w = urwid.Overlay(
            urwid.AttrMap(urwid.LineBox(layout), "dialog"),
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

        self.target.name = self.connection_name.edit_text
        self.target.hostinfo = host_info

        self.config.add_node(self.parent, self.target)

        self.on_close()

    def on_cancel(self, args):
        self.on_close()


class RemoveHostDialog:

    def __init__(self, state, parent: Node, node: Node, on_close):
        self.loop = state.loop
        self.config = state.config
        self.parent = parent
        self.node = node
        self.on_close = on_close

    def show(self):
        # Header
        header_text = urwid.Text('Remove Connection: ' + self.node.name, align='center')
        header = urwid.AttrMap(header_text, 'dialog')

        # Footer
        ok_btn = urwid.Button('Ok', self.on_ok)
        ok_btn = urwid.AttrWrap(ok_btn, 'dialog_button', 'dialog_button_focus')

        cancel_btn = urwid.Button('Cancel', self.on_cancel)
        cancel_btn = urwid.AttrWrap(cancel_btn, 'dialog_button', 'dialog_button_focus')

        footer = urwid.GridFlow([ok_btn, cancel_btn], 12, 1, 1, 'center')

        body = urwid.Filler(
            urwid.Pile([
                urwid.Text("Are you sure?"),
                urwid.Text(""),
                footer
            ])
        )

        # Layout
        layout = urwid.Frame(
            body,
            header=header
        )

        w = urwid.Overlay(
            urwid.AttrMap(urwid.LineBox(layout), "dialog"),
            self.loop.widget,
            align='center',
            width=40,
            valign='middle',
            height=10
        )

        self.loop.widget = w

    def on_ok(self, args):
        self.config.delete_node(self.parent, self.node)
        self.on_close()

    def on_cancel(self, args):
        self.on_close()


class MessageDialog:

    def __init__(self, state, title, message, on_close):
        self.loop = state.loop
        self.title = title
        self.message = message
        self.on_close = on_close

    def show(self):
        # Header
        header_text = urwid.Text(self.title, align='center')
        header = urwid.AttrMap(header_text, 'dialog')

        # Footer
        ok_btn = urwid.Button('Ok', self.on_ok)
        ok_btn = urwid.AttrWrap(ok_btn, 'dialog_button', 'dialog_button_focus')

        footer = urwid.GridFlow([ok_btn], 12, 1, 1, 'center')

        body = urwid.Filler(
            urwid.Pile([
                urwid.Text(self.message),
                urwid.Text(""),
                footer
            ])
        )

        # Layout
        layout = urwid.Frame(
            body,
            header=header
        )

        w = urwid.Overlay(
            urwid.AttrMap(urwid.LineBox(layout), "dialog"),
            self.loop.widget,
            align='center',
            width=40,
            valign='middle',
            height=10
        )

        self.loop.widget = w

    def on_ok(self, args):
        self.on_close()
