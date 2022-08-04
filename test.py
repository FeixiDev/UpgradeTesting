import yaml
import logging
import re
import paramiko


def yaml_read():
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    return config

def install_lvm2(ssh_obj):
    pass

class Ssh():
    def __init__(self, ip, password):
        self.ip = ip
        self.port = 22
        self.username = 'root'
        self.password = password
        self.obj_SSHClient = paramiko.SSHClient()
        self.connect()

    def connect(self):
        try:
            self.obj_SSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.obj_SSHClient.connect(hostname=self.ip,
                                       port=self.port,
                                       username=self.username,
                                       password=self.password, )
        except:
            print("SSH connection failed,please check the hostname or password")

    def close(self):
        self.obj_SSHClient.close()


class Mainoperation():
    def __init__(self):
        self.primaly = a
        self.secondary = a
        self.pvname = a
        self.vgname = a
        self.lvname = a
        self.vgsize = a
        self.lvsize = a

    def pv_operation(self,obj_ssh):
        pass
        # return status

    def vg_operation(self,obj_ssh):
        pass
        # return status

    def lv_operation(self,obj_ssh):
        pass
        # return status

    def delete_operation(self,obj_ssh):
        pass
        # return status

class ThinOperation():
    def __init__(self):
        self.thinpoolname = a
        self.thinpoolsize = a
        self.thinvolname = a
        self.thinvolsize = a
        self.poolextendsize = a
        self.volextendsize = a
        self.volreducesize = a
        self.snapshotname = a

    def thinpool_create(self,obj_ssh):
        pass
        # return status

    def thinvol_create(self,obj_ssh):
        pass
        # return status

    def extend_operation(self,obj_ssh):
        pass
        # return status

    def reduce_operation(self,obj_ssh):
        pass
        # return status

    def snapshot_create(self,obj_ssh):
        pass
        # return status

    def delete_operation(self,obj_ssh):
        pass
        # return status

class StripOperation():
    def __init__(self):
        self.stripvolname = a
        self.stripvolsize = a
        self.stripnumbers = a
        self.stripsize = a

    def stripvol_create(self,obj_ssh):
        pass
        # return status

    def delete_operation(self,obj_ssh):
        pass
        # return status

class MirrorOperation():
    def __init__(self):
        self.mirrorvolname = a
        self.mirrorvolsize = a
        self.datavol = a
        self.replicavol = a

    def mirrorvol_create(self,obj_ssh):
        pass
        # return status

    def delete_operation(self,obj_ssh):
        pass
        # return status

def main():
    ip = a['node']['ip']
    passwd = a['node']['password']

    ssh_obj = Ssh(ip,passwd)
    main_operation_obj = Mainoperation()
    thin_operation_obj = ThinOperation()
    strip_operation_obj = StripOperation()
    mirror_operation_obj = MirrorOperation()

    step1 = install_lvm2(ssh_obj)
    step2 = main_operation_obj.pv_operation(ssh_obj)
    step3 = main_operation_obj.vg_operation(ssh_obj)
    step4 = main_operation_obj.lv_operation(ssh_obj)
    step5 = main_operation_obj.delete_operation(ssh_obj)
    step6 = thin_operation_obj.thinpool_create(ssh_obj)
    step7 = thin_operation_obj.thinvol_create(ssh_obj)
    step8 = thin_operation_obj.extend_operation(ssh_obj)
    step9 = thin_operation_obj.reduce_operation(ssh_obj)
    step10 = thin_operation_obj.snapshot_create(ssh_obj)
    step11 = thin_operation_obj.delete_operation(ssh_obj)
    step12 = strip_operation_obj.stripvol_create(ssh_obj)
    step13 = strip_operation_obj.delete_operation(ssh_obj)
    step14 = mirror_operation_obj.mirrorvol_create(ssh_obj)
    step15 = mirror_operation_obj.delete_operation(ssh_obj)


if __name__ == "__main__":
    a = yaml_read()
    main()