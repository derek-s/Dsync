# -*- coding:UTF-8 -*-
#---- main.py ----
#Dsync 基于Python与rsync的监视同步工具
#2016-12-6 Ver 1.0


import sys
import time
import logging
import os
import sys
import pexpect
import string
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from watchdog.events import LoggingEventHandler
import yaml


#读取配置文件
f = open('_config.yml','r')
config = yaml.load(f.read())


#远程主机参数
remoteHost = config['host']
remoteLogin = config['user']
remotePasswd = config['passwd']
remoteDir = config['remotedir']

#本地监控目录
localDir = config['localdir']

def pexpectRun(cmd):
    #调用pexpect创建rsync子线程，带log输出到系统标准输出
    ssh = pexpect.spawn(cmd,[],86400,logfile=sys.stdout)
    try:
        while True:
            #对输出进行匹配，匹配输入密码或者保存ssh密匙
            i = ssh.expect(['password', 'continue connecting (yes/no)?'])
            if i == 0:
                ssh.sendline(remotePasswd)
                break
            elif i == 1:
                ssh.sendline('yes')
    except pexpect.EOF:
        #处理进程退出
        ssh.close()
    else:
        ssh.expect(pexpect.EOF)
        ssh.close()
             
    print "Done"


#创建文件远程处理
def rsyncFile(file):
    "创建文件远程处理模块，接收文件名，可带目录形式，如： /未命名文件夹/无标题文档"
    #合并路径并解决空格替换
    localFile = os.path.join(localDir,file.replace(' ','\ '))
    remoteFile = os.path.join(remoteDir,file.replace(' ','\ '))
    #rsync命令
    cmd = 'rsync -avz -s %s %s@%s:%s' % (localFile,remoteLogin,remoteHost,remoteFile)
    print cmd
    pexpectRun(cmd)

    

#删除文件处理，强同步，本地删除文件时会比较远程与本地文件，远程存在且本地不存在的文件将一律删除
def deleteFile():
    cmd = 'rsync -avz --delete %s %s@%s:%s' % (localDir,remoteLogin,remoteHost,remoteDir)
    print cmd
    pexpectRun(cmd)

def modifiedFile():
    cmd = 'rsync -avz %s %s@%s:%s' % (localDir,remoteLogin,remoteHost,remoteDir)
    print cmd
    pexpectRun(cmd)


#监控事件类
class DwPatternMatchingEventHandler(PatternMatchingEventHandler,LoggingEventHandler):
    "重写Watchdog监控事件"
    #创建事件
    def on_created(self,event):
        logging.info("Created file: %s",event.src_path)
        name = event.src_path.split(localDir)
        watchname = name[-1].decode('utf8')
        rsyncFile(watchname)
    #删除事件
    def on_deleted(self,event):
        logging.info("Deleted file: %s",event.src_path)
        deleteFile()
    #修改事件
    def on_modified(self,event):
        logging.info("Modified file: %s",event.src_path)
        modifiedFile()
    #移动事件
    def on_moved(self,event):
        logging.info("Moved file: %s",event.src_path)
        deleteFile()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    
    event_handler = DwPatternMatchingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, localDir, recursive=True)
    observer.start()
    try:
        logging.info("Observer start")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shtting down watcher")
        observer.stop()
    observer.join()