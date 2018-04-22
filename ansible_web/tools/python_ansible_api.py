# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# this is the Interface package of Ansible2 API
#

from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from tempfile import NamedTemporaryFile
from ansible.plugins.callback import CallbackBase
from ansible.errors import AnsibleParserError
import os
import json


class ResultCallback(CallbackBase):
    def __init__(self, display=None, option=None):
        # super().__init__(display, option)
        self.result = None
        self.error_msg = None

    def v2_runner_on_ok(self, result, **kwargs):
        res = getattr(result, '_result')
        self.result = res
        self.error_msg = res.get('stderr')

    def v2_runner_on_failed(self, result, ignore_errors=None, **kwargs):
        if ignore_errors:
            return
        res = getattr(result, '_result')
        self.error_msg = res.get('stderr', '') + res.get('msg')

    def runner_on_unreachable(self, host, result, **kwargs):
        if result.get('unreachable'):
            self.error_msg = host + ':' + result.get('msg', '')

    def v2_runner_item_on_failed(self, result, **kwargs):
        res = getattr(result, '_result')
        self.error_msg = res.get('stderr', '') + res.get('msg')

    # def v2_runner_on_ok(self, result, **kwargs):
    #     self.data = json.dumps(result._result, indent=4)

class AnsibleTask(object):
    def __init__(self, targetHost,user,password,os,port):

        Options = namedtuple("Options",
                             ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection', 'module_path', 'forks',
                              'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',
                              'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check'])
        self.options = Options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh',
                               module_path='/usr/lib/python2.7/site-packages/ansible/modules', forks=100, remote_user=None, private_key_file=None,
                               ssh_common_args=None,
                               ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=False,
                               become_method=None, become_user=None, verbosity=0, check=False)

        # initialize needed objects
        self.variable_manager = VariableManager()


        # self.options = Options(
        #                   listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh',
        #                   module_path='/usr/lib/python2.7/site-packages/ansible/modules', forks=100,
        #                   remote_user='root', private_key_file=None, ssh_common_args=None, ssh_extra_args=None,
        #                   sftp_extra_args=None, scp_extra_args=None, become=False, become_method=None, become_user='root',
        #                   verbosity=None, check=False
        #               )
        self.passwords = {}
        self.loader = DataLoader()
        hosts = '''{host} ansible_ssh_user="{user}"  ansible_ssh_pass="{password}" ansible_ssh_port={port}'''.format(host=targetHost,user=user,password=password,port=port)
        if os=="windows":
            hosts=hosts+""" ansible_connection="winrm" ansible_winrm_server_cert_validation=ignore"""
        # create inventory and pass to var manager
        self.hostsFile = NamedTemporaryFile(delete=False)
        # self.hostsFile.write()
        self.hostsFile.write("""[run_hosts]
        %s
        """ % hosts)
        self.hostsFile.close()
        self.inventory = Inventory(loader=self.loader, variable_manager=self.variable_manager, host_list=self.hostsFile.name)
        self.variable_manager.set_inventory(self.inventory)




    def ansiblePlay(self, module,args):
        # create play with tasks
        # args = "ls /"
        play_source =  dict(
                name = "Ansible Play",
                hosts = 'all',
                gather_facts = 'no',
                tasks = [
                    dict(action=dict(module=module, args=args), register='shell_out'),
                ]
            )
        print "Ansible:"
        print play_source
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)

        # run it
        results_callback = ResultCallback()
        tqm = None
        try:
            tqm = TaskQueueManager(
                      inventory=self.inventory,
                      variable_manager=self.variable_manager,
                      loader=self.loader,
                      options=self.options,
                      passwords=self.passwords,
                      stdout_callback=results_callback,
                  )
            result = tqm.run(play)
            if results_callback.error_msg:
                results_callback.result = { 'msg': "地址或用户名错误，主机连接失败",'flag': False}
            else:
                if results_callback.result==None:
                    data={ 'msg': "执行命令有问题或执行不成功",'flag': False}
                    return data
                else:
                    results_callback.result["flag"]=True
            return results_callback.result
        except AnsibleParserError:
            code = 1001
            results = { 'msg': "地址或用户名错误，主机连接失败",'flag': False}
            return code, results
        finally:
            if tqm is not None:
                tqm.cleanup()
                os.remove(self.hostsFile.name)
                self.inventory.clear_pattern_cache()
            # return json.loads(results_callback.data)


if __name__ =='__main__':
    runner = AnsibleTask("47.94.147.210")
    a=runner.ansiblePlay(module='setup',args='')
    print a