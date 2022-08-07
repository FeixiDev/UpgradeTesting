import yaml
import logging
import re
import paramiko
import subprocess


def yaml_read():
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    return config

def install_lvm2(ssh_obj):
    install_cmd = "apt-get install -y lvm2"
    ssh_obj.obj_SSHClient.exec_command(install_cmd)
    check_cmd = 'apt-cache policy lvm2'
    stdin, stdout, stderr = ssh_obj.obj_SSHClient.exec_command(check_cmd)
    result = (str(stdout.read(),encoding='utf-8'))
    a = re.findall(r'Installed: ([\w\W]*) Candidate', result)
    b = a[0]
    b = b.strip('\n')
    b = b.strip(' ')
    if b == '2.03.11-2.1ubuntu4':
        print('Lvm2 installation succeeded')
    else:
        print('Lvm2 version error')


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
    def __init__(self,obj_ssh):
        self.primaly = yaml_info['disk partition']['primary']
        self.vgname = 'vgtest'
        self.lvname = 'lvtest'
        self.vgsize = yaml_info['basic operation']['vgsize']
        self.lvsize = yaml_info['basic operation']['lvsize']
        self.obj_ssh = obj_ssh

    def pv_operation(self):
        status = False
        pvcreate_cmd = f'pvcreate {self.primaly}'
        stdin,stdout,stderr = self.obj_ssh.obj_SSHClient.exec_command(pvcreate_cmd)
        info = str(stdout.read(),encoding='utf-8')
        a = re.findall(r'Physical volume “'+self.primaly+'” successfully created',info)
        if a:
            print('pvcreate successfully')
        else:
            print('pvcreate failed')
        pvdisplay_cmd = f'pvdisplay {self.primaly}'
        stdin,stdout,stderr = self.obj_ssh.obj_SSHClient.exec_command(pvdisplay_cmd)
        info2 = str(stdout.read(),encoding='utf-8')
        b = re.findall(r'PV Name  '+self.primaly,info2)
        c = re.findall(r'PV Size  '+self.vgsize+'GiB',info2)
        if b and c:
            print('pvdisplay information is correct')
            status = True
        else:
            print('pvdisplay information error')

        return status

    def vg_operation(self,obj_ssh):
        status = False
        pvcreate_cmd = f'vgcreate vgtest {self.primaly}'
        stdin,stdout,stderr = self.obj_ssh.obj_SSHClient.exec_command(pvcreate_cmd)
        info = str(stdout.read(),encoding='utf-8')
        a = re.findall(r'Volume group “vgtest” successfully created',info)
        if a:
            print('vgcreate successfully')
        else:
            print('vgcreate failed')
        pvdisplay_cmd = f'vgdisplay vgtest'
        stdin,stdout,stderr = self.obj_ssh.obj_SSHClient.exec_command(pvdisplay_cmd)
        info2 = str(stdout.read(),encoding='utf-8')
        b = re.findall(r'PV Name  '+self.primaly,info2)
        c = re.findall(r'PV Size  '+self.vgsize,info2)
        if b and c:
            print('vgdisplay information is correct')
            status = True
        else:
            print('vgdisplay information error')

        return status

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
    yaml_info = yaml_read()
    main()