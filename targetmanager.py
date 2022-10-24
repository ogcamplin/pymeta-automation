import pandas as pd
import json
import os

class TargetManager():
    def __init__(self, hosts_table):
        self.hosts_table = hosts_table
        self.targets = {}
        return

    def get_target(self, ip):
        return self.targets[ip]

    def parse_targets_from_host(self, hosts):
        hosts = filter(lambda x: x['os_name'] == 'Windows 7', hosts)

        for host in hosts:
            ip = host['address']
            
            self.targets[ip] = Target(ip)
            info = host['info']
            if info != '':
                info: dict = json.loads(host['info'])
                if 'backdoor_port' in info.keys():
                    self.targets[ip].backdoor = True
                    self.targets[ip].backdoor_port = info['backdoor_port']

    def get_targets_dict(self):
        return self.targets

    def get_targets_df(self, exploited=False):
        tar_list = []

        for i, t in enumerate(self.targets.values()):
            tar_list.append([t.ip, t.is_exploited(), t.how_exploited, t.sid, t.backdoor, t.status])

        df = pd.DataFrame(tar_list, columns=['IP', 'Exploited?', 'Exploit', 'SID', 'Backdoor', 'Status'])
        if exploited:
            df = df[df['Exploited?'] == True].reset_index(drop=True)
        
        df.index = df.index+1
        return df

    def set_backdoor(self, target, backdoor_port):
        self.targets[target.ip].backdoor = True
        self.targets[target.ip].backdoor_port = backdoor_port
        self.hosts_table.report(target.ip, info='{\"backdoor_port\":\"'+backdoor_port+'\"}')

    def get_unique_port(self):
        port = 8080

        while any(t.backdoor and int(t.backdoor_port) == port for t in self.targets.values()):
            port += 1
        
        return str(port)


class Target():
    def __init__(self, ip):
        self.ip = ip
        self.how_exploited = None
        self.sid = None
        self.backdoor = False
        self.backdoor_port = None
        self.update_online_status()
    
    def is_exploited(self):
        return self.sid is not None

    def update_online_status(self):
        if self.ip is not None:
            response = os.system("ping -c 1 " + self.ip + " >/dev/null 2>&1")
            # and then check the response...
            if response == 0:
                self.status = "Online"
            else:
                self.status = "Offline"
        else:
            self.status = "Offline"

    def stop_session(self):
        self.sid = None
        self.how_exploited = None