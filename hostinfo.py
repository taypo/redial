class Node:
    name = ""


class Folder(Node):
    children = []


class HostInfo(Node):
    full_name = ""
    ip = ""
    port = ""
    username = ""
