#!/usr/bin/python3
# -*- coding: UTF-8 -*-


from configparser import ConfigParser
import os, sys


def log(s):
    mode = 'a'
    log_file = 'log.txt'
    with open(log_file, mode) as f:
        import time, os
        print(s)
        f.write(time.strftime('[%Y-%m-%d %H:%M:%S]') + s + os.linesep)


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

except Exception as e:
    log('Config failed. ' + str(e.args))

    #
