from redial import xdg
from redial.hostinfo import HostInfo
from redial.tree.node import Node
import os, json


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
                kv = list(filter(None, line.split(' ')))

                key = kv[0].lower()  # SSH config file keys are case insensitive

                try:
                    if key == "host":
                        if host_info is not None:
                            hosts.append(host_info)
                        if len(kv) == 1:
                            host_info = None
                        else:
                            host_info = HostInfo(kv[1])
                    if key == "hostname" and host_info:
                        host_info.ip = kv[1]
                    if key == "user" and host_info:
                        host_info.username = kv[1]
                    if key == "port" and host_info:
                        host_info.port = kv[1]
                    if key == "identityfile" and host_info:
                        host_info.identity_file = kv[1]
                    if key == "dynamicforward" and host_info:
                        host_info.dynamic_forward = kv[1]
                    if key == "localforward" and host_info:
                        host_info.local_forward = (kv[1], kv[2])
                    if key == "remoteforward" and host_info:
                        host_info.remote_forward = (kv[1], kv[2])
                except IndexError:
                    continue

            if host_info is not None:
                hosts.append(host_info)

        return Config.__construct_tree(hosts)

    @staticmethod
    def save_to_file(sessions):
        with open(Config.__get_or_create_config_file(), "w") as file:
            Config.__append_node_to_file(sessions, "", file)

    @staticmethod
    def save_state(state: dict):
        with open(Config.__get_or_create_state_file(), "w") as file:
            json.dump(state, file, default=vars, indent=4)

    @staticmethod
    def load_state() -> dict:
        with open(Config.__get_or_create_state_file(), "r") as file:
            try:
                return json.load(file)
            except json.decoder.JSONDecodeError:
                return {}

    # Private Methods
    __CONFIG_PATH = xdg.get_config_dir()
    __CONFIG_FILE = "sessions"
    __STATE_FILE = "state.json"

    @staticmethod
    def __get_or_create_config_file() -> str:
        full_path = Config.__CONFIG_PATH + "/" + Config.__CONFIG_FILE
        if not os.path.isfile(full_path):
            file = open(full_path, "w")
            file.close()
        return full_path

    @staticmethod
    def __get_or_create_state_file() -> str:
        full_path = Config.__CONFIG_PATH + "/" + Config.__STATE_FILE
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
            host = node.hostinfo
            file.write("Host " + session_name + "\n")
            file.write("\tHostName " + host.ip + "\n")

            if host.username:
                file.write("\tUser " + host.username + "\n")

            if host.port:
                file.write("\tPort " + host.port + "\n")

            if host.identity_file:
                file.write("\tIdentityFile " + host.identity_file + "\n")

            if host.dynamic_forward:
                file.write("\tDynamicForward " + host.dynamic_forward + "\n")

            if host.local_forward[0]:
                file.write("\tLocalForward " + host.local_forward[0] + " " + host.local_forward[1] + "\n")

            if host.remote_forward[0]:
                file.write("\tRemoteForward " + host.remote_forward[0] + " " + host.remote_forward[1] + "\n")

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

