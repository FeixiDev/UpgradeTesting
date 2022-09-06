import logging
import re
import yaml
import subprocess

def yaml_read():
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    return config


class Lvm2Operation():
    def __init__(self):
        pass

    def install_lvm2(self):
        install_cmd = "apt-get install -y lvm2"
        result01 = subprocess.run(f'{install_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        check_cmd = 'apt-cache policy lvm2'
        result02 = subprocess.run(f'{check_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        a = re.findall(r'Installed: ([\w\W]*) Candidate', result02.stdout)
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


class MainOperation():
    def __init__(self,yaml_info):
        self.primary = yaml_info['disk partition']['primary']
        self.vgsize = yaml_info['basic operation']['vgsize']
        self.lvsize = yaml_info['basic operation']['lvsize']
        logging.info('  开始进行基本操作测试')

    def pv_operation(self):
        status = False
        pvcreate_cmd = f'pvcreate {self.primary}'
        result01 = subprocess.run(f'{pvcreate_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        a = re.findall(r'Physical volume "' + self.primary + '" successfully created', result01.stdout)
        if a:
            print('pvcreate successfully')
        else:
            print('pvcreate failed')
        pvdisplay_cmd = f'pvdisplay {self.primary}'
        result02 = subprocess.run(f'{pvdisplay_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        b = re.findall(r'PV Name\s*' + self.primary, result02.stdout)
        if b:
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
        result03 = subprocess.run(f'{vgcreate_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        a = re.findall(r'Volume group "vgtest" successfully created', result03.stdout)
        if a:
            print('vgcreate successfully')
        else:
            print('vgcreate failed')
        vgdisplay_cmd = f'vgdisplay vgtest'
        result04 = subprocess.run(f'{vgdisplay_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        b = re.findall(r'VG Name\s*vgtest', result04.stdout)
        if b:
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
        result05 = subprocess.run(f'{lvcreate_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        a = re.findall(r'Logical volume "lvtest" created', result05.stdout)
        if a:
            print('lvcreate successfully')
        else:
            print('lvcreate failed')
        lvdisplay_cmd = f'lvdisplay /dev/vgtest/lvtest'
        result06 = subprocess.run(f'{lvdisplay_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        b = re.findall(r'LV Name\s*lvtest', result06.stdout)
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
        result07 = subprocess.run(f'{lvremove_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        a = re.findall(r'Logical volume "lvtest" successfully removed', result07.stdout)
        if a:
            print('lvremove successfully')
            status = True
        else:
            print('lvremove failed')
            status = False

        if status is True:
            vgremove_cmd = f'vgremove vgtest'
            result08 = subprocess.run(f'{vgremove_cmd}', shell=True, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, encoding='utf-8',
                                      timeout=100)
            b = re.findall(r'Volume group "vgtest" successfully removed', result08.stdout)
            if b:
                print('vgremove successfully')
                status = True
            else:
                print('vgremove failed')
                status = False

            if status is True:
                pvremove_cmd = f'pvremove {self.primary}'
                result09 = subprocess.run(f'{pvremove_cmd}', shell=True, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, encoding='utf-8',
                                          timeout=100)
                c = re.findall(r'Labels on physical volume "' + self.primary + '" successfully wiped', result09.stdout)
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

    def __init__(self,yaml_info):
        self.primary = yaml_info['disk partition']['primary']
        self.thinpoolsize = yaml_info['thin vol']['thinpoolsize']
        self.thinvolsize = yaml_info['thin vol']['thinvolsize']
        self.poolextendsize = yaml_info['thin vol']['poolextendsize']
        self.volextendsize = yaml_info['thin vol']['volextendsize']
        self.volreducesize = yaml_info['thin vol']['volreducesize']
        logging.info('  开始进行精简卷配置测试')

    def thinpool_create(self):
        status = False
        pvcreate_cmd = f'pvcreate {self.primary}'
        result01 = subprocess.run(f'{pvcreate_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        a = re.findall(r'Physical volume "' + self.primary + '" successfully created', result01.stdout)
        if a:
            print('pvcreate successfully')
        else:
            print('pvcreate failed')
        pvdisplay_cmd = f'pvdisplay {self.primary}'
        result02 = subprocess.run(f'{pvdisplay_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        b = re.findall(r'PV Name\s*' + self.primary, result02.stdout)
        if b:
            print('pvdisplay information is correct')
            status = True
        else:
            print('pvdisplay information error')
            status = False

        if status is True:
            vgcreate_cmd = f'vgcreate vgtest {self.primary}'
            result03 = subprocess.run(f'{vgcreate_cmd}', shell=True, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, encoding='utf-8',
                                      timeout=100)
            c = re.findall(r'Volume group "vgtest" successfully created', result03.stdout)
            if c:
                print('vgcreate successfully')
            else:
                print('vgcreate failed')
            vgdisplay_cmd = f'vgdisplay vgtest'
            result04 = subprocess.run(f'{vgdisplay_cmd}', shell=True, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, encoding='utf-8',
                                      timeout=100)
            d = re.findall(r'VG Name\s*vgtest', result04.stdout)
            if d:
                print('vgdisplay information is correct')
                status = True
            else:
                print('vgdisplay information error')
                status = False

            if status is True:
                poolcreate_cmd = f'lvcreate -L {self.thinpoolsize} --thinpool pooltest vgtest'
                result05 = subprocess.run(f'{poolcreate_cmd}', shell=True, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, encoding='utf-8',
                                          timeout=100)
                e = re.findall(r'Logical volume "pooltest" created', result05.stdout)
                if e:
                    print('thinpool create successfully')
                else:
                    print('thinpool create failed')
                thinpooldisplay_cmd = f'lvdisplay /dev/vgtest/pooltest'
                result06 = subprocess.run(f'{thinpooldisplay_cmd}', shell=True, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, encoding='utf-8',
                                          timeout=100)
                f = re.findall(r'LV Name\s*pooltest', result06.stdout)
                g = re.findall(r'LV Pool data\s*pooltest_tdata', result06.stdout)
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
        result07 = subprocess.run(f'{thinvolcreate_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        h = re.findall(r'Logical volume "thin_vol" created', result07.stdout)
        if h:
            print('thinvol create successfully')
        else:
            print('thinvol create failed')
        thinvoldisplay_cmd = f'lvdisplay /dev/vgtest/thin_vol'
        result08 = subprocess.run(f'{thinvoldisplay_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        f = re.findall(r'LV Name\s*thin_vol', result08.stdout)
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
        result09 = subprocess.run(f'{thinpoolextend_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        i = re.findall(r'Logical volume vgtest/pooltest_tdata successfully resized', result09.stdout)
        if i:
            print('thinvol create successfully')
            status = True
        else:
            print('thinvol create failed')
            status = False
        if status is True:
            thinpoolcheck_cmd = 'lvdisplay /dev/vgtest/pooltest'
            result10 = subprocess.run(f'{thinpoolcheck_cmd}', shell=True, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, encoding='utf-8',
                                      timeout=100)
            after_extend = str(int(self.thinpoolsize.replace(self.thinpoolsize[-1], '')) + int(
                self.poolextendsize.replace(self.poolextendsize[-1], '')))
            j = re.findall(r'LV Size\s*' + after_extend, result10.stdout)
            if j:
                print('thinpool extend successfully')
                logging.info('      精简池扩容成功')
                status = True
            else:
                print('thinpool extend failed')
                logging.info('      精简池扩容失败')
                status = False
            if status is True:
                thinvolextend_cmd = f'lvextend -L +' + self.volextendsize + ' vgtest/thin_vol'
                result11 = subprocess.run(f'{thinvolextend_cmd}', shell=True, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, encoding='utf-8',
                                          timeout=100)
                i = re.findall(r'Logical volume vgtest/thin_vol successfully resized', result11.stdout)
                if i:
                    print('thinvol extend successfully')
                    status = True
                else:
                    print('thinvol extend failed')
                    status = False
                if status is True:
                    thinvolcheck_cmd = 'lvdisplay /dev/vgtest/thin_vol'
                    result12 = subprocess.run(f'{thinvolcheck_cmd}', shell=True, stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE, encoding='utf-8',
                                              timeout=100)
                    after_extend = str(int(self.thinvolsize.replace(self.thinvolsize[-1], '')) + int(
                        self.volextendsize.replace(self.volextendsize[-1], '')))
                    j = re.findall(r'LV Size\s*' + after_extend, result12.stdout)
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
        result13 = subprocess.run(f'{thinpoolreduce_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        k = re.findall(r'Logical volume vgtest/thin_vol successfully resized', result13.stdout)
        if k:
            print('thinvol reduce successfully')
        else:
            print('thinvol reduce failed')
        thinpoolreducecheck_cmd = f'lvdisplay /dev/vgtest/thin_vol'
        result14 = subprocess.run(f'{thinpoolreducecheck_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        size_number = str(self.volreducesize.replace(self.volreducesize[-1], ''))
        l = re.findall(r'LV Size\s*' + size_number, result14.stdout)
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
        result15 = subprocess.run(f'{thinpoolreduce_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        m = re.findall(r'Logical volume "thin_vol0" created', result15.stdout)
        if m:
            print('thinvol_snapshot create successfully')
        else:
            print('thinvol_snapshot create failed')
        thinvol_snapshot_check_cmd = f'lvdisplay /dev/vgtest/thin_vol0'
        result16 = subprocess.run(f'{thinvol_snapshot_check_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        n = re.findall(r'LV Name\s*thin_vol0', result16.stdout)
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
        result17 = subprocess.run(f'{thinvol_snapshotremove_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        a = re.findall(r'Logical volume "thin_vol0" successfully removed', result17.stdout)
        if a:
            print('thin_vol0_snapshot remove successfully')
            status = True
        else:
            print('thin_vol0_snapshot remove failed')
            status = False
        if status is True:
            thinvol_remove_cmd = f'lvremove -y /dev/vgtest/thin_vol'
            result18 = subprocess.run(f'{thinvol_remove_cmd}', shell=True, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, encoding='utf-8',
                                      timeout=100)
            b = re.findall(r'Logical volume "thin_vol" successfully removed', result18.stdout)
            if b:
                print('thin_vol_snapshot remove successfully')
                status = True
            else:
                print('thin_vol_snapshot remove failed')
                status = False
            if status is True:
                thinpool_remove_cmd = f'lvremove -y /dev/vgtest/pooltest'
                result19 = subprocess.run(f'{thinpool_remove_cmd}', shell=True, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, encoding='utf-8',
                                          timeout=100)
                b = re.findall(r'Logical volume "pooltest" successfully removed', result19.stdout)
                if b:
                    print('thin_pool remove successfully')
                    status = True
                else:
                    print('thin_pool remove failed')
                    status = False
                if status is True:
                    vgremove_cmd = f'vgremove -y vgtest'
                    result20 = subprocess.run(f'{vgremove_cmd}', shell=True, stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE, encoding='utf-8',
                                              timeout=100)
                    b = re.findall(r'Volume group "vgtest" successfully removed', result20.stdout)
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
    def __init__(self,yaml_info):
        self.stripvolsize = yaml_info['strip vol']['stripvolsize']
        self.stripnumbers = yaml_info['strip vol']['stripnumbers']
        self.stripsize = yaml_info['strip vol']['stripsize']
        self.secondary = yaml_info['disk partition']['secondary']
        self.primary = yaml_info['disk partition']['primary']
        logging.info('  开始进行条带卷配置测试')

    def stripvol_create(self):
        status = False
        pvcreate_cmd = f'pvcreate {self.secondary}'
        result01 = subprocess.run(f'{pvcreate_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        a = re.findall(r'Physical volume "' + self.secondary + '" successfully created', result01.stdout)
        if a:
            print('secondary_pvcreate successfully')
            status = True
        else:
            print('secondary_pvcreate failed')
            status = False
        if status is True:
            vgcreate_cmd = f'vgcreate vgtest {self.primary} {self.secondary}'
            result02 = subprocess.run(f'{vgcreate_cmd}', shell=True, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, encoding='utf-8',
                                      timeout=100)
            a = re.findall(r'Volume group "vgtest" successfully created', result02.stdout)
            if a:
                print('vgcreate successfully')
                status = True
            else:
                print('vgcreate failed')
                status = False
            if status is True:
                lvcreate_cmd = f'lvcreate -L {self.stripvolsize} -i {self.stripnumbers} -I {self.stripsize} -n lvtest vgtest'
                result03 = subprocess.run(f'{lvcreate_cmd}', shell=True, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, encoding='utf-8',
                                          timeout=100)
                a = re.findall(r'Logical volume "lvtest" created', result03.stdout)
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
        result04 = subprocess.run(f'{stripcheck_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        a = re.findall(r'vgtest-lvtest', result04.stdout)
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
        result05 = subprocess.run(f'{lvremove_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        a = re.findall(r'Logical volume "lvtest" successfully removed', result05.stdout)
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
    def __init__(self,yaml_info):
        self.secondary = yaml_info['disk partition']['secondary']
        self.primary = yaml_info['disk partition']['primary']
        self.mirrorvolsize = yaml_info['mirror vol']['mirrorvolsize']
        self.datavol = yaml_info['mirror vol']['datavol']
        self.replicavol = yaml_info['mirror vol']['replicavol']
        logging.info('  开始进行镜像卷配置测试')

    def mirrorvol_create(self):
        status = False
        lvcreate_cmd = f'lvcreate -L {self.mirrorvolsize} -m1 -n lvmirror vgtest {self.datavol} {self.replicavol}'
        result01 = subprocess.run(f'{lvcreate_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        a = re.findall(r'Logical volume "lvmirror" created', result01.stdout)
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
        result02 = subprocess.run(f'{lvcheck_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        a = re.findall(r'lvmirror', result02.stdout)
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
        result03 = subprocess.run(f'{lvremove_cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        a = re.findall(r'Logical volume "lvmirror" successfully removed', result03.stdout)
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
            result04 = subprocess.run(f'{vgremove_cmd}', shell=True, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, encoding='utf-8',
                                      timeout=100)
            b = re.findall(r'Volume group "vgtest" successfully removed', result04.stdout)
            if b:
                print('vgremove successfully')
                status = True
            else:
                print('vgremove failed')
                status = False

            if status is True:
                pvremove_cmd = f'pvremove {self.primary}'
                result05 = subprocess.run(f'{pvremove_cmd}', shell=True, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, encoding='utf-8',
                                          timeout=100)
                c = re.findall(r'Labels on physical volume "' + self.primary + '" successfully wiped', result05.stdout)
                pvremove_cmd_1 = f'pvremove {self.secondary}'
                result06 = subprocess.run(f'{pvremove_cmd_1}', shell=True, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, encoding='utf-8',
                                          timeout=100)
                d = re.findall(r'Labels on physical volume "' + self.secondary + '" successfully wiped', result06.stdout)
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

if __name__ == "__main__":
    pass