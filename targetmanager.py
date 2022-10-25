import pandas as pd
import json
import os
from pymetasploit3.msfrpc import MeterpreterSession

'''
This class manages all the targets found within the metasploit database
'''
class TargetManager():
    def __init__(self, hosts_table):
        self.hosts_table = hosts_table
        self.targets = {}
        return


    '''Returns target with specified IP'''
    def get_target(self, ip):
        return self.targets[ip]


    '''Parses a dictionary containing host information to target classes and stores them'''
    def parse_targets_from_host(self, hosts):
        hosts = filter(lambda x: 'Windows' in x['os_name'], hosts)

        for host in hosts:
            ip = host['address']
            
            self.targets[ip] = Target(ip)
            info = host['info']
            if info != '':
                info: dict = json.loads(host['info'])
                if 'backdoor_port' in info.keys():
                    self.targets[ip].backdoor = True
                    self.targets[ip].backdoor_port = info['backdoor_port']


    '''Return the target dictionary'''
    def get_targets_dict(self):
        return self.targets


    '''Returns the targets as a pandas dataframe, optionally specify to return only exploited targets'''
    def get_targets_df(self, exploited=False):
        tar_list = []
        for i, t in enumerate(self.targets.values()):
            tar_list.append([t.ip, t.is_exploited(), t.how_exploited, None if t.session is None else t.session.sid, t.backdoor, t.status])

        df = pd.DataFrame(tar_list, columns=['IP', 'Exploited?', 'Exploit', 'SID', 'Backdoor', 'Status'])
        if exploited:
            df = df[df['Exploited?'] == True].reset_index(drop=True)
        
        df.index = df.index+1
        return df


    '''
    Sets the backdoor of the target using  a specified port. 
    Persist the backdoor withn the info field of the metasploit 
    database so backdoor can be used across successive script executions
    '''
    def set_backdoor(self, target, backdoor_port):
        self.targets[target.ip].backdoor = True
        self.targets[target.ip].backdoor_port = backdoor_port
        self.hosts_table.report(target.ip, info='{\"backdoor_port\":\"'+backdoor_port+'\"}')


    '''
    Returns a unique port to use for a backdoor 
    (i.e. a port that has not been used by other targets for backdoor)
    '''
    def get_unique_port(self):
        port = 8080
        while any(t.backdoor and int(t.backdoor_port) == port for t in self.targets.values()):
            port += 1
        return str(port)


    '''Update all hosts statuses'''
    def update_online_statuses(self):
        for target in self.targets.values():
            target.update_online_status()


'''
Stores and controls information for a particular target host
'''
class Target():
    def __init__(self, ip):
        self.ip = ip
        self.how_exploited = None
        self.session : MeterpreterSession = None
        self.backdoor = False
        self.backdoor_port = None
        self.update_online_status()
    

    def is_exploited(self):
        return self.session is not None


    '''
    Check whether the host is online by sending a single ping.
    Change the status (Online/Offline) depending on response success.
    '''
    def update_online_status(self):
        if self.ip is not None:
            response = os.system("ping -c 1 " + self.ip + " >/dev/null 2>&1")
            if response == 0:
                self.status = "Online"
            else:
                self.status = "Offline"
                self.stop_session()
        else:
            self.status = "Offline"
            self.stop_session()


    '''Stop the meterpreter session associated with the target'''
    def stop_session(self):
        if self.session is not None:
            self.session.stop()
            self.session = None
            self.how_exploited = None