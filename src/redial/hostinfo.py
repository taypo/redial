
class HostInfo:
    # TODO rename to name
    full_name = ""
    ip = ""
    port = ""
    username = ""
    identity_file = ""
    dynamic_forward = ""
    local_forward = ("", "")
    remote_forward = ("", "")

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

        if self.identity_file:
            c = c + "-i " + self.identity_file + " "

        if self.dynamic_forward:
            c = c + "-D" + self.dynamic_forward + " "

        if self.local_forward[0]:
            c = c + "-L" + self.local_forward[0] + ":" + self.local_forward[1] + " "

        if self.remote_forward[0]:
            c = c + "-R" + self.remote_forward[0] + ":" + self.remote_forward[1] + " "

        if self.username:
            c = c + self.username + "@"

        c = c + self.ip

        if self.port:
            c = c + " -p " + self.port

        return c

    def get_ssh_copy_command(self, identity_file):
        c = "ssh-copy-id -i {} ".format(identity_file)

        if self.username:
            c = c + self.username + "@"

        c = c + self.ip

        if self.port:
            c = c + " -p " + self.port

        return c
