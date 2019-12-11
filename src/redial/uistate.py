from redial.config import Config
from redial.ui.tree import UITreeListBox, UITreeNode, UIParentNode

SELECTED = "selected"
COLLAPSED = "collapsed"


# todo do we really need sessions here
def restore_ui_state(listbox: UITreeListBox, sessions):
    ui_state = Config().load_state()

    if SELECTED in ui_state:
        selected = ui_state[SELECTED]
        node = find_node(sessions, selected[1:])
        listbox.set_focus_to_node(node)

    if COLLAPSED in ui_state:
        collapsed = ui_state[COLLAPSED]
        for c in collapsed:
            node = find_node(sessions, c[1:])
            listbox.collapse_node(node)


def save_ui_state(listbox: UITreeListBox):
    ui_state = dict()
    ui_state[SELECTED] = get_path(listbox.get_focus_path()[0])

    parent: UIParentNode = listbox.focus.get_node().get_root()
    ui_state[COLLAPSED] = find_collapsed(parent._children)  # todo can we avoid this

    Config().save_state(ui_state)


def find_node(node_tree: list, path: list):
    if len(path) == 0:
        return node_tree
    for node in node_tree.children:
        if node.name == path[0]:
            return find_node(node, path[1:])


def find_collapsed(nodes):
    collapsed = []
    for key in nodes:
        node = nodes[key]
        if isinstance(node, UITreeNode):
            continue
        collapsed.extend(find_collapsed(node._children))
        if node.get_widget().expanded is False:
            collapsed.append(get_path(node))
    return collapsed


def get_path(node: UITreeNode) -> list:
    path = []

    while node:
        path.append(node.get_value().name)
        node = node.get_parent()

    path.reverse()
    return path
