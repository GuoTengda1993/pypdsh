# -*- coding: utf-8 -*-
import os
import logging
import paramiko

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SSHAgent:

    def __init__(self, ip, password, username='root', port=22):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.ip, port=self.port, username=self.username, password=self.password)
        self.trans = paramiko.Transport((self.ip, port))
        self.trans.connect(username=self.username, password=self.password)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ssh.close()
        self.trans.close()

    def trans_file(self, source, dest):
        ft = paramiko.SFTPClient.from_transport(self.trans)
        ft.put(localpath=source, remotepath=dest)
        ft.close()

    def get_file(self, localfile, remotefile):
        gt = paramiko.SFTPClient.from_transport(self.trans)
        gt.get(localpath=localfile, remotepath=remotefile)
        gt.close()

    def remote_command(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return stdout.read(), stderr.read()

    def close(self):
        self.ssh.close()
        self.trans.close()


def gen_ip(ip):
    if ('[' or ']') not in ip:
        return [ip]
    else:
        ips = []
        ip_section = ip.split('.')
        ip_range = ip_section[3][1:-1]
        ip4_list = []
        for each in ip_range.split(','):
            if '-' not in each:
                ip4_list.append(each.strip())
            else:
                part4 = each.split('-')
                for i in range(int(part4[0].strip()), int(part4[1].strip())+1):
                    ip4_list.append(i)
        for ip4 in ip4_list:
            ip_pattern = str(ip_section[0] + '.' + ip_section[1] + '.' + ip_section[2] + '.' + '{ip4}')
            ips.append(ip_pattern.format(ip4=ip4))
        return ips


def run(ip, username, password, command):
    try:
        conn = SSHAgent(ip=ip, username=username, password=password)
        with conn:
            for each_command in command:
                out, error = conn.remote_command(each_command)
                if out:
                    logger.info(ip + ':\r\n' + out.decode('utf-8'))
                if error:
                    logger.error(ip + ':\r\n' + error.decode('utf-8'))
    except paramiko.ssh_exception.AuthenticationException:
        logger.error(ip + ': Authentication Fail, please check the password!')


def transfile(ip, username, password, source, dest):
    try:
        conn = SSHAgent(ip=ip, username=username, password=password)
        with conn:
            conn.trans_file(source, dest)
            logger.info(ip + ': Transmit {source} >> {dest} finish.'.format(source=source, dest=dest))
    except paramiko.ssh_exception.AuthenticationException:
        logger.error(ip + ': Authentication Fail, please check the password!')


def get_files(ip, username, password, localpath, remotefile):
    filename = remotefile.split('/')[-1]
    local_filename = ip + '_' + filename
    local_file = os.path.join(localpath, local_filename)
    try:
        conn = SSHAgent(ip=ip, username=username, password=password)
        with conn:
            conn.get_file(local_file, remotefile)
            logger.info(ip + ': Get File {localpath} << {remotefile} finish.'.format(localpath=local_file, remotefile=remotefile))
    except paramiko.ssh_exception.AuthenticationException:
        logger.error(ip + ': Authentication Fail, please check the password!')


if __name__ == '__main__':
    print(gen_ip('100.123.11.[1-36, 45, 67-78]'))
