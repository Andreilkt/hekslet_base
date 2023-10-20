from datetime import datetime
import os
import paramiko
import re
import socket
import time

date_name = datetime.strftime(datetime.now(), '%d-%b-%y_%H-%M')
date_log = datetime.strftime(datetime.now(), "%b %d %H:%M:%S %Y:")


def getConfig(ip, password, max_bytes=60000):

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(hostname=ip, username='user', password=password, look_for_keys=False, allow_agent=False)
    except (socket.error, paramiko.AuthenticationException, paramiko.SSHException) as message:
        return message

    with ssh.invoke_shell() as shell:
        while True:
            output_hostname = shell.recv(max_bytes).decode('utf-8').split()
            time.sleep(0.5)
            if '>' in output_hostname[-1]:
                hostname = ''.join(output_hostname[-1].split('>'))
                break
        result = {}
        shell.send('iplir show config\n')
        shell.settimeout(5)
        output = ""
        while True:
            try:
                page = shell.recv(max_bytes).decode("utf-8", errors='ignore')
                output += page
            except socket.timeout:
                break
            if ":" in page:
                shell.send(' ')
        ansi_escape = re.compile(r'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])|:|\r|\(END\)')
        output = ansi_escape.sub('', output)
        result = output
        ssh.close()

    return hostname, result[20:]


if __name__ == '__main__':

    hosts = {
        #'ip': 'password'
        # '1.1.1.1': '12345',
        '192.168.79.46': '11111111'
    }

    for host, password in hosts.items():
        result = getConfig(host, password)
        try:
            if not os.path.exists(result[0]):
                os.mkdir(result[0])
            os.chdir(result[0])

            with open(f'{date_name}_iplir.conf', 'w', newline='\n') as iplir_conf:
                iplir_conf.write(result[1])
            os.chdir('..')
        except:
            with open(f'messages.log', 'a') as message_log:
                message_log.write(f'{date_log} {host}: {str(result)}\n')
            pass

for i in range(1, 10):
    print(f'iplir tcptunnel server port {i}')
