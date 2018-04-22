# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

from rest_framework import status
from rest_framework import request
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ansible_web.tools.python_ansible_api import AnsibleTask

import sys

reload(sys)
sys.setdefaultencoding( "utf-8" )
import json

class CE():
    pass

@api_view(['GET','POST'])
def QueryHost(request):
    datajs=json.loads(request.body)
    print "\nQueryHost:"
    print "接受参数："
    print datajs
    repdata = {"error_code":0,"data":{}}
    host=datajs["ce_ip"]
    user=datajs["ssh_username"]
    password=datajs["ssh_password"]
    os=datajs["os"]
    port = datajs["ce_port"]
    runner = AnsibleTask(host, user, password, os, port)
    a = runner.ansiblePlay(module='setup', args='')
    if a["flag"] == True:
        data = a["ansible_facts"]
        # 物理内存容量
        repdata["data"]["mem_total"] = data["ansible_memtotal_mb"]
        # 虚拟内容容量
        repdata["data"]["swap_total"] = data["ansible_memory_mb"]["swap"]["total"]
        # CPU型号
        repdata["data"]["cpu_type"] = data["ansible_processor"][-1]
        # CPU核心数
        repdata["data"]["cpu_total"] = data["ansible_processor_vcpus"]
        # 操作系统类型
        repdata["data"]["os_type"] = " ".join((data["ansible_distribution"], data["ansible_distribution_version"]))
        # 硬盘总容量
        # disk_total = sum([int(data["ansible_devices"][i]["sectors"]) * \
        #                           int(data["ansible_devices"][i]["sectorsize"]) / 1024 / 1024 / 1024 \
        #                           for i in data["ansible_devices"] if i[0:2] in ("sd", "ss")])
        repdata["data"]["disk_total"] = data["ansible_devices"]["vda"]["size"]
        # 硬盘挂载名及容量
        mounts=len(data["ansible_mounts"])
        repdata["data"]["disk_mount"] =''
        print mounts
        for i in range(0,mounts):
            print(i)
            repdata["data"]["disk_mount"]='%s挂载目录：%s，磁盘大小：%sG；' % (repdata["data"]["disk_mount"], data["ansible_mounts"][i]["mount"], data["ansible_mounts"][i]["size_total"]/ 1024 / 1024 / 1024)
        # 服务器型号
        repdata["data"]["server_type"] = data["ansible_product_name"]
        # 服务器主机名
        repdata["data"]["host_name"]= data["ansible_hostname"]
        # 操作系统内核型号
        repdata["data"]["os_kernel"] = data["ansible_kernel"]
        # 服务器ipv4地址
        repdata["data"]["ipv4"] = ','.join(data["ansible_all_ipv4_addresses"])
        repdata["error_code"] = 1
    else:
        repdata["data"]=a
    print "返回参数："
    print repdata
    return Response(repdata, status=status.HTTP_200_OK, template_name=None, headers={"Access-Control-Allow-Origin": "*"})

@api_view(['GET','POST'])
def ping(request):
    datajs = json.loads(request.body)
    print "\nping:"
    print "接受参数："
    print datajs
    repdata = {"error_code":0,"data":{}}
    host=datajs["ce_ip"]
    user=datajs["ssh_username"]
    password=datajs["ssh_password"]
    os=datajs["os"]
    port = datajs["ce_port"]
    pingHost=datajs["ping"]
    runner = AnsibleTask(host, user, password, os, port)
    a = runner.ansiblePlay(module='shell', args='ping {ping} -c 4'.format(ping=pingHost))
    if a["flag"] == True:
        repdata["starttime"] = a["start"]
        repdata["endtime"] = a["end"]
        vll = {}
        for line in a["stdout_lines"]:
            if line.find("rtt") >= 0:
                b = str(line).lstrip("tr").strip().split("=")
                name = str(b[0]).split("/")
                val = str(b[1]).strip().split("/")
                for num in range(0, len(name)):
                    if name[num]=="avg":
                        vll["delay_average"] = val[num]
                    elif name[num]=="min":
                        vll["delay_minnum"] = val[num]
                    elif name[num]=="max":
                        vll["delay_maxnum"] = val[num]
                    else:
                        vll[name[num]] = val[num]

            if line.find("4 packets") >= 0:
                loss = line.split(",")[2].split(" ")
                while '' in loss:
                    loss.remove('')
                vll["packet_loss"]=loss[0]
        repdata["data"] = vll
        repdata["error_code"] = 1
    print "返回参数："
    print repdata
    return Response(repdata, status=status.HTTP_200_OK, template_name=None, headers={"Access-Control-Allow-Origin": "*"})

@api_view(['GET','POST'])
def sysstat(request):
    datajs = json.loads(request.body)
    print "\nping:"
    print "接受参数："
    print datajs
    repdata = {"error_code":0,"data":{}}
    host=datajs["ce_ip"]
    user=datajs["ssh_username"]
    password=datajs["ssh_password"]
    os=datajs["os"]
    port = datajs["ce_port"]
    runner = AnsibleTask(host, user, password, os, port)
    a = runner.ansiblePlay(module='shell', args='sar -ur -n DEV 1 3 |grep Average')
    if a["flag"] == True:
        repdata["data"]["starttime"] = a["start"]
        repdata["data"]["endtime"] = a["end"]
        vll = {}
        line=a["stdout_lines"]
        cpu=line[1].split(' ')
        while '' in cpu:
            cpu.remove('')

        repdata["data"]["cpu_user"] = cpu[2]
        repdata["data"]["cpu_nice"] = cpu[3]
        repdata["data"]["cpu_system"] = cpu[4]
        repdata["data"]["cpu_steal"] = cpu[6]
        repdata["data"]["cpu_idle"] = cpu[7]
        Memory=line[3].split(' ')
        while '' in Memory:
            Memory.remove('')

        repdata["data"]["kbmemfree"] = Memory[1]
        repdata["data"]["kbmemused"] = Memory[2]
        repdata["data"]["memused"] = Memory[3]
        dev=line[5].split(' ')
        while '' in dev:
            dev.remove('')

        repdata["data"]["rxbyt"] = cpu[4]
        repdata["data"]["txbyt"] = cpu[5]
        repdata["error_code"] = 1
    print "返回参数："
    print repdata
    return Response(repdata, status=status.HTTP_200_OK, template_name=None, headers={"Access-Control-Allow-Origin": "*"})


@api_view(['GET','POST'])
def  statusHost(request):
    datajs = json.loads(request.body)
    print "\nstatusHost:"
    print "接受参数："
    print datajs
    repdata = {"error_code": 0, "data": {}}
    host=datajs["ce_ip"]
    user=datajs["ssh_username"]
    password=datajs["ssh_password"]
    os=datajs["os"]
    port = datajs["ce_port"]
    runner = AnsibleTask(host, user, password, os,port)

    a = runner.ansiblePlay(module='ping', args='')
    repdata["data"]=a
    if repdata["data"]["flag"]==True:
        repdata["error_code"]=1
    print "返回参数："
    print repdata
    return Response(repdata, status=status.HTTP_200_OK, template_name=None, headers={"Access-Control-Allow-Origin": "*"})

@api_view(['GET','POST'])
def currency(request):
    datajs = json.loads(request.body)
    print "\ncurrency:"
    print "接受参数："
    print datajs
    repdata = {"error_code": 0, "data": {}}
    host=datajs["ce_ip"]
    user=datajs["ssh_username"]
    password=datajs["ssh_password"]
    os=datajs["os"]
    port = datajs["ce_port"]
    module=datajs["module"]
    args=datajs["args"]
    runner = AnsibleTask(host, user, password, os, port)
    a = runner.ansiblePlay(module=module, args=args)
    repdata["data"]=a
    if repdata["data"]["flag"] == True:
        repdata["error_code"] = 1
    print "返回参数："
    print repdata
    return Response(repdata, status=status.HTTP_200_OK, template_name=None, headers={"Access-Control-Allow-Origin": "*"})