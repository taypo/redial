from redial import xdg
from redial.hostinfo import HostInfo
from redial.tree.node import Node
import os


class Config:

    @staticmethod
    def load_from_file():
        hosts = []
        with open(Config.__get_or_create_config_file(), "r") as file:
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

        return Config.__construct_tree(hosts)

    @staticmethod
    def save_to_file( sessions):
        with open(Config.__get_or_create_config_file(), "w") as file:
            Config.__append_node_to_file(sessions, "", file)

    # Private Methods
    __CONFIG_PATH = xdg.get_config_dir()
    __CONFIG_FILE = "sessions"

    @staticmethod
    def __get_or_create_config_file() -> str:
        full_path = Config.__CONFIG_PATH + "/" + Config.__CONFIG_FILE
        if not os.path.isfile(full_path):
            file = open(full_path, "w")
            file.close()
        return full_path

    @staticmethod
    def __append_node_to_file(node: Node, path: str, file):
        path = path.lstrip("/")
        if node.nodetype == "folder":
            for child in node.children:
                sub_path = path + "/" + node.name if (node.name != ".") else ""
                Config.__append_node_to_file(child, sub_path, file)
        else:
            session_name = (path + "/" + node.name).lstrip("/")
            file.write("Host " + session_name + "\n")
            file.write("\thostname " + node.hostinfo.ip + "\n")
            file.write("\tuser " + node.hostinfo.username + "\n")
            file.write("\tport " + node.hostinfo.port + "\n")
            file.write("\n")

    @staticmethod
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

