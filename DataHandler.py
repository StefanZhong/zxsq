#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import requests
import json
from PrepareHeaders import getHeadersFromText
from Config import *
import os, glob
from DocxHelper import DocxHelper
import datetime

def replace_special(text):
    s = ['*','.', '?', '+', '$', '^', '[', ']', '(', ')', '{', '}', '|', '\\']
    text2 = ''
    for c in text:
        if c in s:
            c = '\\' + c
        text2 += c
    return text2

class DataHandler():
    def __init__(self, group, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.group = group

    def get_file_download_url(self, file_id):
        try:

            url = FILE_URL.format(ZSXQ_VERSION, file_id)
            response = requests.get(url, headers=getHeadersFromText())
            fileDic = json.loads(response.text)
            fileLink = fileDic['resp_data']['download_url']
            return fileLink
        except Exception as e:
            print('get_file_download_url error:', e.args)
            raise (e)

    def get_links(self, text):
        s = ''
        try:
            import re
            import urllib.request
            # text1 = text
            text = urllib.request.unquote(text)
            result = re.findall('<e type="web" href="(.*?)".*?title="(.*?)".*?/>', text)

            links = []

            if result:
                for link in result:
                    s = re.findall(r'<e type="web" href="{}".*?title="{}".*?/>'.format(replace_special(link[0]), replace_special(link[1])), text)

                    text = text.replace(s[0], '')
                    links.append((link[1], link[0]))

            title = re.findall('<e type="mention".*?title="(.*?)"', text)
            if title:
                for t in title:
                    s = re.findall(r'<e type="mention".*?title="{}".*?/>'.format(replace_special(t)), text)
                    text = text.replace(s[0], t)
            return text, links
        except Exception as e:
            print('出错',text,e)
            return text, []

    def get_file_links(self, topic):
        file_links = []
        if 'files' in topic['talk'].keys():
            files = topic['talk']['files']
            if files:
                for file in files:
                    file_name = file['name']
                    file_id = file['file_id']
                    file_link = self.get_file_download_url(file_id)
                    file_links.append((file_name, file_link))
        return file_links

    def download_image(self, link):

        import os
        import hashlib
        # file_name = link.split('/')[-1]
        file_name = hashlib.md5(link.encode('utf-8')).hexdigest() + '.jpg'
        file_name = os.path.join(IMAGE_FOLDER, file_name)

        import os
        if os.path.isfile(file_name):
            with open(file_name, 'rb') as f:
                if len(f.read()) // 1024 > 55:  # ignore big picture.
                    return None
            return file_name

        file_res = requests.get(link)

        if file_res.status_code == 200:
            with open(file_name, 'wb') as f:
                if len(file_res.content) // 1024 > 55:  # ignore big picture.
                    return None
                f.write(file_res.content)

                return file_name
        else:
            return False

    def get_images(self, topic, type):
        images = []
        if 'images' in topic[type].keys():
            for image in topic[type]['images']:

                file_name = self.download_image(image['thumbnail']['url'])
                if file_name:
                    images.append(file_name)

        return images

    def save_to_word(self, topics, date):
        try:
            file_name = '{}发贴及问答汇总{}.docx'.format(self.group.group_name, date.replace('-', ''))
            file_name = os.path.join(TEMP_FOLDER, file_name)
            doc = DocxHelper(file_name)

            qa_topics = []
            talks = []
            for topic in topics:
                if topic['type'] == 'talk':

                    if self.group.owner_id == topic['talk']['owner']['user_id']:

                        text = topic['talk']['text']
                        text, links = self.get_links(text)
                        file_links = self.get_file_links(topic)

                        talks.append((text, topic['create_time'],
                                      self.get_images(topic, 'talk'), links, file_links))
                    else:

                        if topic['comments_count'] == 0:
                            continue
                        owner_comment = ''
                        if 'show_comments' not in topic.keys():
                            continue
                        for comment in topic['show_comments']:
                            if comment['owner']['user_id'] == self.group.owner_id:
                                owner_comment = comment['text']
                        if owner_comment:
                            text = topic['talk']['text']

                            text, links = self.get_links(text)
                            qa_topics.append((text, owner_comment, topic['create_time'],
                                              self.get_images(topic, 'talk'), [], links))

                elif topic['type'] == 'q&a':
                    text = topic['question']['text']

                    text, links = self.get_links(text)
                    answer = topic['answer']['text']

                    answer, links2 = self.get_links(answer)
                    qa_topics.append((text, answer, topic['create_time'],
                                      self.get_images(topic, 'question'), self.get_images(topic, 'answer'), links))
            if len(talks) > 0:
                for talk in talks:
                    doc.add_Talk(*talk)
            if len(qa_topics) > 0:
                for qa_topics in qa_topics:
                    doc.add_QA(*qa_topics)

            doc.save()
            print('成功导出Word文档，位置在{}'.format(file_name))
            return file_name
        except Exception as e:
            log('Save to word failed. {}'.format(e.args))
            return None

    def load_data(self):

        files = glob.glob(TEMP_FOLDER + os.path.sep + "Topic_*.txt")

        if files:
            topics = []
            for file in files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = f.read()
                        topic = json.loads(data)

                        if topic['group']['group_id'] == self.group.group_id \
                                and topic['create_time'][:10] == self.start_date:
                            topics.append(topic)
                            # os.remove(file)
                except Exception as e:
                    log('Load data from {} failed. {}'.format(file, e.args))

            if len(topics) > 0:
                return sorted(topics, key=lambda topic: topic['create_time'])

        return None

    def run(self, callback):

        # date为文章所在日期

        topics = self.load_data()

        if topics:

            word = self.save_to_word(topics, self.start_date)

            if callback and callable(callback):
                callback(self.group, word, self.start_date)
                # callback用于后续操作，提供三个参数，
                # 星球详情，Word路径, 日期，可以用来发邮件。


def do_something(group, word, date):
    print(group, word, date)


if __name__ == '__main__':
    start_date = datetime.datetime.now() - datetime.timedelta(days=1)
    start_date = datetime.datetime.strftime(start_date, '%Y-%m-%d')

    DataHandler(GROUPS[0], start_date, None).run(do_something)
