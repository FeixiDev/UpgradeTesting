import logging
import time
import datetime
import paramiko
import yaml
from operation import MainOperation
from operation import MirrorOperation
from operation import StripOperation
from operation import ThinOperation
from operation import Lvm2Operation


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


def yaml_read():
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    return config


def log():
    time1 = datetime.datetime.now().strftime('%Y%m%d %H_%M_%S')
    # 此处进行Logging.basicConfig() 设置，后面设置无效
    logging.basicConfig(filename=f'{time1} log.txt',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s-%(funcName)s',
                        level=logging.INFO)


def main():
    yaml_info = yaml_read()
    ip = yaml_info['node']['ip']
    passwd = yaml_info['node']['password']
    log()

    obj_ssh = Ssh(ip, passwd)
    main_operation_obj = MainOperation(obj_ssh,yaml_info)
    thin_operation_obj = ThinOperation(obj_ssh,yaml_info)
    strip_operation_obj = StripOperation(obj_ssh,yaml_info)
    mirror_operation_obj = MirrorOperation(obj_ssh,yaml_info)
    lvm_operation = Lvm2Operation(obj_ssh)

    # if not install_lvm2(obj_ssh):
    #     exit()
    # time.sleep(1)
    # if not main_operation_obj.pv_operation():
    #     exit()
    # time.sleep(1)
    # if not main_operation_obj.vg_operation():
    #     exit()
    # time.sleep(1)
    # if not main_operation_obj.lv_operation():
    #     exit()
    # time.sleep(1)
    # if not main_operation_obj.delete_operation():
    #     exit()
    # time.sleep(1)
    # if not thin_operation_obj.thinpool_create():        #bug
    #     exit()
    # time.sleep(1)
    # if not thin_operation_obj.thinvol_create():
    #     exit()
    # time.sleep(1)
    # if not thin_operation_obj.extend_operation():
    #     exit()
    # time.sleep(1)
    # if not thin_operation_obj.reduce_operation():
    #     exit()
    # time.sleep(1)
    # if not thin_operation_obj.snapshot_create():
    #     exit()
    # time.sleep(1)
    # if not thin_operation_obj.delete_operation():
    #     exit()
    # time.sleep(1)
    # if not strip_operation_obj.stripvol_create():
    #     exit()
    # time.sleep(1)
    # if not strip_operation_obj.stripvol_check():
    #     exit()
    # time.sleep(1)
    # if not strip_operation_obj.delete_operation():
    #     exit()
    # time.sleep(1)
    # if not mirror_operation_obj.mirrorvol_create():
    #     exit()
    # time.sleep(1)
    # if not mirror_operation_obj.mirrorvol_check():
    #     exit()
    # time.sleep(1)
    # if not mirror_operation_obj.delete_operation():
    #     exit()

    fun_list = ['lvm_operation.install_lvm2'
        ,'main_operation_obj.pv_operation'
        , 'main_operation_obj.vg_operation'
        , 'main_operation_obj.lv_operation'
        , 'main_operation_obj.delete_operation'
        , 'thin_operation_obj.thinpool_create'
        , 'thin_operation_obj.thinvol_create'
        , 'thin_operation_obj.extend_operation'
        , 'thin_operation_obj.reduce_operation'
        , 'thin_operation_obj.snapshot_create'
        , 'thin_operation_obj.delete_operation'
        , 'strip_operation_obj.stripvol_create'
        , 'strip_operation_obj.stripvol_check'
        , 'strip_operation_obj.delete_operation'
        , 'mirror_operation_obj.mirrorvol_create'
        , 'mirror_operation_obj.mirrorvol_check'
        , 'mirror_operation_obj.delete_operation']

    for i in fun_list:
        func = eval(i)
        stats = func()
        if stats is True:
            pass
        else:
            break


if __name__ == "__main__":
    main()
