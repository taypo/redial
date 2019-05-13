import urwid

from redial.utils import append_to_config

def add_host_dialog(parent):
    # Header
    header_text = urwid.Text(('banner', 'Help'), align='center')
    header = urwid.AttrMap(header_text, 'banner')

    # Body
    body_text = urwid.Text("Deneme", align='center')
    body_filler = urwid.Filler(body_text, valign='top')
    body_padding = urwid.Padding(
        body_filler,
        left=1,
        right=1
    )
    body = urwid.LineBox(body_padding)

    # Footer
    footer = urwid.Button('Okay', parent.reset_layout)
    footer = urwid.AttrWrap(footer, 'selectable', 'focus')
    footer = urwid.GridFlow([footer], 8, 1, 1, 'center')

    # Layout
    layout = urwid.Frame(
        body,
        header=header,
        footer=footer,
        focus_part='footer'
    )

    w = urwid.Overlay(
        urwid.LineBox(layout),
        parent.body,
        align='center',
        width=40,
        valign='middle',
        height=10
    )

    parent.loop.widget = w
