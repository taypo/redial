from os.path import expanduser
from hostinfo import *


def getHosts():
    home = expanduser("~")

    f = open(home + "/.ssh/config")

    hosts = []

    for f_line in f:
        line = f_line.strip()
        if line.startswith('#'):
            continue
        kv = line.split(' ')
        if kv[0].lower() == "host":
            h = HostInfo()
            h.full_name = kv[1]
            split = kv[1].split('/')
            h.name = split[len(split) - 1]
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
