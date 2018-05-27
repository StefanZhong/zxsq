# 知识星球数据抓取

本工具用于自动连接到已经付费的知识星球，下载所有的文章。
后续可以跟根据需要过滤一些数据，生成Word文档，方便打印学习。

源代码基于Python3.6。需要用的第三方库请自行用pip3下载。
需要安装的包有，reqeusts,pymongo,python-docx

学习理财、财经知识可以到知识星球搜索“老齐的读书圈”和“齐俊杰的粉丝群”，都很不错。代码中就拿这两个星球做为例子。

有疑问请发邮件至zhm1027@foxmail.com


# headers.txt
该文件最为关键，用于存放cookies和其它header里的内容,没有正确的cookies自然不能下载数据。
首先在网页中登录知识星球，然后直接从Network中找到对应的Request，再将Request Hearder复制过来就可以。

# group.ini
用于记录每个星球上次下载的时间，避免重复下载数据。

# Zsxq.ini
用于配置知识星球的各种URL，其中版本号更新得会快一些。
DOWNLOAD_FILE_FLAG用于配置是否在下载文章的同时下载对应的文件（如果有的话）。

# Zsxq.py
用于下载数据，请根据自己的需要修改星球的名称、ID以及星主ID。

# DataHandler
用于处理下载来的数据，本代码中为将与星主相关的对话保存成Word文档。




