#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import requests
import time
from requests import RequestException
from urllib.parse import quote
import json
from PrepareHeaders import getHeadersFromText
import re
from Config import *
import configparser
import os



class Downloader():

    def __init__(self, group_id, owner_id, callback):
        self.group_id = group_id
        self.owner_id = owner_id
        self.count = 0
        self.process_data = callback
        self.config = configparser.ConfigParser()
        self.group_log_file = 'groups.ini'
        self.config.read(self.group_log_file)

    def get_file_download_url(self, file_id):
        try:
            url = FILE_URL.format(ZSXQ_VERSION, file_id)
            response = requests.get(url, headers=getHeadersFromText())
            fileDic = json.loads(response.text)
            fileLink = fileDic['resp_data']['download_url']
            return fileLink
        except Exception as e:
            print('get_file_download_url error:', e.args)
            return None

    def download_file(self, url, file_name):
        import os
        if os.path.exists(file_name):
            return True
        file_res = requests.get(url)
        if file_res.status_code == 200:
            # print(len(file_res.content))
            print('1 file downloaded.')
            with open(file_name, 'wb') as f:
                f.write(file_res.content)
                return True
        else:
            return False

    def process_topics(self, url, stop_time):
        try:
            topics_page = requests.get(url, headers=getHeadersFromText())
            earliest_time = None
            if topics_page.status_code == 200:
                resp_data = json.loads(topics_page.text)
                if not resp_data['succeeded']:
                    print('Get topics failed.', topics_page.text)
                    return None
                if resp_data and 'topics' in resp_data['resp_data'].keys():
                    for topic in resp_data['resp_data']['topics']:
                        if (stop_time and
                                (time.mktime(time.strptime(topic['create_time'][:19],
                                                           '%Y-%m-%dT%H:%M:%S')) <= stop_time)):
                            return None
                        if callable(self.process_data):
                            self.process_data(topic)
                        earliest_time = topic['create_time']
                        self.count += 1
                        # if file need to be downloaded, then download the file
                        if (DOWNLOAD_FILE_FLAG == 'True' and topic['type'] == 'talk'
                                and topic['talk']['owner']['user_id'] == self.owner_id
                                and 'files' in topic['talk'].keys()):
                            for file in topic['talk']['files']:
                                file_url = self.get_file_download_url(file['file_id'])
                                self.download_file(file_url,
                                                   os.path.join(DOWNLOAD_FOLDER, file['name']))
                        maximum = int(re.match(r'.*?count=([\d]+).*?', url).group(1))
                        if len(resp_data['resp_data']['topics']) < maximum:
                            # if the returned row count less than page size then stop the loop
                            return None
                    return earliest_time
                else:
                    log('Get topics failed.' + topics_page.text)
                    return None
        except RequestException as e:
            print('Get topics error.', e.args)
            return None

    def getTimeStr(self, input_time):
        import datetime
        time_format = '%Y-%m-%dT%H:%M:%S.%f'
        new_time = (datetime.datetime.strptime(input_time[:23], time_format)
                    - datetime.timedelta(milliseconds=1))

        return datetime.datetime.strftime(new_time, time_format)[:-3] + '+0800'

    def get_topic_list(self, base_url, last_download_time, earliest_time):

        if earliest_time:
            url = base_url + '&end_time=' + quote(earliest_time)
        else:
            url = base_url

        create_time = self.process_topics(url, last_download_time)
        time.sleep(5)
        if create_time:
            print('Got topics till ', create_time)

        if create_time:
            self.get_topic_list(base_url, last_download_time, self.getTimeStr(create_time))

    def start(self, expect_stop_time=None):

        base_url = TOPICS_URL.format(ZSXQ_VERSION, self.group_id)
        if str(self.group_id) not in self.config.sections():
            self.config[str(self.group_id)] = {}
            last_download_time = time.strftime('%Y-%m-%d 00:00:00')
        else:
            last_download_time = self.config[str(self.group_id)]['LastDownloadTime']

            self.config[str(self.group_id)]['LastDownloadTime'] = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(self.group_log_file, 'w') as configfile:
            self.config.write(configfile)

        if expect_stop_time:
            last_download_time = expect_stop_time
        stop_time = time.mktime(time.strptime(last_download_time, '%Y-%m-%d %H:%M:%S'))
        self.get_topic_list(base_url, stop_time, None)
        if self.count:
            log('Downloaded {} topics.'.format(self.count))


def process_data(topic):
    with open(os.path.join(TEMP_FOLDER, 'Topic_{}.txt').format(topic['topic_id']),
              'w', encoding='utf-8') as f:
        f.write(json.dumps(topic))


def download():
    #初始化两个星球，三个字段分别为：星球名称，星球ID号，星球创始人ID号。
    #ID号可以从浏览器检查网页中的Network中获取。
    groups = [('老齐的读书圈', 454548818428, 88288542115152),
              ('齐俊杰的粉丝群', 552521181154, 88288542115152)]

    for group in groups:
        print('Downloading {}...'.format(group[0]))
        Downloader(group[1], group[2], process_data).start()


if __name__ == '__main__':
    download()
