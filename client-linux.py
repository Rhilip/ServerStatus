# -*- coding: utf-8 -*-
# Update by : https://github.com/Rhilip/ServerStatus
# Support Python version：2.7 to 3.5
# Support OS version： Linux, OSX, FreeBSD, OpenBSD and NetBSD, both 32-bit and 64-bit architectures

import socket
import time
import re
import os
import json
import subprocess
import collections

# -*- CLIENT SETTING -*-
SERVER = "127.0.0.1"
PORT = 35601
USER = "USER"
PASSWORD = "USER_PASSWORD"
INTERVAL = 1  # Update interval
IN_CHINA = False  # enabled in china (changed to True)
# -*- END OF CLIENT SETTING -*-


def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime = f.readline()
        uptime = uptime.split('.', 2)
    return int(uptime[0])


def get_memory():
    re_parser = re.compile(r'^(?P<key>\S*):\s*(?P<value>\d*)\s*kB')
    result = dict()
    for line in open('/proc/meminfo'):
        match = re_parser.match(line)
        if not match:
            continue
        key, value = match.groups(['key', 'value'])
        result[key] = int(value)

    MemTotal = float(result['MemTotal'])
    MemUsed = MemTotal - (float(result['Cached']) + float(result['MemFree']))
    SwapTotal = float(result['SwapTotal'])
    SwapFree = float(result['SwapFree'])
    return int(MemTotal), int(MemUsed), int(SwapTotal), int(SwapFree)


def get_hdd():
    p = subprocess.check_output(
        ['df', '-Tlm', '--total', '-t', 'ext4', '-t', 'ext3', '-t', 'ext2', '-t', 'reiserfs', '-t', 'jfs', '-t', 'ntfs',
         '-t', 'fat32', '-t', 'btrfs', '-t', 'fuseblk', '-t', 'zfs', '-t', 'simfs', '-t', 'xfs']
    ).decode("utf-8")
    total = p.splitlines()[-1]
    used = total.split()[3]
    size = total.split()[2]
    return int(size), int(used)


def get_time():
    with open("/proc/stat", "r") as stat_file:
        time_list = stat_file.readline().split(' ')[2:6]
        for i in range(len(time_list)):
            time_list[i] = int(time_list[i])
        return time_list


def delta_time():
    x = get_time()
    time.sleep(INTERVAL)
    y = get_time()
    for i in range(len(x)):
        y[i] -= x[i]
    return y


def get_cpu():
    t = delta_time()
    st = sum(t)
    if st == 0:
        st = 1
    result = 100 - (t[len(t) - 1] * 100.00 / st)
    return round(result)


class Traffic:
    def __init__(self):
        self.rx = collections.deque(maxlen=10)
        self.tx = collections.deque(maxlen=10)

    def get(self):
        avgrx = avgtx = 0
        with open('/proc/net/dev', 'r') as f:
            net_dev = f.readlines()

        for dev in net_dev[2:]:
            dev = dev.split(':')
            if dev[0].strip() == "lo" or dev[0].find("tun") > -1:
                continue
            dev = dev[1].split()
            avgrx += int(dev[0])
            avgtx += int(dev[8])

        self.rx.append(avgrx)
        self.tx.append(avgtx)
        avgrx = avgtx = 0

        l = len(self.rx)
        for x in range(l - 1):
            avgrx += self.rx[x + 1] - self.rx[x]
            avgtx += self.tx[x + 1] - self.tx[x]

        avgrx = int(avgrx / l / INTERVAL)
        avgtx = int(avgtx / l / INTERVAL)

        return avgrx, avgtx


def liuliang():
    NET_IN = NET_OUT = 0
    re_parser = re.compile('([^\s]+):[\s]*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)')
    with open('/proc/net/dev') as f:
        for line in f.readlines():
            netinfo = re.findall(re_parser, line)
            if netinfo:
                if netinfo[0][0] == 'lo' or 'tun' in netinfo[0][0] or netinfo[0][1] == '0' or netinfo[0][9] == '0':
                    continue  # 排除localloop以及不存在流进流出的网卡
                else:
                    NET_IN += int(netinfo[0][1])
                    NET_OUT += int(netinfo[0][9])
    return NET_IN, NET_OUT


def get_network(ip_version):
    if IN_CHINA:  # 国内使用清华大学开源镜像站提供的域名解析服务
        HOST = "mirrors6.tuna.tsinghua.edu.cn" if ip_version == 6 else "mirrors4.tuna.tsinghua.edu.cn"
    else:
        HOST = "ipv6.google.com" if ip_version == 6 else "ipv4.google.com"

    try:
        socket.create_connection((HOST, 80), 2)
        return True
    except socket.error:
        return False


if __name__ == '__main__':
    socket.setdefaulttimeout(30)
    while 1:
        try:
            print("Connecting...")
            s = socket.create_connection((SERVER, PORT), 5)
            data = s.recv(1024)
            if data.find("Authentication required") > -1:
                s.send(USER + ':' + PASSWORD + '\n')
                data = s.recv(1024)
                if data.find("Authentication successful") < 0:
                    print(data)
                    raise socket.error
            else:
                print(data)
                raise socket.error

            print(data)
            data = s.recv(1024)
            print(data)

            timer = 0
            check_ip = 0
            if data.find("IPv4") > -1:
                check_ip = 6
            elif data.find("IPv6") > -1:
                check_ip = 4
            else:
                print(data)
                raise socket.error

            traffic = Traffic()
            traffic.get()
            while 1:
                CPU = get_cpu()
                NetRx, NetTx = traffic.get()
                NET_IN, NET_OUT = liuliang()
                Uptime = get_uptime()
                Load_1, Load_5, Load_15 = os.getloadavg()
                MemoryTotal, MemoryUsed, SwapTotal, SwapFree = get_memory()
                HDDTotal, HDDUsed = get_hdd()

                array = {}
                if not timer:
                    array['online' + str(check_ip)] = get_network(check_ip)
                    timer = 10
                else:
                    timer -= 1 * INTERVAL

                array['uptime'] = Uptime
                array['load_1'] = Load_1
                array['load_5'] = Load_5
                array['load_15'] = Load_15
                array['memory_total'] = MemoryTotal
                array['memory_used'] = MemoryUsed
                array['swap_total'] = SwapTotal
                array['swap_used'] = SwapTotal - SwapFree
                array['hdd_total'] = HDDTotal
                array['hdd_used'] = HDDUsed
                array['cpu'] = CPU
                array['network_rx'] = NetRx
                array['network_tx'] = NetTx
                array['network_in'] = NET_IN
                array['network_out'] = NET_OUT

                s.send("update " + json.dumps(array) + "\n")
        except KeyboardInterrupt:
            raise
        except socket.error:
            print("Disconnected...")
            # keep on trying after a disconnect
            s.close()
            time.sleep(3)
        except Exception as e:
            print("Caught Exception:", e)
            s.close()
            time.sleep(3)
