import os
import csv
import sys
import time
import getpass
from optparse import OptionParser
from threading import Thread
import pypdsh
from .pypdsh import *

version = pypdsh.__version__

logName = time.strftime('%Y%m%d-%H%M%S', time.localtime()) + '_log.txt'
handler = logging.FileHandler(logName)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def parse_options():
    """
    Handle command-line options with optparse.OptionParser.

    Return list of arguments, largely for use in `parse_arguments`.
    """

    # Initialize
    parser = OptionParser(usage="pypdsh [options] [PypdshClass [PypdshClass2 ... ]]")

    parser.add_option(
        '-i', '--ip',
        dest='ip',
        type='str',
        help="single ip or ip in format '192.168.1.[1-10,16,19,30-40]'"
    )

    parser.add_option(
        '-I', '--IP',
        dest='IP',
        type='str',
        help="ip(s) in CSV file: ip | username | password"
    )

    parser.add_option(
        '-c', '--command',
        dest='command',
        type='str',
        help="single command or command in TXT file",
        default=""
    )

    parser.add_option(
        '-f', '--file',
        dest='file',
        type='str',
        help="file to transmit to each host",
        default=""
    )

    parser.add_option(
        '-d', '--destination',
        dest='destination',
        type='str',
        help="destination path of each host, and this path must be existing in host(s)",
        default=""
    )

    parser.add_option(
        '-p', '--password',
        action='store',
        type='str',
        dest='password',
        default="",
        help="password of host(s)",
    )

    parser.add_option(
        '-u', '--username',
        action='store',
        type='str',
        dest='username',
        default="root",
        help="username of host(s)",
    )

    parser.add_option(
        '--log-level',
        action='store',
        type='str',
        dest='log_level',
        default="INFO",
        help="log level: INFO or ERROR",
    )

    # Version number (optparse gives you --version but we have to do it
    # ourselves to get -V too. sigh)
    parser.add_option(
        '-v', '-V', '--version',
        action='store_true',
        dest='version',
        default=False,
        help="show version number of pypdsh and exit"
    )
    # Finalize
    # Return three-tuple of parser + the output from parse_args (opt obj, args)
    opts, args = parser.parse_args()
    return parser, opts, args


def main():
    parser, options, arguments = parse_options()
    _mark = 0

    if options.version:
        logger.info("pypdsh %s" % (version,))
        sys.exit(0)

    if options.ip and options.IP:
        logger.error('Cannot use "ip" and "IP" together')
        sys.exit(1)

    if options.command and options.file:
        logger.error('Cannot use "-c" and "-f" together')
        sys.exit(1)

    if not options.command and not options.file:
        logger.error('Nothing to do')
        sys.exit(1)

    if options.file and not options.destination:
        logger.error('missing "-d" parameter' )
        sys.exit(1)

    log_level = options.log_level
    if log_level.upper() != 'INFO' and log_level.upper() != 'ERROR':
        logger.error('log level should be INFO or ERROR')
        sys.exit(1)
    if log_level.upper() == 'INFO': logger.setLevel(logging.INFO)
    if log_level.upper() == 'ERROR': logger.setLevel(logging.ERROR)

    if options.command:
        _mark = 1
        command = options.command
        if str(command).endswith('.txt'):
            with open(command, 'r') as f:
                commands = f.readlines()
        else:
            commands = [command]

    if options.file:
        _mark = 2
        source = options.file
        dest = options.destination
        filename = os.path.basename(source)
        if filename.split('.')[-1] in dest.split('.')[-1]:
            pass
        else:
            dest = os.path.join(dest, filename)

    if options.ip:
        ip_list = gen_ip(options.ip)
        username = options.username
        password = options.password
        if not password:
            p1 = getpass.getpass('Please input your password:')
            p2 = getpass.getpass('Please conform your password:')
            while p1 != p2:
                print('The password you typed is NOT same.')
                p1 = getpass.getpass('Please input your password:')
                p2 = getpass.getpass('Please conform your password:')
            password = p1
        if _mark == 1:
            for ip in ip_list:
                t = Thread(target=run, args=(ip, username, password, commands))
                t.start()
                t.join()
            sys.exit(0)
        if _mark == 2:
            for ip in ip_list:
                t = Thread(target=transfile, args=(ip, username, password, source, dest))
                t.start()
                t.join()
            sys.exit(0)
    if options.IP:
        if options.username or options.password:
            logger.warning('"-u" and "-p" will not work with "-I"')
        csv_file = options.IP
        with open(csv_file, 'r') as f:
            host_infos = csv.reader(f)
        if _mark == 1:
            for host in host_infos:
                t = Thread(target=run, args=(host[0], host[1], host[2], commands))
                t.start()
                t.join()
                sys.exit(0)
        if _mark == 2:
            for host in host_infos:
                t = Thread(target=transfile, args=(host[0], host[1], host[2], source, dest))
                t.start()
                t.join()
                sys.exit(0)
