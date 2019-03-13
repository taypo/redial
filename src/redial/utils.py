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
            for f_line in file:
                line = f_line.strip()
                if line.startswith('#'):
                    continue
                kv = line.split(' ')
                h = HostInfo()
                if kv[0].lower() == "host":
                    h.full_name = kv[1]
                    split = kv[1].split('/')
                    h.name = split[len(split) - 1]
                    hosts.append(h)
                
    else:
        file = open(directory + "config", "w")
        file.close()

    return hosts


def append_to_config(answers):
    if len(answers) == 4:
        content = "\nHost " + answers[0] + "\n" + "hostname " + answers[1] + "\n" + "user " + answers[2] + "\n" + "port " + answers[3] + "\n\n"
                
        home = expanduser("~")
        path = home + "/.ssh/config"
        with open(path, "a+") as file:
            file.write(content)
    else:
        print("Connection is not saved!")
