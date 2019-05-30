import urwid

from redial.hostinfo import HostInfo
from redial.tree.node import Node


class AddHostDialog:

    def __init__(self, state, parent: Node, on_close):
        self.loop = state.loop
        self.config = state.config
        self.parent = parent
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

        node = Node(self.connection_name.edit_text, "session", host_info)
        self.config.add_node(self.parent, node)

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
        header_text = urwid.Text(('banner', 'Remove Connection: ' + self.node.name), align='center')
        header = urwid.AttrMap(header_text, 'banner')

        # Footer
        ok_btn = urwid.Button('Ok', self.on_ok)
        ok_btn = urwid.AttrWrap(ok_btn, 'selectable', 'focus')

        cancel_btn = urwid.Button('Cancel', self.on_cancel)
        cancel_btn = urwid.AttrWrap(cancel_btn, 'selectable', 'focus')

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
            urwid.LineBox(layout),
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
        header_text = urwid.Text(('banner', self.title), align='center')
        header = urwid.AttrMap(header_text, 'banner')

        # Footer
        ok_btn = urwid.Button('Ok', self.on_ok)
        ok_btn = urwid.AttrWrap(ok_btn, 'selectable', 'focus')

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
            urwid.LineBox(layout),
            self.loop.widget,
            align='center',
            width=40,
            valign='middle',
            height=10
        )

        self.loop.widget = w

    def on_ok(self, args):
        self.on_close()
