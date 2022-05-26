# 使用基础镜像
FROM python:3.9.11-buster
RUN pip3 install -r requirements.txt -i https://pypi.douban.com/simple