import urwid

from redial.hostinfo import HostInfo
from redial.tree.node import Node


class AddHostDialog:

    def __init__(self, parent: Node, target: Node, on_close):
        self.parent = parent
        self.target = target
        self.on_close = on_close

        # Form Fields
        self.connection_name = urwid.Edit("Connection Name: ", target.name)
        self.ip = urwid.Edit("IP: ", target.hostinfo.ip)
        self.username = urwid.Edit("Username: ", target.hostinfo.username)
        self.port = urwid.Edit("Port: ", target.hostinfo.port if self.target.name else "22")

    def show(self, loop):
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

        w = DialogOverlay(
            on_close=lambda: self.on_close(self.parent),
            on_enter=self.on_save,
            top_w=urwid.AttrMap(urwid.LineBox(layout), "dialog"),
            bottom_w=loop.widget,
            align='center',
            width=40,
            valign='middle',
            height=10
        )

        loop.widget = w

    def on_save(self, args=None):
        host_info = HostInfo(self.connection_name.edit_text)
        host_info.ip = self.ip.edit_text
        host_info.port = self.port.edit_text
        host_info.username = self.username.edit_text

        self.target.name = self.connection_name.edit_text
        self.target.hostinfo = host_info

        self.parent.add_child(self.target)

        self.on_close(self.target)

    def on_cancel(self, args):
        self.on_close(self.parent)


class RemoveHostDialog:

    def __init__(self, parent: Node, target: Node, on_close):
        self.parent = parent
        self.target = target
        self.on_close = on_close

    def show(self, loop):
        # Header
        header_text = urwid.Text('Remove Connection: ' + self.target.name, align='center')
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

        w = DialogOverlay(
            on_close=lambda: self.on_close(self.target),
            on_enter=lambda: self.on_ok(None),
            top_w=urwid.AttrMap(urwid.LineBox(layout), "dialog"),
            bottom_w=loop.widget,
            align='center',
            width=40,
            valign='middle',
            height=10
        )

        loop.widget = w

    def on_ok(self, args):
        self.parent.remove_child(self.target)
        self.on_close(self.parent)

    def on_cancel(self, args):
        self.on_close(self.target)


class AddFolderDialog:

    def __init__(self, parent: Node, target: Node, on_close):
        self.parent = parent
        self.target = target
        self.on_close = on_close

        # Form Fields
        self.folder_name = urwid.Edit("Folder Name: ", target.name)

    def show(self, loop):
        # Header
        header_text = urwid.Text('Edit Folder' if self.target.name else "Add Folder", align='center')
        header = urwid.AttrMap(header_text, 'dialog')

        # Footer
        save_btn = urwid.Button('Save', self.on_save)
        save_btn = urwid.AttrWrap(save_btn, 'dialog_button', 'dialog_button_focus')

        cancel_btn = urwid.Button('Cancel', self.on_cancel)
        cancel_btn = urwid.AttrWrap(cancel_btn, 'dialog_button', 'dialog_button_focus')

        footer = urwid.GridFlow([save_btn, cancel_btn], 12, 1, 1, 'center')

        body = urwid.Filler(
            urwid.Pile([self.folder_name, footer])
        )

        # Layout
        layout = urwid.Frame(
            body,
            header=header)

        w = DialogOverlay(
            on_close=lambda: self.on_close(self.target),
            on_enter=self.on_save,
            top_w=urwid.AttrMap(urwid.LineBox(layout), "dialog"),
            bottom_w=loop.widget,
            align='center',
            width=40,
            valign='middle',
            height=10
        )

        loop.widget = w

    def on_save(self, args=None):
        self.target.name = self.folder_name.edit_text
        self.parent.add_child(self.target)
        self.on_close(self.target)

    def on_cancel(self, args):
        self.on_close(self.parent)


class MessageDialog:

    def __init__(self, title, message, on_close):
        self.title = title
        self.message = message
        self.on_close = on_close

    def show(self, loop):
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

        w = DialogOverlay(
            on_close=self.on_close,
            on_enter=self.on_ok,
            top_w=urwid.AttrMap(urwid.LineBox(layout), "dialog"),
            bottom_w=loop.widget,
            align='center',
            width=40,
            valign='middle',
            height=10
        )

        loop.widget = w

    def on_ok(self, args=None):
        self.on_close()


class DialogOverlay(urwid.Overlay):

    def __init__(self, on_close, on_enter, **kwargs):
        self.on_close = on_close
        self.on_enter = on_enter
        super(DialogOverlay, self).__init__(**kwargs)

    def keypress(self, size, key):
        if key == 'shift tab':
            key = 'up'
        elif key == 'tab':
            key = 'down'
        elif key == 'esc':
            self.on_close()
        # TODO: implement, save with "enter"

        super().keypress(size, key)
