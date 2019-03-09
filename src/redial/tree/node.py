class Node(object):
    def __init__(self, name, type=None):
        self.name = name
        self.children = []
        self.type = type

    def child(self, cname, type=None):
        child_found = [c for c in self.children if c.name == cname]
        if not child_found:
            _child = Node(cname, type)
            self.children.append(_child)
        else:
            _child = child_found[0]
        return _child

    def as_dict(self):
        res = {'name': self.name}
        if self.type is "folder":
            res['children'] = [c.as_dict() for c in self.children]
            res['type'] = "folder"
        elif self.type is "session":
            res['type'] = "session"
        else:
            res['children'] = [c.as_dict() for c in self.children]
        return res


# path1 = "sub1/grandsub1/file1"
# path2 = "sub1/grandsub1/file1"
# path3 = "sub2/grandsub1/file2/dshasgas"
# path4 = "sub3/grandsub1/file1"
# path5 = "sub3/grandsub2/file1"
#
# configs = [path1, path2, path3, path4, path5]
#
# root = Node('parent')
#
# for config in configs:
#     prev_part = root
#     parts = config.split("/")
#     for part_idx in range(len(parts)):
#         if part_idx == len(parts)-1:
#             part = prev_part.child(parts[part_idx], type="session")
#         else:
#             part = prev_part.child(parts[part_idx], type="folder")
#
#         prev_part = part

# print(root.as_dict())
