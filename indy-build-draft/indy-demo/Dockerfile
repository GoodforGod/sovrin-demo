FROM ubuntu:xenial

ARG uid=1000
ARG indy_stream=stable

ENV LC_ALL="C.UTF-8"
ENV LANG="C.UTF-8"
ENV SHELL="/bin/bash"

# Python 3.6
RUN apt-get update
RUN apt-get install -y software-properties-common vim
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update

RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-venv

# update pip
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel

# Install environment
RUN apt-get update -y && apt-get install -y \
		petname \
		pwgen \
		wget \
		python-setuptools \
		python3-nacl \
		apt-transport-https \
		ca-certificates \
		build-essential \
		pkg-config \
		libssl-dev \
		libsqlite3-dev \
		libsodium-dev \
		curl \
		vim

# Add indy user
RUN useradd -ms /bin/bash -u $uid indy

RUN curl "http://keyserver.ubuntu.com/pks/lookup?search=0x68DB5E88&op=get" | awk '/^-----BEGIN/ { output = 1 }; output; /^-----END/ { output = 0 }' | apt-key add -
RUN echo "deb https://repo.sovrin.org/deb xenial stable" >> /etc/apt/sources.list
RUN echo "deb https://repo.sovrin.org/sdk/deb xenial stable" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y libindy indy-cli indy-node

RUN pip3 install setuptools
RUN pip3 install python3-indy

WORKDIR /indy-demo

CMD [ "/bin/bash", "-c", "while true; do sleep 200; done;" ]
