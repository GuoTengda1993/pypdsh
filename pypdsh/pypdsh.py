# -*- coding: utf-8 -*-
import logging
import paramiko

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Connect:

    def __init__(self, ip, password, username='root', port=22):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.ip, port=self.port, username=self.username, password=self.password)

    def trans_file(self, source, dest):
        trans = paramiko.Transport((self.ip, 22))
        trans.connect(username=self.username, password=self.password)
        ft = paramiko.SFTPClient.from_transport(trans)
        ft.put(localpath=source, remotepath=dest)
        ft.close()

    def remote_command(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return stdout.read(), stderr.read()

    def close(self):
        self.ssh.close()


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
    conn = Connect(ip=ip, username=username, password=password)
    for each_command in command:
        out, error = conn.remote_command(each_command)
        if out:
            logger.info(ip + ': ' + out)
        if error:
            logger.error(ip + ': ' + error)
    conn.close()


def transfile(ip, username, password, source, dest):
    conn = Connect(ip=ip, username=username, password=password)
    conn.trans_file(source, dest)
    logger.info(ip + ': Transmit {source} >> {dest} finish.'.format(source=source, dest=dest))


if __name__ == '__main__':
    print(gen_ip('100.123.11.[1-36, 45, 67-78]'))