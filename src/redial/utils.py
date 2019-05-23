from os.path import expanduser

from redial.hostinfo import *


def append_to_config(host: HostInfo):
    content = "\n"
    if host.full_name:
        content += "Host " + host.full_name + "\n"
    if host.ip:
        content += "    hostname " + host.ip + "\n"
    if host.port:
        content += "    port " + host.port + "\n"
    if host.username:
        content += "    user " + host.username + "\n"
                
    home = expanduser("~")
    path = home + "/.ssh/config"
    with open(path, "a+") as file:
        file.write(content)
