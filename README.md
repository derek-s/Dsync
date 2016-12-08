# Dsync

监控本地目录并同步到远程计算机

使用Python 2.7开发，配合Rsync进行同步工作，理论支持所有Linux发行版，如需要在Windows上使用，请安装Cygwin等环境。

###所需依赖

    logging pexpect watchdog yaml

### 需要安装Rsync

    #Fedora/Redhat
    yum install rsync -y
    
    #Ubunut/Debain
    apt-get install rsync -y

如果你对这个工具感兴趣，可以关注：

https://www.dadclab.com/archives/6580.jiecao
