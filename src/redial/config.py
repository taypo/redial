from redial.hostinfo import HostInfo
from redial.tree.node import Node
import os


def load_session_config() -> Node:
    hosts = []
    with open(__get_or_create_config_file(), "r") as file:
        host_info = None
        for f_line in file:
            line = f_line.strip()
            if line.startswith('#') or not line:
                continue
            kv = line.split(' ')

            key = kv[0].lower()
            value = kv[1]

            if key == "host":
                if host_info is not None:
                    hosts.append(host_info)

                host_info = HostInfo(value)
            if key == "hostname":
                host_info.ip = value
            if key == "user":
                host_info.username = value
            if key == "port":
                host_info.port = value

        if host_info is not None:
            hosts.append(host_info)

    return __construct_tree(hosts)


def save_session_config(sessions: Node):
    with open(__get_or_create_config_file(), "w") as file:
        __append_node_to_file(sessions, file)


# Private Methods
__CONFIG_PATH = ".ssh/"
__CONFIG_FILE = "config"


def __get_or_create_config_file() -> str:
    home = os.path.expanduser("~")
    directory = home + "/" + __CONFIG_PATH
    if not os.path.exists(directory):
        os.makedirs(directory)
    full_path = directory + __CONFIG_FILE
    if not os.path.isfile(full_path):
        file = open(full_path, "w")
        file.close()
    return full_path


def __append_node_to_file(node: Node, file):
    if node.nodetype == "folder":
        for child in node.children:
            __append_node_to_file(child, file)
    else:
        file.write("Host " + node.hostinfo.full_name + "\n")
        file.write("\thostname " + node.hostinfo.ip + "\n")
        file.write("\tuser " + node.hostinfo.username + "\n")
        file.write("\tport " + node.hostinfo.port + "\n")
        file.write("\n")


def __construct_tree(hosts):
    root = Node('.')

    for host in hosts:
        prev_part = root
        parts = host.full_name.split("/")
        for part_idx in range(len(parts)):
            if part_idx == len(parts) - 1:
                part = prev_part.add_child(Node(parts[part_idx], "session", host))
            else:
                part = prev_part.add_child(Node(parts[part_idx]))

            prev_part = part

    return root
