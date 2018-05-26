#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from EmailHelper import EmailHelper
from DataHandler import DataHandler


def send_email(word, group_name, date):
    print('Creating the email...')
    em = EmailHelper()
    mail = em.create_mail("山顶的巧克力", '32055887@qq.com',
                          '{}每日更新 - {}'.format(group_name, date))
    mail_file = open('Mail_Message', encoding='utf-8')
    mail_msg = mail_file.read()
    em.add_content(mail_msg, mail)
    em.attach_file(word, mail)

    sender = '32055887@qq.com'
    receivers = ['32055887@qq.com']
    SMTP_SERVER = 'smtp.qq.com'

    em.send_email_ssl(sender, receivers, mail, SMTP_SERVER, 465, sender, 'kdrjogjfctobbihc')


if __name__ == '__main__':
    DataHandler().run(send_email)
