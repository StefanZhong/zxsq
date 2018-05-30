#!/usr/bin/python3
# -*- coding: UTF-8 -*-


from configparser import ConfigParser
import os, sys


class Group():
    def __init__(self, group_name, group_id, owner_id, sender_name=None,sender=None,
                 SMTP=None, port=None, password=None, last_dl_time=None):
        self.group_name = group_name  # 星球名称
        self.group_id = int(group_id)  # 星球ID号
        self.owner_id = int(owner_id)  # 星球创始人ID号
        self.sender_name = sender_name  # 发送邮件的邮箱地址
        self.sender = sender  # 发送邮件的邮箱地址
        self.SMTP = SMTP  # SMTP服务器IP
        self.port = port  # 端口
        self.password = password  # 发件邮箱密码
        self.last_dl_time = last_dl_time  # 上一次下载数据的时间

    def __str__(self):
        return self.group_name

    def update_last_dl_time(self, last_dl_time):
        self.last_dl_time = last_dl_time
        config = ConfigParser()
        config.read("groups.ini", encoding='utf-8')
        config[str(self.group_id)]['LastDownloadTime'] = last_dl_time
        with open('groups.ini', 'w', encoding='utf-8') as configfile:
            config.write(configfile)

    @classmethod
    def load_groups(self):
        config = ConfigParser()
        config.read("groups.ini", encoding='utf-8')
        groups = []

        for section in config.sections():
            if section != 'DEFAULT':
                group = Group(config[section]['GROUP_NAME'],
                              config[section]['GROUP_ID'],
                              config[section]['OWNER_ID'])
                if 'SENDER' in config[section].keys():
                    group.sender_name = config[section]['SENDER_NAME']
                    group.sender = config[section]['SENDER']
                    group.password = config[section]['PASSWORD']
                    group.port = config[section]['PORT']
                    group.SMTP = config[section]['SMTP']
                if 'lastdownloadtime' in config[section].keys():
                    group.last_dl_time = config[section]['lastdownloadtime']
                groups.append(group)
        if len(groups) > 0:
            return groups


def log(s):
    mode = 'a'
    log_file = 'log.txt'
    with open(log_file, mode) as f:
        import time, os
        print(s)
        f.write(time.strftime('[%Y-%m-%d %H:%M:%S]') + s + os.linesep)
        import traceback
        if sys.exc_info()[0]:
            traceback.print_exc(file=f)
            traceback.print_exc()


try:

    # print(sys.path[0])

    os.chdir(sys.path[0])

    config = ConfigParser()
    config.read("Zsxq.ini")
    ZSXQ_VERSION = config['DEFAULT'].get('zsxq_version')
    TOPICS_URL = config['DEFAULT'].get('topics_url')
    FILE_URL = config['DEFAULT'].get('file_url')
    DOWNLOAD_FOLDER = config['DEFAULT'].get('download_folder')
    IMAGE_FOLDER = config['DEFAULT'].get('image_folder')
    TEMP_FOLDER = config['DEFAULT'].get('TEMP_FOLDER')
    DOWNLOAD_FILE_FLAG = config['DEFAULT'].get('DOWNLOAD_FILE_FLAG')

    GROUPS = Group.load_groups()


except Exception as e:
    log('Config failed. ' + str(e.args))

    #
