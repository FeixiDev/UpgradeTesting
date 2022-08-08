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
        self.primary = yaml_info['disk partition']['primary']
        self.vgsize = yaml_info['basic operation']['vgsize']
        self.lvsize = yaml_info['basic operation']['lvsize']
        self.obj_ssh = obj_ssh

    def pv_operation(self):
        status = False
        pvcreate_cmd = f'pvcreate {self.primary}'
        stdin,stdout,stderr = self.obj_ssh.obj_SSHClient.exec_command(pvcreate_cmd)
        info = str(stdout.read(),encoding='utf-8')
        a = re.findall(r'Physical volume “'+self.primary+'” successfully created',info)
        if a:
            print('pvcreate successfully')
        else:
            print('pvcreate failed')
        pvdisplay_cmd = f'pvdisplay {self.primary}'
        stdin,stdout,stderr = self.obj_ssh.obj_SSHClient.exec_command(pvdisplay_cmd)
        info2 = str(stdout.read(),encoding='utf-8')
        b = re.findall(r'PV Name\s*'+self.primary,info2)
        if b :
            print('pvdisplay information is correct')
            status = True
        else:
            print('pvdisplay information error')

        return status

    def vg_operation(self):
        status = False
        vgcreate_cmd = f'vgcreate vgtest {self.primary}'
        stdin,stdout,stderr = self.obj_ssh.obj_SSHClient.exec_command(vgcreate_cmd)
        info = str(stdout.read(),encoding='utf-8')
        a = re.findall(r'Volume group “vgtest” successfully created',info)
        if a:
            print('vgcreate successfully')
        else:
            print('vgcreate failed')
        vgdisplay_cmd = f'vgdisplay vgtest'
        stdin,stdout,stderr = self.obj_ssh.obj_SSHClient.exec_command(vgdisplay_cmd)
        info2 = str(stdout.read(),encoding='utf-8')
        b = re.findall(r'VG Name\s*vgtest',info2)
        if b :
            print('vgdisplay information is correct')
            status = True
        else:
            print('vgdisplay information error')

        return status

    def lv_operation(self):
        status = False
        lvcreate_cmd = f'lvcreate -L {self.lvsize} -n lvtest vgtest'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(lvcreate_cmd)
        info = str(stdout.read(), encoding='utf-8')
        a = re.findall(r'Logical volume “lvtest” created', info)
        if a:
            print('lvcreate successfully')
        else:
            print('lvcreate failed')
        lvdisplay_cmd = f'lvdisply /dev/vgtest/lvtest'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(lvdisplay_cmd)
        info2 = str(stdout.read(), encoding='utf-8')
        b = re.findall(r'LV Name\s*lvest', info2)
        if b:
            print('lvdisplay information is correct')
            status = True
        else:
            print('lvdisplay information error')

        return status

    def delete_operation(self):
        status = False
        lvremove_cmd = f'lvremove -y /dev/vgtest/lvtest'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(lvremove_cmd)
        info = str(stdout.read(), encoding='utf-8')
        a = re.findall(r'Logical volume “lvtest” successfully removed', info)
        if a:
            print('lvremove successfully')
            status = True
        else:
            print('lvremove failed')
            status = False

        if status is True:
            vgremove_cmd = f'vgremove vgtest'
            stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(vgremove_cmd)
            info = str(stdout.read(), encoding='utf-8')
            b = re.findall(r'Volume group “vgtest” successfully removed', info)
            if b:
                print('vgremove successfully')
                status = True
            else:
                print('vgremove failed')
                status = False

            if status is True:
                pvremove_cmd = f'pvremove {self.primary}'
                stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(pvremove_cmd)
                info = str(stdout.read(), encoding='utf-8')
                c = re.findall(r'Labels on physical volume “'+self.primary+'” successfully wiped', info)
                if c:
                    print('pvremove successfully')
                    status = True
                    return status
                else:
                    print('pvremove failed')
                    status = False
                    return status
            else:
                return status
        else:
            return status

class ThinOperation():
    def __init__(self,obj_ssh):
        self.primary = yaml_info['disk partition']['primary']
        self.thinpoolsize = yaml_info['thin vol']['thinpoolsize']
        self.thinvolsize = yaml_info['thin vol']['thinvolsize']
        self.poolextendsize = yaml_info['thin vol']['poolextendsize']
        self.volextendsize = yaml_info['thin vol']['volextendsize']
        self.volreducesize = yaml_info['thin vol']['volreducesize']
        self.obj_ssh = obj_ssh

    def thinpool_create(self):
        status = False
        pvcreate_cmd = f'pvcreate {self.primary}'
        stdin,stdout,stderr = self.obj_ssh.obj_SSHClient.exec_command(pvcreate_cmd)
        info = str(stdout.read(),encoding='utf-8')
        a = re.findall(r'Physical volume “'+self.primary+'” successfully created',info)
        if a:
            print('pvcreate successfully')
        else:
            print('pvcreate failed')
        pvdisplay_cmd = f'pvdisplay {self.primary}'
        stdin,stdout,stderr = self.obj_ssh.obj_SSHClient.exec_command(pvdisplay_cmd)
        info2 = str(stdout.read(),encoding='utf-8')
        b = re.findall(r'PV Name\s*'+self.primary,info2)
        if b :
            print('pvdisplay information is correct')
            status = True
        else:
            print('pvdisplay information error')
            status = False

        if status is True:
            vgcreate_cmd = f'vgcreate vgtest {self.primary}'
            stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(vgcreate_cmd)
            info = str(stdout.read(), encoding='utf-8')
            c = re.findall(r'Volume group “vgtest” successfully created', info)
            if c:
                print('vgcreate successfully')
            else:
                print('vgcreate failed')
            vgdisplay_cmd = f'vgdisplay vgtest'
            stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(vgdisplay_cmd)
            info2 = str(stdout.read(), encoding='utf-8')
            d = re.findall(r'VG Name\s*vgtest', info2)
            if d:
                print('vgdisplay information is correct')
                status = True
            else:
                print('vgdisplay information error')
                status = False

            if status is True:
                poolcreate_cmd = f'lvcreate -L {self.thinpoolsize} --thinpool pooltest vgtest'
                stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(poolcreate_cmd)
                info = str(stdout.read(), encoding='utf-8')
                e = re.findall(r'Logical volume "pooltest" created', info)
                if e:
                    print('thinpool create successfully')
                else:
                    print('thinpool create failed')
                thinpooldisplay_cmd = f'vgdisplay vgtest'
                stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinpooldisplay_cmd)
                info2 = str(stdout.read(), encoding='utf-8')
                f = re.findall(r'LV Name\s*vgtest', info2)
                g = re.findall(r'LV pool data\s*pooltest_tdata',info2)
                if f and g:
                    print('vgdisplay information is correct')
                    status = True
                    return status
                else:
                    print('vgdisplay information error')
                    status = False
                    return status
            else:
                return status
        else:
            return status

    def thinvol_create(self):
        status = False
        thinvolcreate_cmd = f'lvcreate -V {self.thinvolsize} --thin -n thin_vol vgtest/pooltest'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinvolcreate_cmd)
        info = str(stdout.read(), encoding='utf-8')
        h = re.findall(r'Logical volume "thin_vol" created', info)
        if h:
            print('thinvol create successfully')
        else:
            print('thinvol create failed')
        thinvoldisplay_cmd = f'vgdisplay /dev/vgtest/thin_vol'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinvoldisplay_cmd)
        info2 = str(stdout.read(), encoding='utf-8')
        f = re.findall(r'LV Name\s*thin_vol', info2)
        if f:
            print('lvdisplay information is correct')
            status = True
            return status
        else:
            print('lvdisplay information error')
            status = False
            return status

    def extend_operation(self):
        status = False
        thinpoolextend_cmd = f'lvextend -L +{self.poolextendsize} vgtest/pooltest'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinpoolextend_cmd)
        info = str(stdout.read(), encoding='utf-8')
        i = re.findall(r'Logical volume vgtest/pooltest_tdata successfully resized', info)
        if i:
            print('thinvol create successfully')
            status = True
        else:
            print('thinvol create failed')
            status = False
        if status is True:
            thinpoolcheck_cmd = 'display /dev/vgtest/pooltest'
            stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinpoolcheck_cmd)
            info = str(stdout.read(), encoding='utf-8')
            after_extend = str(int(self.thinpoolsize.replace(self.thinpoolsize[-1], '')) + int(self.poolextendsize.replace(self.poolextendsize[-1], '')))
            j = re.findall(r'LV Size\s*'+after_extend, info)
            if j:
                print('thinpool extend successfully')
                status = True
            else:
                print('thinpool extend failed')
                status = False
            if status is True:
                thinvolextend_cmd = f'lvextend -L +'+self.volextendsize+' vgtest/thin_vol'
                stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinvolextend_cmd)
                info = str(stdout.read(), encoding='utf-8')
                i = re.findall(r'Logical volume vgtest/thin_vol successfully resized', info)
                if i:
                    print('thinvol extend successfully')
                    status = True
                else:
                    print('thinvol extend failed')
                    status = False
                if status is True:
                    thinvolcheck_cmd = 'lvdisplay /dev/vgtest/thin_vol'
                    stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinvolcheck_cmd)
                    info = str(stdout.read(), encoding='utf-8')
                    after_extend = str(int(self.thinvolsize.replace(self.thinvolsize[-1], '')) + int(
                        self.volextendsize.replace(self.volextendsize[-1], '')))
                    j = re.findall(r'LV Size\s*' + after_extend, info)
                    if j:
                        print('thinvol extend successfully')
                        status = True
                    else:
                        print('thinvol extend failed')
                        status = False
                else:
                    return status
            else:
                return status
        else:
            return status

    def reduce_operation(self):
        status = False
        thinpoolreduce_cmd = f'lvreduce -f -L {self.volreducesize} vgtest/thin_vol'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinpoolreduce_cmd)
        info = str(stdout.read(), encoding='utf-8')
        k = re.findall(r'Logical volume vgtest/thin_vol successfully resized', info)
        if k:
            print('thinvol reduce successfully')
        else:
            print('thinvol reduce failed')
        thinpoolreducecheck_cmd = f'lvdisplay /dev/vgtest/thin_vol'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinpoolreducecheck_cmd)
        info = str(stdout.read(), encoding='utf-8')
        l = re.findall(r'LV Size\s*' + self.volreducesize, info)
        if l:
            print('thinvol reduce successfully')
            status = True
        else:
            print('thinvol reduce failed')
            status = False
        return status


    def snapshot_create(self):
        status = False
        thinpoolreduce_cmd = f'lvcreate -L {self.volreducesize} –-snapshot –-name thin_vol0 vgtest/thin_vol'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinpoolreduce_cmd)
        info = str(stdout.read(), encoding='utf-8')
        m = re.findall(r'Logical volume “thin_vol0” created', info)
        if m:
            print('thinvol_snapshot create successfully')
        else:
            print('thinvol_snapshot create failed')
        thinvol_snapshot_check_cmd = f'lvdisplay /dev/vgtest/thin_vol0'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinvol_snapshot_check_cmd)
        info = str(stdout.read(), encoding='utf-8')
        n = re.findall(r'LV Size\s*' + self.volreducesize, info)
        if n:
            print('thinvol_snapshot create successfully')
            status = True
        else:
            print('thinvol_snapshot create failed')
            status = False
        return status

    def delete_operation(self):
        thinvol_snapshotremove_cmd = f'lvremove -y /dev/vgtest/thin_vol0'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinvol_snapshotremove_cmd)
        info = str(stdout.read(), encoding='utf-8')
        a = re.findall(r'Logical volume “thin_vol0” successfully removed', info)
        if a:
            print('thin_vol0_snapshot remove successfully')
            status = True
        else:
            print('thin_vol0_snapshot remove failed')
            status = False
        if status is True:
            thinvol_remove_cmd = f'lvremove -y /dev/vgtest/thin_vol'
            stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinvol_remove_cmd)
            info = str(stdout.read(), encoding='utf-8')
            b = re.findall(r'Logical volume “thin_vol” successfully removed', info)
            if b:
                print('thin_vol0_snapshot remove successfully')
                status = True
            else:
                print('thin_vol0_snapshot remove failed')
                status = False
            if status is True:
                thinpool_remove_cmd = f'lvremove -y /dev/vgtest/pooltest'
                stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinpool_remove_cmd)
                info = str(stdout.read(), encoding='utf-8')
                b = re.findall(r'Logical volume “pooltest” successfully removed', info)
                if b:
                    print('thin_pool remove successfully')
                    status = True
                else:
                    print('thin_pool remove failed')
                    status = False
                if status is True:
                    vgremove_cmd = f'vgremove -y vgtest'
                    stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(vgremove_cmd)
                    info = str(stdout.read(), encoding='utf-8')
                    b = re.findall(r'Volume group “vgtest” successfully removed', info)
                    if b:
                        print('thin_vol0_snapshot remove successfully')
                        status = True
                        return status
                    else:
                        print('thin_vol0_snapshot remove failed')
                        status = False
                        return status
                else:
                    return status
            else:
                return status
        else:
            return status


class StripOperation():
    def __init__(self,obj_ssh):
        self.stripvolsize = yaml_info['strip vol']['stripvolsize']
        self.stripnumbers = yaml_info['strip vol']['stripnumbers']
        self.stripsize = yaml_info['strip vol']['stripsize']
        self.secondary = yaml_info['disk partition']['secondary']
        self.primary = yaml_info['disk partition']['primary']
        self.obj_ssh = obj_ssh

    def stripvol_create(self):
        status = False
        pvcreate_cmd = f'pvcreate {self.secondary}'
        stdin,stdout,stderr = self.obj_ssh.obj_SSHClient.exec_command(pvcreate_cmd)
        info = str(stdout.read(),encoding='utf-8')
        a = re.findall(r'Physical volume “'+self.secondary+'” successfully created',info)
        if a:
            print('secondary_pvcreate successfully')
            status = True
        else:
            print('secondary_pvcreate failed')
            status = False
        if status is True:
            vgcreate_cmd = f'vgcreate vgtest {self.primary} {self.secondary}'
            stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(vgcreate_cmd)
            info = str(stdout.read(), encoding='utf-8')
            a = re.findall(r'Volume group “vgtest” successfully created', info)
            if a:
                print('vgcreate successfully')
                status = True
            else:
                print('vgcreate failed')
                status = False
            if status is True:
                lvcreate_cmd = f'lvcreate -L {self.stripvolsize} -i {self.stripnumbers} -I {self.stripsize} –n lvtest vgtest'
                stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(lvcreate_cmd)
                info = str(stdout.read(), encoding='utf-8')
                a = re.findall(r'Logical volume “lvtest” created', info)
                if a:
                    print('strip_lvcreate successfully')
                    status = True
                    return status
                else:
                    print('strip_lvcreate failed')
                    status = True
                    return status
            else:
                return status
        else:
            return status

    def stripvol_check(self):
        pass

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