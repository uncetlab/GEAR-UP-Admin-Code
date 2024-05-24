FROM ubuntu:20.04
# Uses Python 3.8

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
RUN apt update -y\
    && apt install software-properties-common -y\
    && add-apt-repository -y ppa:ubuntugis/ppa

RUN apt update \
    && apt install gdal-bin python3-gdal libgdal-dev python3-dev -y


RUN apt update -y\
    && apt install python3-pip -y

RUN apt install ffmpeg libsm6 libxext6  -y\
    && dpkg --configure -a
RUN apt upgrade

RUN apt update -y\
    && apt install libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev \
    libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
    libharfbuzz-dev libfribidi-dev libxcb1-dev libyaml-dev -y

ADD . /home/App
WORKDIR /home/App

COPY requirements.txt /home/App/requirements.txt

RUN python3 -m pip install psycopg2-binary
# RUN python3 -m pip install Pillow
# RUN python3 -m pip install wheel
RUN python3 -m pip install setuptools
RUN apt update -y\
    && apt install libpq-dev -y
RUN pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

COPY . /home/App
EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000", "--verbosity", "2"]
# RUN python3 manage.py collectstatic --noinput