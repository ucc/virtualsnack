# Dockerfile for virtualsnack

# Use ttyd to allow access from a web browser

# Run
#
#   docker run -p 7681:7681 -p 5150:5150 -i <images>


FROM ubuntu:18.04
LABEL maintainer "Mark Tearle - mtearle@ucc.asn.au"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      ca-certificates \
      cmake \
      curl \
      g++ \
      git \
      libjson-c3 \
      libjson-c-dev \
      libssl1.0.0 \
      libssl-dev \
      libwebsockets8 \
      libwebsockets-dev \
      pkg-config \
      vim-common \
    && git clone --depth=1 https://github.com/tsl0922/ttyd.git /tmp/ttyd \
    && cd /tmp/ttyd && mkdir build && cd build \
    && cmake -DCMAKE_BUILD_TYPE=RELEASE .. \
    && make \
    && make install \
    && apt-get remove -y --purge \
        cmake \
        g++ \
        libwebsockets-dev \
        libjson-c-dev \
        libssl-dev \
        pkg-config \
    && apt-get purge -y \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/ttyd

# Install required python packages (npyscreen, et al)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      python-setuptools \
      python-pip 

COPY requirements.txt /tmp

RUN pip install -r /tmp/requirements.txt

# Install virtual snack and run it

RUN mkdir -p /app

COPY virtualsnack.py /app

WORKDIR /app

# snack port
EXPOSE 5150
# ttyd interface
EXPOSE 7681


CMD ["ttyd", "/app/virtualsnack.py"]
