# -*- coding: utf-8 -*-
import os
import re
import subprocess
import pexpect
from pexpect import pxssh
import sys
import threading
import signal
from os import popen
from multiprocessing import Process,Queue,Lock
import multiprocessing
from Queue import Empty as QueueEmpty
import shlex
import psutil
from threading import Thread,Lock
import time
import json
emac = "0050.f112.decc"
dmac = "4458.2945.45c4"
count = 1
interv = 1
gus_ip = '0'
def ue_ping():
    print 'enter ue_ping'
    comm = ""
    # gfile_out = open('udp_store.txt','w')
    # p = subprocess.Popen(comm,shell=True,universal_newlines=True,stdout=gfile_out,close_fds=True).wait()

def calcluate_latency():
    ret = 0
    cmd_cli = './start_capture.sh'

    print cmd_cli
    result = os.system(cmd_cli)
    time.sleep(10)
    print result


def isRunning(process_name):
    try:
        process = len(os.popen('ps aux | grep "' + process_name + '" | grep -v grep').readlines())
        if process >= 1:
            return True
        else:
            return False
    except:
        print("Check process ERROR!!!")
        return False
def enter_vpp(s):
    ret = 0
    print 'exec k8s -e and enter vpp'
    s.sendline('kubectl exec -it cmts-dp-macl3vpp-0 vppctl')
    s.prompt()
    print(s.before)
    time.sleep(2)# lose if 1s

    print 'exec vppctl'   
    # s.sendline('vppctl')
    # s.prompt()
    print(s.before)
    time.sleep(2) #lose to 1s
    return ret

def exec_curl_get_sfid_sid(s):
    CM_MAC = '4458.2945.45c4'
    print 'enable curl to get sfid'

    curl = 'curl -X GET http://127.0.0.1:32307/v1/sf/cm/4458.2945.45c4'
    # p = subprocess.Popen(curl, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    s.sendline(curl)
    s.prompt()
    time.sleep(1)
    result_txt = s.before
    print result_txt
    searchObj = re.search("\[\{.*\}\]",result_txt)
    result_txt = searchObj.group(0)
    # result_txt = result_txt[0:5108]
    print type(result_txt)
    print result_txt
    result_json = json.loads(result_txt)

    for sf in result_json:
        if sf['sfkeys']['sfdir'] == 'SF_DIR_US':
            if sf['sfkeys']['sftype'] == 'SF_TYPE_PRIMARY':
                sid = sf['sfkeys']['sid']
                continue
            if sf['sfkeys']['sftype'] == 'SF_TYPE_SECONDARY':
                sfid = sf['sfkeys']['sfid']
                continue
    print "CM:" + CM_MAC + " Secondary SFID: " + str(sfid) + " Primary SID: " + str(sid)

    # print s.before
    return {"sid":str(sid),"sfid":str(sfid)}


def exec_curl_pgs_enable(s,gus_ip,sfid):
    ret = 0
    print 'enable curl'
    data ="\'" + '{"sf_type":"pgs","grant_interval":1000,"grant_jitter":0,"grant_size":100,"gpi":1,"poll_interval":1000,"poll_jitter":0}' + "\'"
    data2 = '--noproxy '
    data3 = gus_ip + ' ' + gus_ip
    data4 = ':8080/test/pgs/0/0/' + sfid
    cur_com = 'curl -X PUT -d '
    comm = cur_com + data + ' ' + data2 + data3 + data4
    print 'comm' + ' ' +comm
    print 'exec curl enable command and next step'
    s.sendline(comm)
    s.prompt()
    time.sleep(1)
    print s.before
    return ret

def login_ccmts():
    hostname = "10.124.210.201"
    username = "root"
    password = "cisco123"
    s = pxssh.pxssh()
    s.PROMPT = '[$#] '

    s.login(hostname, username, password, auto_prompt_reset=False)

    s.sendline('kubectl get pods -o wide | grep uss')  # run a command
    s.prompt()  # match the prompt
    result = s.before
    # print result  # print everything before the prompt.
    global gus_ip
    searchObj = re.search("\d+\.\d+\.\d+\.\d+", result)
    gus_ip = searchObj.group(0)
    print gus_ip
    time.sleep(1)
    info = exec_curl_get_sfid_sid(s)
    # exec_curl_pgs_enable(s, gus_ip, info["sfid"])
    time.sleep(1)
    enter_vpp(s)
    enable_bwr(s, info["sfid"], info["sid"])
    while 1:
        time.sleep(20)
        calcluate_latency()
        #disable_bwr(s, info["sfid"], info["sid"])
        time.sleep(20)
        calcluate_latency()
        time.sleep(20)
        print "Run for the next time"



def enable_bwr(s, sfid, sid):
    print (s.before)
    print 'Enable BWR:'

    enable_cli = 'usmac test set bwr enable ' + ' sfid ' + sfid + ' sid ' + sid

    s.sendline(enable_cli)
    s.prompt()
    time.sleep(10)
    print s.before
    print 'get enable ping time'

    print time.asctime(time.localtime(time.time()))

def disable_bwr(s,sfid,sid):

    print 'Disable BWR:'

    disable_cli = 'usmac test set bwr disable ' + ' sfid ' + sfid + ' sid ' + sid
    s.sendline(disable_cli)
    s.prompt()
    time.sleep(10)
    print s.before
    print 'get disable ping time'

    print time.asctime(time.localtime(time.time()))

def main():
    ret = -1
    # file_exist()
    ue_ping()
    login_ccmts()

    # p1.start()
    # p2.start()
    # p1.join()
    # p2.join()
    # s.logout()
        
def file_exist():
    print "Directory: %s" %os.listdir(os.getcwd())
    print '\n'
    index = os.path.exists('enable.txt')
    if index == 0:
        print 'file not exist'
    else:
        os.remove('enable.txt')
    index = os.path.exists('disable.txt')
    if index == 0:
        print 'file not exist'
    else:
        os.remove('disable.txt')
    index = os.path.exists('enable_ping.txt')
    if index == 0:
        print 'file not exist'
    else:
        os.remove('enable_ping.txt')
    index = os.path.exists('disable_ping.txt')
    if index == 0:
        print('file not exist')
    else:
        os.remove('disable_ping.txt')
    index = os.path.exists('draw_latency.txt')
    if index == 0:
        print('file not exist')
    else:
        os.remove('draw_latency.txt')
    index = os.path.exists('temp.png')
    if index == 0:
        print('file not exist')
    else:
        os.remove('temp.png')
    index = os.path.exists('udp_store.txt')
    if index == 0:
        print('file not exist')
    else:
        print 'file is here'
        os.remove('udp_store.txt')
    print '\n'
    print "Delete Directory: %s" %os.listdir(os.getcwd())
    time.sleep(1)
if __name__ == "__main__":
    main()
