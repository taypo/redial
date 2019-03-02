from os.path import expanduser

from hostinfo import *


def read_ssh_config():
    home = expanduser("~")
    f = open(home + "/.ssh/config")
    hosts = []

    for f_line in f:
        line = f_line.strip()
        if line.startswith('#'):
            continue
        kv = line.split(' ')
        h = HostInfo()
        if kv[0].lower() == "host":
            h.full_name = kv[1]
            split = kv[1].split('/')
            h.name = split[len(split) - 1]
        elif kv[0].lower() == "hostname":
            h.ip = kv[1]
        hosts.append(h)

    # root = Folder()
    #
    # for h in hosts:
    #     s = h.full_name.split('/')
    #     if(len(s) == 1):
    #         root.children.append(h)
    #     else:
    #
    #
    # for h in hosts:
    #     print h.full_name + ":--------:" + h.name

    f.close()
    return hosts
