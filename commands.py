import logging
import re
import yaml

class Lvm2OperationCmds:
    def __init__(self):
        self.cmd_list = []
        self.cmd_list_creation()

    def cmd_list_creation(self):
        self.cmd_list.append('apt-get install -y lvm2')
        self.cmd_list.append('apt-cache policy lvm2')

class MainOperationCmds:
    def __init__(self,yaml_info):
        self.primary = yaml_info['disk partition']['primary']
        self.vgsize = yaml_info['basic operation']['vgsize']
        self.lvsize = yaml_info['basic operation']['lvsize']
        self.cmd_list = []
        self.cmd_list_creation()

    def cmd_list_creation(self):
        self.cmd_list.append(f'pvcreate {self.primary}')
        self.cmd_list.append(f'vgcreate vgtest {self.primary}')
        self.cmd_list.append(f'lvcreate -L {self.lvsize} -n lvtest vgtest')
        self.cmd_list.append(f'lvremove -y /dev/vgtest/lvtest')
        self.cmd_list.append(f'vgremove vgtest')
        self.cmd_list.append(f'pvremove {self.primary}')

class ThinOperationCmds:
    def __init__(self,yaml_info):
        self.primary = yaml_info['disk partition']['primary']
        self.thinpoolsize = yaml_info['thin vol']['thinpoolsize']
        self.thinvolsize = yaml_info['thin vol']['thinvolsize']
        self.poolextendsize = yaml_info['thin vol']['poolextendsize']
        self.volextendsize = yaml_info['thin vol']['volextendsize']
        self.volreducesize = yaml_info['thin vol']['volreducesize']
        self.cmd_list = []
        self.cmd_list_creation()

    def cmd_list_creation(self):
        self.cmd_list.append(f'pvcreate {self.primary}')
        self.cmd_list.append(f'vgcreate vgtest {self.primary}')
        self.cmd_list.append(f'lvcreate -L {self.thinpoolsize} --thinpool pooltest vgtest')
        self.cmd_list.append(f'lvcreate -V {self.thinvolsize} --thin -n thin_vol vgtest/pooltest')
        self.cmd_list.append(f'lvextend -L +{self.poolextendsize} vgtest/pooltest')
        self.cmd_list.append(f'lvextend -L +' + self.volextendsize + ' vgtest/thin_vol')
        self.cmd_list.append(f'lvreduce -f -L {self.volreducesize} vgtest/thin_vol')
        self.cmd_list.append(f'lvcreate -L {self.volreducesize} --snapshot --name thin_vol0 vgtest/thin_vol')
        self.cmd_list.append(f'lvremove -y /dev/vgtest/thin_vol0')
        self.cmd_list.append(f'lvremove -y /dev/vgtest/thin_vol')
        self.cmd_list.append(f'lvremove -y /dev/vgtest/pooltest')
        self.cmd_list.append(f'vgremove -y vgtest')

class StripOperationCmds:
    def __init__(self,yaml_info):
        self.stripvolsize = yaml_info['strip vol']['stripvolsize']
        self.stripnumbers = yaml_info['strip vol']['stripnumbers']
        self.stripsize = yaml_info['strip vol']['stripsize']
        self.secondary = yaml_info['disk partition']['secondary']
        self.primary = yaml_info['disk partition']['primary']
        self.cmd_list = []
        self.cmd_list_creation()

    def cmd_list_creation(self):
        self.cmd_list.append(f'pvcreate {self.secondary}')
        self.cmd_list.append(f'vgcreate vgtest {self.primary} {self.secondary}')
        self.cmd_list.append(f'lvcreate -L {self.stripvolsize} -i {self.stripnumbers} -I {self.stripsize} -n lvtest vgtest')
        self.cmd_list.append(f'lvremove -y /dev/vgtest/lvtest')

class MirrorOperationCmds:
    def __init__(self,yaml_info):
        self.secondary = yaml_info['disk partition']['secondary']
        self.primary = yaml_info['disk partition']['primary']
        self.mirrorvolsize = yaml_info['mirror vol']['mirrorvolsize']
        self.datavol = yaml_info['mirror vol']['datavol']
        self.replicavol = yaml_info['mirror vol']['replicavol']
        self.cmd_list = []
        self.cmd_list_creation()

    def cmd_list_creation(self):
        self.cmd_list.append(f'lvcreate -L {self.mirrorvolsize} -m1 -n lvmirror vgtest {self.datavol} {self.replicavol}')
        self.cmd_list.append(f'lvremove -y /dev/vgtest/lvmirror')
        self.cmd_list.append(f'vgremove vgtest')
        self.cmd_list.append(f'pvremove {self.primary}')
        self.cmd_list.append(f'pvremove {self.secondary}')
