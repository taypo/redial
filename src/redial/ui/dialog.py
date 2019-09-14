import os
from os.path import expanduser

import urwid
from redial.hostinfo import HostInfo
from redial.tree.node import Node
from redial.utils import get_public_ssh_keys
from urwid.tests.util import SelectableText


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


class SSHListBox(urwid.ListBox):
    def __init__(self, on_enter, **kwargs):
        self.on_enter = on_enter
        super(SSHListBox, self).__init__(**kwargs)

    def keypress(self, size, key):
        if key == "enter":
            self.on_enter()
        else:
            return super(SSHListBox, self).keypress(size, key)


class CopySSHKeyDialog:

    def __init__(self, target: Node, on_close):
        self.target = target
        self.on_close = on_close

        # Form Fields
        self.ssh_keys_walker = urwid.SimpleListWalker(
            self.prepare_ssh_list_elements()
        )

    def show(self, loop):
        # Header
        header_text = urwid.Text('Select Public SSH Key to Copy', align='center')
        header = urwid.AttrMap(header_text, 'dialog')

        cancel_btn = urwid.Button('Cancel', self.on_cancel)
        cancel_btn = urwid.AttrWrap(cancel_btn, 'dialog_button', 'dialog_button_focus')

        footer = urwid.GridFlow([cancel_btn], 12, 1, 1, 'center')

        list_box = urwid.BoxAdapter(SSHListBox(on_enter=self.on_copy, body=self.ssh_keys_walker), 5)

        body = urwid.Filler(
            urwid.Pile([list_box, footer])
        )

        # Layout
        layout = urwid.Frame(
            body=body,
            header=header)

        layout = urwid.AttrWrap(layout, 'dialog')

        w = DialogOverlay(
            on_close=lambda: self.on_close(),
            on_enter=self.on_copy,
            top_w=urwid.AttrMap(urwid.LineBox(layout), "dialog"),
            bottom_w=loop.widget,
            align='center',
            width=40,
            valign='middle',
            height=10
        )

        loop.widget = w

    def on_copy(self, args=None):
        ssh_files_path = os.path.join(expanduser("~"), '.ssh/')
        selected_ssh_key = os.path.join(ssh_files_path, self.ssh_keys_walker.get_focus()[0].original_widget.text)
        command = self.target.hostinfo.get_ssh_copy_command(selected_ssh_key)
        self.on_close(command)

    def on_cancel(self, args):
        self.on_close()

    def prepare_ssh_list_elements(self):
        ssh_keys = []
        for key in get_public_ssh_keys():
            ssh_keys.append(urwid.AttrWrap(SelectableText(os.path.basename(key)), 'ssh_copy', 'ssh_copy_focus'))
        return ssh_keys


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
