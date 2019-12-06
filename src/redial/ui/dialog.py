import os
from os.path import expanduser

import urwid
from redial.hostinfo import HostInfo
from redial.tree.node import Node
from redial.utils import get_public_ssh_keys
from urwid.tests.util import SelectableText


def textbox(markup, label=""):
    return urwid.AttrWrap(urwid.Edit(label, markup, wrap=urwid.widget.CLIP), 'dialog_edit', 'dialog_edit_focus')


# TODO validations
# * special characters
# * identity file exists
class AddHostDialog:

    def __init__(self, parent: Node, target: Node, on_close):
        self.parent = parent
        self.target = target
        self.on_close = on_close

        self.show_advanced = False
        self.loop = None

        # Form Fields
        label_connection_name = urwid.Text("Name")

        self.connection_name = textbox(target.name)

        label_ip = urwid.Text("IP")
        self.ip = textbox(target.hostinfo.ip)

        label_username = urwid.Text("Username")
        self.username = textbox(target.hostinfo.username)

        label_port = urwid.Text("Port")
        self.port = textbox(target.hostinfo.port if self.target.name else "22")

        label_id_file = urwid.Text("Private Key Path")
        self.id_file = textbox(target.hostinfo.identity_file)

        label_dynamic_forward = urwid.Text("Dynamic Forward")
        self.dynamic_forward = textbox(target.hostinfo.dynamic_forward)

        label_local_forward = urwid.Text("Local Forward")
        self.local_forward_from = textbox(target.hostinfo.local_forward[0], "from ")
        self.local_forward_to = textbox(target.hostinfo.local_forward[1], "to ")
        self.local_forward = urwid.Columns([self.local_forward_from, self.local_forward_to])

        label_remote_forward = urwid.Text("Remote Forward")
        self.remote_forward_from = textbox(target.hostinfo.remote_forward[0], "from ")
        self.remote_forward_to = textbox(target.hostinfo.remote_forward[1], "to ")
        self.remote_forward = urwid.Columns([self.remote_forward_from, self.remote_forward_to])

        # Header
        self.header_text = 'Edit Connection' if self.target.name else 'Add Connection'

        # Advanced
        self.advanced_btn = urwid.AttrWrap(urwid.CheckBox('Advanced', False, False, self.on_advanced),
                                           'dialog_button', 'dialog_button_focus')

        # Footer
        save_btn = urwid.AttrWrap(urwid.Button('Save', self.on_save),
                                  'dialog_button', 'dialog_button_focus')

        cancel_btn = urwid.AttrWrap(urwid.Button('Cancel', self.on_cancel),
                                    'dialog_button', 'dialog_button_focus')

        self.footer = urwid.GridFlow([save_btn, cancel_btn], 12, 1, 1, 'center')

        label_pile = urwid.Pile([label_connection_name, label_ip, label_username, label_port])
        edit_pile = urwid.Pile([self.connection_name, self.ip, self.username, self.port])

        advanced_label_pile = urwid.Pile([label_connection_name, label_ip, label_username, label_port, label_id_file,
                                          label_dynamic_forward, label_local_forward, label_remote_forward])
        advanced_edit_pile = urwid.Pile([self.connection_name, self.ip, self.username, self.port, self.id_file,
                                         self.dynamic_forward, self.local_forward, self.remote_forward])

        self.body = urwid.Filler(
            urwid.Pile([
                urwid.Columns([('weight', 1, label_pile), ('weight', 2, edit_pile)]),
                self.advanced_btn,
                self.footer
            ])
        )

        self.advanced_body = urwid.Filler(
            urwid.Pile([
                urwid.Columns([('weight', 1, advanced_label_pile), ('weight', 2, advanced_edit_pile)]),
                self.footer
            ])
        )

    def show(self, loop):
        self.loop = loop
        w = DialogOverlay(
            on_close=lambda: self.on_close(self.parent),
            on_enter=self.on_save,
            top_w=urwid.AttrMap(
                urwid.LineBox(
                    self.advanced_body if self.show_advanced else self.body, self.header_text),
                "dialog"),
            bottom_w=loop.widget,
            align='center',
            width=64,
            valign='middle',
            height=11 if self.show_advanced else 8
        )

        loop.widget = w

    def on_advanced(self, args, user_data):
        self.show_advanced = not self.show_advanced
        self.show(self.loop)

    def on_save(self, args=None):
        host_info = HostInfo(self.connection_name.edit_text)
        host_info.ip = self.ip.edit_text
        host_info.username = self.username.edit_text
        host_info.port = self.port.edit_text
        host_info.identity_file = self.id_file.edit_text
        host_info.dynamic_forward = self.dynamic_forward.edit_text
        host_info.local_forward = (self.local_forward_from.edit_text, self.local_forward_to.edit_text)
        host_info.remote_forward = (self.remote_forward_from.edit_text, self.remote_forward_to.edit_text)

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
