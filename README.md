# redial

[![Build Status](https://img.shields.io/pypi/pyversions/redial.svg)](https://pypi.org/project/redial/)
[![License](https://img.shields.io/github/license/taypo/redial)](LICENSE)
[![Version](https://img.shields.io/pypi/v/redial)](https://pypi.org/project/redial/)

redial is a simple shell application that manages your SSH sessions on Unix terminal.

![redial](https://github.com/taypo/redial/blob/master/doc/redial.png?raw=true)

## Installation

### Requirements
- Python 3 or later to run redial.
- [mc (Midnight Commander)](https://midnight-commander.org/) to use `F5 (Browse)` feature.

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

### Docker

[Dockerfile](Dockerfile) is provided. 

#### Build Dockerfile:

```bash
docker build -t redial .
```

#### Run redial in Docker Container

```bash
docker run -it --rm redial:latest redial
```

## Features
- [x] Manage your connections in folders/groups
- [x] Open a file manager to your remote host (Midnight Commander should be installed)
- [x] Edit/Move/Delete connection
- [x] Copy SSH Key to remote host

More features coming soon..

### Connect to SSH Session (ENTER)

Press `ENTER` to connect a SSH session.

![connect_gif](https://raw.githubusercontent.com/taypo/redial/master/doc/connect.gif)

### Add Folder (F6)

Press `F6` or click `F6 New Folder` to add a folder. There must be at least
one connection under the folder. 

![add_folder_gif](https://raw.githubusercontent.com/taypo/redial/master/doc/add_folder.gif)

### Add Connection (F7)

Press `F7` or click `F7 New Conn.` to add a ssh connection. 

![add_conn_gif](https://raw.githubusercontent.com/taypo/redial/master/doc/add_connection.gif)

### Browse over mc (F5)

Press `F5` or click `F5 Browse` to open mc (Midnight Commander) session. 

![mc_gif](https://raw.githubusercontent.com/taypo/redial/master/doc/mc.gif)

### Remove Connection (F8)

Press `F8` or click `F8 Remove` to remove a session. 

![remove_gif](https://raw.githubusercontent.com/taypo/redial/master/doc/remove.gif)

### Edit Connection (F9)

Press `F9` or click `F9 Edit` to edit a session. 

![edit_gif](https://raw.githubusercontent.com/taypo/redial/master/doc/edit.gif)


### Move sessions and folders

Press `CTRL` and `up/down` keys to move session or folder. **For macOS users:** Use `ALT` and `up/down` keys.

![move_gif](https://raw.githubusercontent.com/taypo/redial/master/doc/move.gif)

## Notes

Configuration file is stored in `~/.config/redial/sessions`. File format
is same as the [SSH config](https://man.openbsd.org/ssh_config) file. Configuration file can be included in
SSH config file with the following way (Make sure that `~/.ssh/config` file exists): 

```bash
sed -i -e '1iInclude ~/.config/redial/sessions' ~/.ssh/config
```

## Platforms

- Linux
- macOS

Windows is currently not supported.

## License

redial is licensed under the [GNU General Public License v3.0](LICENSE).
