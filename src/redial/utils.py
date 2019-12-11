import glob
import os
import shutil
from os.path import expanduser


def package_available(package_name):
    """
    Checks unix package availability
    :param package_name: Unix package name. For example: git, docker, mc
    :return: True if package is available
             False if package is not available
    """

    return True if shutil.which(package_name) is not None else False


def get_public_ssh_keys():
    """
    Gets public (pub) ssh keys from ~/.ssh directory
    :return: list of public key paths
    """
    home = expanduser("~")
    path = os.path.join(home, '.ssh/')
    files = [f for f in glob.glob(path + "**/*.pub", recursive=True)]
    return files
