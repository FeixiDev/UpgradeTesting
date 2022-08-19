import time
import datetime
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
        logging.info('  lvm2安装成功/版本正确')
        status = True
        return status
    else:
        print('Lvm2 version error')
        logging.info('  lvm2安装失败/版本错误')
        status = False
        return status


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
            logging.info('  ssh连接失败')

    def close(self):
        self.obj_SSHClient.close()


class Mainoperation():
    def __init__(self,obj_ssh):
        self.primary = yaml_info['disk partition']['primary']
        self.vgsize = yaml_info['basic operation']['vgsize']
        self.lvsize = yaml_info['basic operation']['lvsize']
        self.obj_ssh = obj_ssh
        logging.info('  开始进行基本操作测试')

    def pv_operation(self):
        status = False
        pvcreate_cmd = f'pvcreate {self.primary}'
        stdin,stdout,stderr = self.obj_ssh.obj_SSHClient.exec_command(pvcreate_cmd)
        info = str(stdout.read(),encoding='utf-8')
        a = re.findall(r'Physical volume "'+self.primary+'" successfully created',info)
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
            logging.info('      pv创建成功')
            status = True
        else:
            print('pvdisplay information error')
            logging.info('      pv创建失败')

        return status

    def vg_operation(self):
        status = False
        vgcreate_cmd = f'vgcreate vgtest {self.primary}'
        stdin,stdout,stderr = self.obj_ssh.obj_SSHClient.exec_command(vgcreate_cmd)
        info = str(stdout.read(),encoding='utf-8')
        a = re.findall(r'Volume group "vgtest" successfully created',info)
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
            logging.info('      vg创建成功')
            status = True
        else:
            print('vgdisplay information error')
            logging.info('      vg创建失败')

        return status

    def lv_operation(self):
        status = False
        lvcreate_cmd = f'lvcreate -L {self.lvsize} -n lvtest vgtest'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(lvcreate_cmd)
        info = str(stdout.read(), encoding='utf-8')
        a = re.findall(r'Logical volume "lvtest" created', info)
        if a:
            print('lvcreate successfully')
        else:
            print('lvcreate failed')
        lvdisplay_cmd = f'lvdisplay /dev/vgtest/lvtest'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(lvdisplay_cmd)
        info2 = str(stdout.read(), encoding='utf-8')
        b = re.findall(r'LV Name\s*lvtest', info2)
        if b:
            print('lvdisplay information is correct')
            logging.info('      lv创建成功')
            status = True
        else:
            print('lvdisplay information error')
            logging.info('      lv创建失败')

        return status

    def delete_operation(self):
        status = False
        lvremove_cmd = f'lvremove -y /dev/vgtest/lvtest'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(lvremove_cmd)
        info = str(stdout.read(), encoding='utf-8')
        a = re.findall(r'Logical volume "lvtest" successfully removed', info)
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
            b = re.findall(r'Volume group "vgtest" successfully removed', info)
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
                c = re.findall(r'Labels on physical volume "'+self.primary+'" successfully wiped', info)
                if c:
                    print('pvremove successfully')
                    status = True
                    logging.info('      删除流程成功')
                    return status
                else:
                    print('pvremove failed')
                    logging.info('      删除流程失败')
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
        logging.info('  开始进行精简卷配置测试')

    def thinpool_create(self):
        status = False
        pvcreate_cmd = f'pvcreate {self.primary}'
        stdin,stdout,stderr = self.obj_ssh.obj_SSHClient.exec_command(pvcreate_cmd)
        info = str(stdout.read(),encoding='utf-8')
        a = re.findall(r'Physical volume "'+self.primary+'" successfully created',info)
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
            c = re.findall(r'Volume group "vgtest" successfully created', info)
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
                thinpooldisplay_cmd = f'lvdisplay /dev/vgtest/pooltest'
                stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinpooldisplay_cmd)
                info2 = str(stdout.read(), encoding='utf-8')
                f = re.findall(r'LV Name\s*pooltest', info2)
                g = re.findall(r'LV Pool data\s*pooltest_tdata',info2)
                if f and g:
                    print('thinpool_lvdisplay information is correct')
                    status = True
                    logging.info('      精简池创建成功')
                    return status
                else:
                    print('thinpool_lvdisplay information error')
                    logging.info('      精简池创建失败')
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
        thinvoldisplay_cmd = f'lvdisplay /dev/vgtest/thin_vol'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinvoldisplay_cmd)
        info2 = str(stdout.read(), encoding='utf-8')
        f = re.findall(r'LV Name\s*thin_vol', info2)
        if f:
            print('thin_vol_lvdisplay information is correct')
            status = True
            logging.info('      精简卷创建成功')
            return status
        else:
            print('thin_vol_lvdisplay information error')
            logging.info('      精简卷创建失败')
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
            thinpoolcheck_cmd = 'lvdisplay /dev/vgtest/pooltest'
            stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinpoolcheck_cmd)
            info = str(stdout.read(), encoding='utf-8')
            after_extend = str(int(self.thinpoolsize.replace(self.thinpoolsize[-1], '')) + int(self.poolextendsize.replace(self.poolextendsize[-1], '')))
            j = re.findall(r'LV Size\s*'+after_extend, info)
            if j:
                print('thinpool extend successfully')
                logging.info('      精简池扩容成功')
                status = True
            else:
                print('thinpool extend failed')
                logging.info('      精简池扩容失败')
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
                        print('thinvol_display extend successfully')
                        logging.info('      精简卷扩容成功')
                        status = True
                        return status
                    else:
                        print('thinvol_display extend failed')
                        logging.info('      精简卷扩容失败')
                        status = False
                        return status
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
        size_number = str(self.volreducesize.replace(self.volreducesize[-1], ''))
        l = re.findall(r'LV Size\s*' + size_number, info)
        if l:
            print('thinvol reduce successfully')
            logging.info('      精简卷缩小成功')
            status = True
        else:
            print('thinvol reduce failed')
            logging.info('      精简卷缩小失败')
            status = False
        return status


    def snapshot_create(self):
        status = False
        thinpoolreduce_cmd = f'lvcreate -L {self.volreducesize} --snapshot --name thin_vol0 vgtest/thin_vol'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinpoolreduce_cmd)
        info = str(stdout.read(), encoding='utf-8')
        m = re.findall(r'Logical volume "thin_vol0" created', info)
        if m:
            print('thinvol_snapshot create successfully')
        else:
            print('thinvol_snapshot create failed')
        thinvol_snapshot_check_cmd = f'lvdisplay /dev/vgtest/thin_vol0'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinvol_snapshot_check_cmd)
        info = str(stdout.read(), encoding='utf-8')
        n = re.findall(r'LV Name\s*thin_vol0', info)
        if n:
            print('thinvol_snapshot_lvdisplay create successfully')
            logging.info('      精简卷快照创建成功')
            status = True
        else:
            print('thinvol_snapshot_lvdisplay create failed')
            logging.info('      精简卷快照创建失败')
            status = False
        return status

    def delete_operation(self):
        thinvol_snapshotremove_cmd = f'lvremove -y /dev/vgtest/thin_vol0'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinvol_snapshotremove_cmd)
        info = str(stdout.read(), encoding='utf-8')
        a = re.findall(r'Logical volume "thin_vol0" successfully removed', info)
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
            b = re.findall(r'Logical volume "thin_vol" successfully removed', info)
            if b:
                print('thin_vol_snapshot remove successfully')
                status = True
            else:
                print('thin_vol_snapshot remove failed')
                status = False
            if status is True:
                thinpool_remove_cmd = f'lvremove -y /dev/vgtest/pooltest'
                stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(thinpool_remove_cmd)
                info = str(stdout.read(), encoding='utf-8')
                b = re.findall(r'Logical volume "pooltest" successfully removed', info)
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
                    b = re.findall(r'Volume group "vgtest" successfully removed', info)
                    if b:
                        print('vg remove successfully')
                        logging.info('      精简卷操作删除成功')
                        status = True
                        return status
                    else:
                        print('vg remove failed')
                        logging.info('      精简卷操作删除失败')
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
        logging.info('  开始进行条带卷配置测试')

    def stripvol_create(self):
        status = False
        pvcreate_cmd = f'pvcreate {self.secondary}'
        stdin,stdout,stderr = self.obj_ssh.obj_SSHClient.exec_command(pvcreate_cmd)
        info = str(stdout.read(),encoding='utf-8')
        a = re.findall(r'Physical volume "'+self.secondary+'" successfully created',info)
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
            a = re.findall(r'Volume group "vgtest" successfully created', info)
            if a:
                print('vgcreate successfully')
                status = True
            else:
                print('vgcreate failed')
                status = False
            if status is True:
                lvcreate_cmd = f'lvcreate -L {self.stripvolsize} -i {self.stripnumbers} -I {self.stripsize} -n lvtest vgtest'
                stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(lvcreate_cmd)
                info = str(stdout.read(), encoding='utf-8')
                a = re.findall(r'Logical volume "lvtest" created', info)
                if a:
                    print('strip_lvcreate successfully')
                    logging.info('      条带卷创建成功')
                    status = True
                    return status
                else:
                    print('strip_lvcreate failed')
                    logging.info('      条带卷创建失败')
                    status = False
                    return status
            else:
                return status
        else:
            return status

    def stripvol_check(self):
        status = False
        stripcheck_cmd = f'lsblk'
        stdin,stdout,stderr = self.obj_ssh.obj_SSHClient.exec_command(stripcheck_cmd)
        info = str(stdout.read(),encoding='utf-8')
        a = re.findall(r'vgtest-lvtest',info)
        if len(a) == 2:
            print('strip check successfully')
            status = True
            return status
        else:
            print('secondary check failed')
            status = False
            return status

    def delete_operation(self):
        status = False
        lvremove_cmd = f'lvremove -y /dev/vgtest/lvtest'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(lvremove_cmd)
        info = str(stdout.read(), encoding='utf-8')
        a = re.findall(r'Logical volume "lvtest" successfully removed', info)
        if a:
            print('lvremove successfully')
            logging.info('      条带卷删除成功')
            status = True
            return status
        else:
            print('lvremove failed')
            logging.info('      条带卷删除失败')
            status = False
            return status


class MirrorOperation():
    def __init__(self,obj_ssh):
        self.secondary = yaml_info['disk partition']['secondary']
        self.primary = yaml_info['disk partition']['primary']
        self.mirrorvolsize = yaml_info['mirror vol']['mirrorvolsize']
        self.datavol = yaml_info['mirror vol']['datavol']
        self.replicavol = yaml_info['mirror vol']['replicavol']
        self.obj_ssh = obj_ssh
        logging.info('  开始进行镜像卷配置测试')

    def mirrorvol_create(self):
        status = False
        lvcreate_cmd = f'lvcreate -L {self.mirrorvolsize} -m1 -n lvmirror vgtest {self.datavol} {self.replicavol}'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(lvcreate_cmd)
        info = str(stdout.read(), encoding='utf-8')
        a = re.findall(r'Logical volume "lvmirror" created', info)
        if a:
            print('mirror create successfully')
            logging.info('      镜像卷创建成功')
            status = True
            return status
        else:
            print('mirror create failed')
            logging.info('      镜像卷创建失败')
            status = False
            return status

    def mirrorvol_check(self):
        status = False
        lvcheck_cmd = f'lvs -a -o +devices'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(lvcheck_cmd)
        info = str(stdout.read(), encoding='utf-8')
        a = re.findall(r'lvmirror', info)
        if len(a) == 7:
            print('mirror check successfully')
            status = True
            return status
        else:
            print('mirror check failed')
            status = False
            return status

    def delete_operation(self):
        status = False
        lvremove_cmd = f'lvremove -y /dev/vgtest/lvmirror'
        stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(lvremove_cmd)
        info = str(stdout.read(), encoding='utf-8')
        a = re.findall(r'Logical volume "lvmirror" successfully removed', info)
        if a:
            print('lvremove successfully')
            logging.info('      镜像卷删除成功')
            status = True
        else:
            print('lvremove failed')
            logging.info('      镜像卷删除失败')
            status = False

        if status is True:
            vgremove_cmd = f'vgremove vgtest'
            stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(vgremove_cmd)
            info = str(stdout.read(), encoding='utf-8')
            b = re.findall(r'Volume group "vgtest" successfully removed', info)
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
                c = re.findall(r'Labels on physical volume "'+self.primary+'" successfully wiped', info)
                pvremove_cmd_1 = f'pvremove {self.secondary}'
                stdin, stdout, stderr = self.obj_ssh.obj_SSHClient.exec_command(pvremove_cmd_1)
                info2 = str(stdout.read(), encoding='utf-8')
                d = re.findall(r'Labels on physical volume "'+self.secondary+'" successfully wiped', info2)
                if c and d:
                    print('pvremove successfully')
                    print('the program ends')
                    logging.info('  环境处理完成，程序结束')
                    status = True
                    return status
                else:
                    print('pvremove failed')
                    logging.info('  环境处理异常，程序结束')
                    status = False
                    return status
            else:
                return status
        else:
            return status

def log():
    time1 = datetime.datetime.now().strftime('%Y%m%d %H_%M_%S')
    # 此处进行Logging.basicConfig() 设置，后面设置无效
    logging.basicConfig(filename=f'{time1} log.txt',
                     format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s-%(funcName)s',
                     level=logging.INFO)

def main():
    ip = yaml_info['node']['ip']
    passwd = yaml_info['node']['password']
    log()

    obj_ssh = Ssh(ip,passwd)
    main_operation_obj = Mainoperation(obj_ssh)
    thin_operation_obj = ThinOperation(obj_ssh)
    strip_operation_obj = StripOperation(obj_ssh)
    mirror_operation_obj = MirrorOperation(obj_ssh)


    if not install_lvm2(obj_ssh):
        exit()
    time.sleep(1)
    if not main_operation_obj.pv_operation():
        exit()
    time.sleep(1)
    if not main_operation_obj.vg_operation():
        exit()
    time.sleep(1)
    if not main_operation_obj.lv_operation():
        exit()
    time.sleep(1)
    if not main_operation_obj.delete_operation():
        exit()
    time.sleep(1)
    if not thin_operation_obj.thinpool_create():        #bug
        exit()
    time.sleep(1)
    if not thin_operation_obj.thinvol_create():
        exit()
    time.sleep(1)
    if not thin_operation_obj.extend_operation():
        exit()
    time.sleep(1)
    if not thin_operation_obj.reduce_operation():
        exit()
    time.sleep(1)
    if not thin_operation_obj.snapshot_create():
        exit()
    time.sleep(1)
    if not thin_operation_obj.delete_operation():
        exit()
    time.sleep(1)
    if not strip_operation_obj.stripvol_create():
        exit()
    time.sleep(1)
    if not strip_operation_obj.stripvol_check():
        exit()
    time.sleep(1)
    if not strip_operation_obj.delete_operation():
        exit()
    time.sleep(1)
    if not mirror_operation_obj.mirrorvol_create():
        exit()
    time.sleep(1)
    if not mirror_operation_obj.mirrorvol_check():
        exit()
    time.sleep(1)
    if not mirror_operation_obj.delete_operation():
        exit()

    # fun_list = ['main_operation_obj.pv_operation','main_operation_obj.vg_operation','main_operation_obj.lv_operation','main_operation_obj.delete_operation']
    # for i in fun_list:
    #     func = eval(i)
    #     stats = func()
    #     if stats is True:
    #         pass
    #     else:
    #         break


if __name__ == "__main__":
    yaml_info = yaml_read()
    main()