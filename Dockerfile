FROM mtgupf/essentia:ubuntu20.04-v2.1_beta5
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8

RUN apt-get update && apt-get install -y wget ca-certificates && rm -rf /var/lib/apt/lists/*

RUN wget -q -O - https://deb.nodesource.com/setup_18.x | bash - \
      && apt-get install -y --no-install-recommends \
         cmake \
         libmad0-dev \
         libsndfile1-dev \
         libgd-dev \
         libboost-filesystem-dev \
         libboost-program-options-dev \
         libboost-regex-dev \
         nodejs \
         libsndfile1-dev \
         build-essential \
         libpython3.8-dev \
         lame \
         libffi-dev \
      && apt-get remove -y python3-yaml python3-six python3-numpy \
      && rm -rf /var/lib/apt/lists/*

RUN wget -O get-pip.py 'https://bootstrap.pypa.io/get-pip.py' \
    && python3 get-pip.py --disable-pip-version-check --no-cache-dir \
    && rm -r get-pip.py


RUN mkdir /code
WORKDIR /code

ADD requirements.txt /code/
RUN pip3 install --no-cache-dir numpy==1.19.5 six
RUN pip3 install --no-cache-dir -r requirements.txt

ADD requirements_dev.txt /code/
RUN pip3 install --no-cache-dir -r requirements_dev.txt

RUN mkdir /sources
WORKDIR /sources
RUN git clone https://github.com/MTG/pycompmusic.git
WORKDIR /sources/pycompmusic
RUN pip3 install -e . -t /usr/local/lib/python3.8/dist-packages/


ADD package.json /code/
WORKDIR /code
RUN npm install && rm -r ~/.npm

ADD . /code/

RUN npm run build
WORKDIR /code
# TODO: Could be made part of the frontend build script
RUN bash build-less.sh

RUN python3 manage.py collectstatic --settings dunya.build_settings
