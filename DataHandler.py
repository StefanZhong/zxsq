#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import requests
import json
from PrepareHeaders import getHeadersFromText
from Config import *
import os, glob
from DocxHelper import DocxHelper


class DataHandler():
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
        import re
        import urllib.request

        result = re.findall('href="(.*?)"[\s]*title="(.*?)"', urllib.request.unquote(text))
        links = []
        if result:
            text = text[:text.index("<e type=")]
            links.append((result[0][1], result[0][0]))
            # print(result[0][0])
        return text, links

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
        file_name = link.split('/')[-1]

        file_name = os.path.join(IMAGE_FOLDER, file_name)

        import os
        if os.path.isfile(file_name):
            return file_name

        file_res = requests.get(link)
        if file_res.status_code == 200:
            with open(file_name, 'wb') as f:
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

    def save_to_word(self, topics, group_name, date, owner_id):
        try:
            file_name = '{}发贴及问答汇总{}.docx'.format(group_name, date.replace('-', ''))
            file_name = os.path.join(TEMP_FOLDER, file_name)
            doc = DocxHelper(file_name)

            qa_topics = []
            talks = []
            for topic in topics:
                if topic['type'] == 'talk':

                    if owner_id == topic['talk']['owner']['user_id']:

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
                            if comment['owner']['user_id'] == owner_id:
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
            return file_name
        except Exception as e:
            log('Save to word failed. {}'.format(e.args))
            return None

    def load_data(self, group_id, date):
        files = glob.glob(TEMP_FOLDER + os.path.sep + "Topic_*.txt")
        if files:
            topics = []
            for file in files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = f.read()
                        topic = json.loads(data)
                        if topic['group']['group_id'] == group_id \
                                and topic['create_time'][:10] == date:
                            topics.append(topic)
                            # os.remove(file)
                except Exception as e:
                    log('Load data from {} failed. {}'.format(file, e.args))

            if len(topics) > 0:
                return topics

        return None

    def run(self, callback):
        groups = [('老齐的读书圈', 454548818428, 88288542115152),
                  ('齐俊杰的粉丝群', 552521181154, 88288542115152)]
        for group in groups:
            d = DataHandler()
            import datetime

            new_time = datetime.datetime.now() - datetime.timedelta(days=1)
            date = datetime.datetime.strftime(new_time, '%Y-%m-%d')
            # date为文章所在日期
            topics = d.load_data(group[1], date)
            if topics:
                word = d.save_to_word(topics, group[0], date, group[2])
                print('成功导出Word文档，位置在{}'.format(word))
                if callback and callable(callback):
                    callback(word, group[0], date)
                    #callback用于后续操作，提供三个参数，Word路径，group_id, 日期，可以用来发邮件。


if __name__ == '__main__':
    DataHandler().run(None)
