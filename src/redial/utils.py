import shutil


def package_available(package_name):
    """
    Checks unix package availability
    :param package_name: Unix package name. For example: git, docker, mc
    :return: True if package is available
             False if package is not available
    """

    return True if shutil.which(package_name) is not None else False
