#!/usr/bin/python3
# -*- coding: UTF-8 -*-


import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

from email.utils import formataddr


class EmailHelper:

    def create_mail(self, sender_name, sender_email, subject):

        msgRoot = MIMEMultipart('related')
        msgRoot['From'] = formataddr([sender_name, sender_email])
        msgRoot['Subject'] = Header(subject, 'utf-8')

        return msgRoot

    def attach_image(self, file_name, content_id, msgRoot):
        fp = open(file_name, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', '<' + content_id + '>')  # '<image1>'
        msgRoot.attach(msgImage)
        return '<p><img src="cid:{}"></p>'.format(content_id)

    def add_content(self, mail_msg, mail):
        msgAlternative = MIMEMultipart('alternative')
        msgAlternative.attach(MIMEText(mail_msg, 'html', 'utf-8'))
        mail.attach(msgAlternative)

    def attach_file(self, file_name, mail, encoding='utf-8'):
        file = MIMEText(open(file_name, 'rb').read(), 'base64', encoding)
        file["Content-Type"] = 'application/octet-stream'
        file.add_header("Content-Disposition", "attachment",
                        filename=("gbk", "", os.path.split(file_name)[1]))

        mail.attach(file)

    def send_email(self, sender, receivers, mail, server):
        try:
            smtpObj = smtplib.SMTP(server)
            smtpObj.sendmail(sender, receivers, mail.as_string())
            print('Email sent.')
            return True
        except smtplib.SMTPException:
            print('Email failed.')
            return False

    def send_email_ssl(self, sender, receivers, mail, server, port, account, password):
        try:
            server = smtplib.SMTP_SSL(server, port)
            server.login(account, password)
            server.sendmail(sender, receivers, mail.as_string())
            server.quit()
            print('Email sent.')
            return True
        except smtplib.SMTPException as e:
            print('Email failed.{}'.format(e))
            return False


if __name__ == '__main__':
    print('Creating the email...')
    from Config import *
    import datetime


    start_date = datetime.datetime.now() - datetime.timedelta(days=1)
    start_date = datetime.datetime.strftime(start_date, '%Y-%m-%d')

    group = GROUPS[0]

    em = EmailHelper()
    mail_msg = """
    Hi There,<p></p>This is a test email from {0}.
        <p></p>
         Best regards,<p></p>{0}
    """.format(group.sender_name)

    mail = em.create_mail(group.sender_name, group.sender,
                          '{}每日更新 - {}'.format('朋友圈', start_date)
                          )
    em.add_content(mail_msg, mail)

    # em.attach_file(r"C:\test.txt", mail)

    receivers = []
    with open('test_subscriber_{}.txt'.format(group.group_id), encoding='utf-8') as f:
        for address in f.readlines():
            receivers.append(address.strip())

    if len(receivers):
        em.send_email_ssl(group.sender, receivers, mail,
                          group.SMTP, group.port,
                          group.sender, group.password)