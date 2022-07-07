FROM python:3.8
RUN \
    apt-get update && \
    apt-get install -y ffmpeg && \
    pip3 install Django==4.0.6
