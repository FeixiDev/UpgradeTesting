import sys
import commands
import logging
import time
import subprocess
import datetime
import paramiko
import yaml
import logging


class YamlRead:
    def __init__(self):
        self.yaml_info = self.yaml_read()
        self.yaml_status = self.yaml_judge()

    def yaml_read(self):
        with open('config.yaml') as f:
            config = yaml.safe_load(f)
        return config

    def yaml_judge(self):
        if bool(self.yaml_info['node']['ip']) is True and bool(self.yaml_info['node']['password']) is True:
            return  True
        else:
            return False

class Ssh:
    def __init__(self, ip, password):
        self.ip = ip
        self.port = 22
        self.username = 'root'
        self.password = password
        self.obj_SSHClient = paramiko.SSHClient()

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

    def exec_cmd(self,cmd):
        self.obj_SSHClient.exec_command(f'{cmd}')
        stdin, stdout, stderr = self.obj_SSHClient.exec_command(f'{cmd}')
        # data = stdout.read()
        # if len(data) > 0:
        #     data = data.decode() if isinstance(data, bytes) else data
        #     return data
        err = stderr.read()
        if len(err) > 0:
            err = err.decode() if isinstance(err, bytes) else err
            print(f'{cmd} failed')
            log_data = f"{cmd} - 'successfully'"
            Log().logger.info(log_data)
            return False
        else:
            print(f'{cmd} successfully')
            log_data = f"{cmd} - 'failed'"
            Log().logger.info(log_data)
            return True

    def close(self):
        self.obj_SSHClient.close()


class ExecuteLocally:
    def __init__(self):
        pass

    def exec_cmd(self,cmd):
        result = subprocess.run(f'{cmd}', shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, encoding='utf-8',
                           timeout=100)
        if result.returncode == 0 :
            print(f'{cmd} successfully')
            log_data = f"{cmd} - 'successfully'"
            Log().logger.info(log_data)
            return True
        else:
            print(f'{cmd} failed')
            log_data = f"{cmd} - 'failed'"
            Log().logger.info(log_data)
            return False


class MainOperation:
    def __init__(self):
        self.yaml_obj = YamlRead()
        self.yaml_obj_status = self.yaml_obj.yaml_status
        self.yaml_info_list = self.yaml_obj.yaml_info
        self.Lvm2Operation_obj = commands.Lvm2Operation_cmds()
        self.MainOperation_obj = commands.MainOperation_cmds(self.yaml_info_list)
        self.ThinOperation_obj = commands.ThinOperation_cmds(self.yaml_info_list)
        self.StripOperation_obj = commands.StripOperation_cmds(self.yaml_info_list)
        self.MirrorOperation_obj = commands.MirrorOperation_cmds(self.yaml_info_list)
        self.ssh_obj = Ssh(self.yaml_info_list['node']['ip'],self.yaml_info_list['node']['password'])
        self.sub_obj = ExecuteLocally()
        self.fun_name_list = []
        self.all_cmds_list = self.all_cmds()

    def all_cmds(self):
        all_cmds = []
        all_cmds.extend(self.Lvm2Operation_obj.cmd_list)
        all_cmds.extend(self.MainOperation_obj.cmd_list)
        all_cmds.extend(self.ThinOperation_obj.cmd_list)
        all_cmds.extend(self.StripOperation_obj.cmd_list)
        all_cmds.extend(self.MirrorOperation_obj.cmd_list)
        return all_cmds

    def exec_fun(self,fun_list):
        print(fun_list[0])
        for i in fun_list:
            funct = eval(i)
            status = funct
            if status is True:
                pass
            else:
                sys.exit()

    def execution(self):
        if self.yaml_obj_status is True:
            self.ssh_obj.connect()
            for i in self.all_cmds_list:
                strr = f"self.ssh_obj.exec_cmd('{i}')"
                self.fun_name_list.append(strr)
            self.exec_fun(self.fun_name_list)
        if self.yaml_obj_status is False:
            for i in self.all_cmds_list:
                strr = f"self.sub_obj.exec_cmd('{i}')"
                self.fun_name_list.append(strr)
            self.exec_fun(self.fun_name_list)

class Log(object):
    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            Log._instance = super().__new__(cls)
            Log._instance.logger = logging.getLogger()
            Log._instance.logger.setLevel(logging.INFO)
            Log.set_handler(Log._instance.logger)
        return Log._instance

    @staticmethod
    def set_handler(logger):
        fh = logging.FileHandler('./UpgradeTestingLog', mode='a')
        fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)