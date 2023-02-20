# syntax=docker/dockerfile:1

FROM ubuntu:latest

RUN apt-get update && \ 
    apt-get upgrade -y && \
    apt-get install -y git python-pip
RUN apt install -y python3-pip

COPY . /zaptube
WORKDIR /zaptube
RUN pip3 install git+https://github.com/ytdl-org/youtube-dl.git@57802e632f5a741df6fd9b30a455c32632944489
RUN pip3 install -r requirements.txt

RUN apt install -y ffmpeg libsm6 libxext6

EXPOSE 5000
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]