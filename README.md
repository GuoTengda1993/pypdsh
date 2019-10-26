# pypdsh
PDSH in Python version.
## How to Use It?
Open Console, type `pypdsh -h`, you will see some parameters
>-h, --help
>>show this help message and exit

>-i IP, --ip=IP
>>single ip or ip in format '192.168.1.[1-10,16,19,30-40]'

>-I IP, --IP=IP
>>ip(s) in CSV file: ip | username | password

>-c COMMAND, --command=COMMAND
>>single command or command in TXT file

>-f FILE, --file=FILE
>>file to transmit to each host

>-g LOCALPATH, --get=LOCALPATH
>>get file from remote host

>-d DESTINATION, --destination=DESTINATION
>>destination path of each host, and this path must be existing in host(s)

>-p PASSWORD, --password=PASSWORD
>>password of host(s)

>-u USERNAME, --username=USERNAME
>>username of host(s)

>--log-level=LOG_LEVEL
>>log level: INFO or ERROR

>-v, -V, --version
>>show version number of pypdsh and exit
