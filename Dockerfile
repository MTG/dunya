FROM python:3.11
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8

RUN mkdir -p /etc/apt/keyrings/
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" > /etc/apt/sources.list.d/nodesource.list

RUN apt-get update && apt-get install -y --no-install-recommends \
         cmake \
         libmad0-dev \
         libsndfile1-dev \
         libgd-dev \
         libboost-filesystem-dev \
         libboost-program-options-dev \
         libboost-regex-dev \
         nodejs \
         libsndfile1-dev \
         lame \
         libffi-dev \
      && rm -rf /var/lib/apt/lists/*

RUN mkdir /code
WORKDIR /code

ADD requirements.txt /code/
RUN --mount=type=cache,target=/root/.cache/pip pip3 install -r requirements.txt

ADD requirements_dev.txt /code/
RUN --mount=type=cache,target=/root/.cache/pip pip3 install -r requirements_dev.txt

RUN mkdir /sources
WORKDIR /sources
RUN git clone https://github.com/MTG/pycompmusic.git
WORKDIR /sources/pycompmusic
RUN pip3 install -e . -t /usr/local/lib/python3.8/dist-packages/


ADD package.json package-lock.json /code/
WORKDIR /code
RUN npm install && rm -r ~/.npm

ADD . /code/

RUN npm run build

# TODO: Could be made part of the frontend build script
RUN bash build-less.sh

RUN python manage.py collectstatic --settings dunya.build_settings
