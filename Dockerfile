# Version 0.0.1
FROM ubuntu:cosmic

MAINTAINER Standa Kurik "standa.kurik@gmail.com"

# base tools
RUN apt-get update
RUN apt-get install -y \
   unzip \
   build-essential \
   wget \
   g++ \
   git \
   subversion \
   automake \
   libtool \
   zlib1g-dev \
   libboost-all-dev \
   libbz2-dev \
   liblzma-dev \
   python-dev \
   libsoap-lite-perl \
   libxmlrpc-core-c3-dev libxmlrpc-c++8-dev \
   google-perftools

RUN mkdir -p /home/moses
RUN locale-gen en_GB.UTF-8
ENV LANG='en_GB.UTF-8' LANGUAGE='en_GB:en' LC_ALL='en_GB.UTF-8'
ENV PYTHONIOENCODING=utf-8

WORKDIR /home/moses

# Build boost
#
RUN wget http://downloads.sourceforge.net/project/boost/boost/1.55.0/boost_1_55_0.tar.gz
RUN tar zxvf boost_1_55_0.tar.gz
WORKDIR /home/moses/boost_1_55_0
RUN ./bootstrap.sh
RUN ./b2 -j8 --prefix=$PWD --libdir=$PWD/lib64 --layout=system link=static install || echo FAILURE

# Build cmph
#
WORKDIR /home/moses
RUN wget http://downloads.sourceforge.net/project/cmph/cmph/cmph-2.0.tar.gz
RUN tar zxvf cmph-2.0.tar.gz
WORKDIR /home/moses/cmph-2.0
RUN ./configure --prefix=/usr/local && make && make install prefix=/usr/local/cmph

# Build Moses with xmlrpc-c option (for server)
#
WORKDIR /home/moses
RUN git clone https://github.com/moses-smt/mosesdecoder.git
WORKDIR /home/moses/mosesdecoder
RUN ./bjam --with-boost=/home/moses/boost_1_55_0 --with-cmph=/usr/local/cmph -j8  --with-xmlrpc-c=/usr
# The config adds "bin/xmlrpc-c-config" to that path

WORKDIR /home/moses
RUN wget http://www.statmt.org/moses/download/sample-models.tgz
RUN tar xzf sample-models.tgz

# Build giza; based on instructions from <http://www.statmt.org/moses/?n=Moses.Baseline>
#
WORKDIR /home/moses
RUN git clone https://github.com/moses-smt/giza-pp.git
WORKDIR /home/moses/giza-pp
RUN make
WORKDIR /home/moses/mosesdecoder
RUN mkdir tools
WORKDIR /home/moses/giza-pp
RUN cp GIZA++-v2/GIZA++ GIZA++-v2/snt2cooc.out mkcls-v2/mkcls /home/moses/mosesdecoder/tools

WORKDIR /home/moses
COPY train.py .
