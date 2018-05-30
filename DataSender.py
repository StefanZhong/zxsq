#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from EmailHelper import EmailHelper
from DataHandler import DataHandler
import configparser
from Config import *


class DataSender:

    def send_email(self, group, word, date):

        print('Creating the email...')

        em = EmailHelper()
        mail = em.create_mail(group.sender_name, group.sender,
                              '{}每日更新 - {}'.format(group.group_name, date))
        mail_file = open('Mail_Message', encoding='utf-8')
        mail_msg = mail_file.read()
        em.add_content(mail_msg, mail)
        em.attach_file(word, mail)

        receivers = []
        with open('subscriber_{}.txt'.format(group.group_id), encoding='utf-8') as f:
            for address in f.readlines():
                receivers.append(address.strip())

        if len(receivers):
            em.send_email_ssl(group.sender, receivers, mail,
                              group.SMTP, group.port,
                              group.sender, group.password)


if __name__ == '__main__':
    try:
        import datetime
        import sys

        start_date = datetime.datetime.now() - datetime.timedelta(days=1)
        start_date = datetime.datetime.strftime(start_date, '%Y-%m-%d')

        for group in GROUPS:

            if len(sys.argv) > 1 and int(sys.argv[1]) != group.group_id:
                continue

            sender = DataSender()
            DataHandler(group, start_date, None).run(sender.send_email)
    except Exception as e:
        log('Send data failed. {}'.format(e.args))
