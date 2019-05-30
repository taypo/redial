
class HostInfo:
    # TODO rename to name
    full_name = ""
    ip = ""
    port = ""
    username = ""

    def __init__(self, full_name):
        self.full_name = full_name

    def get_mc_command(self):
        c = "mc . sh://"

        if self.username:
            c = c + self.username + "@"

        c = c + self.ip

        if self.port:
            c = c + ":" + self.port

        if self.username:
            c = c + "/home/" + self.username

        return c

    def get_ssh_command(self):
        c = "ssh "

        if self.username:
            c = c + self.username + "@"

        c = c + self.ip

        if self.port:
            c = c + " -p " + self.port

        return c
