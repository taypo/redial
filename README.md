# redial

redial is a simple shell application that manages your SSH sessions.

![redial](https://github.com/taypo/redial/blob/master/doc/redial.png?raw=true)

## Installation

### Requirements
- Python 3 or later to run redial.
- [mc (Midnight Commadder)](https://midnight-commander.org/) to use `F5 (Browse)` feature.

### Stable Version

#### Installing via pip

We recommend installing redial via pip:

```bash
pip3 install redial
``` 

### Latest Version

#### Installing from Git

You can install the latest version from Git:

```bash
pip3 install git+https://github.com/taypo/redial.git
```

## Features
- [x] Manage your connections in folders/groups
- [x] Open a file manager to your remote host (Midnight Commander should be installed)
- [x] Edit/Move/Delete connection
- [ ] Copy SSH Key to remote host

More features coming soon..

### Add Folder (F6)

Type `F6` or click `F6 New Folder` to add a folder. There must be at least
one connection under the folder. 

![add_folder_gif](/gifs/add_folder.gif)

### Add Connection (F7)

Type `F7` or click `F7 New Conn.` to add a ssh connection. 

![add_conn_gif](/gifs/add_connection.gif)

### Add Connection (F5)

Type `F5` or click `F5 Browse` to open mc (Midnight Commander) session. 

![mc_gif](/gifs/mc.gif)

## License

redial is licensed under the [GNU General Public License v3.0](LICENSE).