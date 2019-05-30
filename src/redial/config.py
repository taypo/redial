from redial.hostinfo import HostInfo
from redial.tree.node import Node
import os


class Config:
    def __init__(self):
        self.sessions = Node(".")
        self.load_from_file()

    def load_from_file(self):
        hosts = []
        with open(self.__get_or_create_config_file(), "r") as file:
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

        self.sessions = self.__construct_tree(hosts)

    def save_to_file(self):
        with open(self.__get_or_create_config_file(), "w") as file:
            self.__append_node_to_file(self.sessions, "", file)

    def get_sessions(self) -> Node:
        return self.sessions

    def add_node(self, parent: Node, node: Node):
        parent.add_child(node)
        self.save_to_file()

    def delete_node(self, parent: Node, node: Node):
        parent.remove_child(node)
        self.save_to_file()

    # Private Methods
    __CONFIG_PATH = ".ssh/"
    __CONFIG_FILE = "config"

    def __get_or_create_config_file(self) -> str:
        home = os.path.expanduser("~")
        directory = home + "/" + self.__CONFIG_PATH
        if not os.path.exists(directory):
            os.makedirs(directory)
        full_path = directory + self.__CONFIG_FILE
        if not os.path.isfile(full_path):
            file = open(full_path, "w")
            file.close()
        return full_path

    def __append_node_to_file(self, node: Node, path: str, file):
        path = path.lstrip("/")
        if node.nodetype == "folder":
            for child in node.children:
                sub_path = path + "/" + node.name if (node.name != ".") else ""
                self.__append_node_to_file(child, sub_path, file)
        else:
            session_name = (path + "/" + node.name).lstrip("/")
            file.write("Host " + session_name + "\n")
            file.write("\thostname " + node.hostinfo.ip + "\n")
            file.write("\tuser " + node.hostinfo.username + "\n")
            file.write("\tport " + node.hostinfo.port + "\n")
            file.write("\n")

    def __construct_tree(self, hosts):
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

