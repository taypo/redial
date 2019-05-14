from os.path import expanduser

from redial.hostinfo import *

import os

def read_ssh_config():
    home = expanduser("~")
    hosts = []
    directory = home + "/.ssh/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    if os.path.isfile(directory + "config"):
        with open(directory + "config", "r") as file:
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

    else:
        file = open(directory + "config", "w")
        file.close()

    return hosts


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
