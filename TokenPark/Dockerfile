# base image
FROM python:3.6.5-alpine3.6
MAINTAINER zyt

# install compile environment
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev jpeg-dev zlib-dev
## docker's timezone use UTC, but our timezone is CST, so we need to reset docker's zonetime.
RUN apk add --no-cache tzdata
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

# install packages use requirements.txt
COPY requirements.txt .
RUN pip3 install --upgrade pip \
    && pip3 install --no-cache-dir -r requirements.txt \
    && pip3 install --no-cache-dir gunicorn

# create dir and copy project to dir
# PROJECT 是项目的名称，比如本项目为 TokenPark
# 你可以在构建镜像前，在文件中修改，也可以在构建时用 --build-arg PROJECT=<project_name> 进行指定
ARG PROJECT=TokenPark

RUN mkdir -p /data/${PROJECT} && mkdir -p /data/logs
VOLUME ["/data/logs", "/data/${PROJECT}"]
COPY . /data/${PROJECT}
WORKDIR /data/${PROJECT}
EXPOSE 5001
CMD ["gunicorn", "--workers=3", "--bind=0.0.0.0:5001", "api:app", "--preload"]
