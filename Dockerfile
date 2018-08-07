FROM rootproject/root-ubuntu16:6.12

ENV MAGICK_HOME=/usr
ENV ROOT_VERSION=6.12/07

LABEL maintainer="Clemens Lange clemens.lange@cern.ch"

# Build-time metadata as defined at http://label-schema.org
ARG BUILD_DATE
ARG VCS_REF
ARG VCS_URL
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="hepdata_lib Docker image" \
      org.label-schema.description="Provide environment in which to run hepdata_lib" \
      org.label-schema.url="https://github.com/clelange/hepdata_lib" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url=$VCS_URL \
      org.label-schema.vendor="CERN" \
      org.label-schema.version=$ROOT_VERSION \
      org.label-schema.schema-version="1.0"

USER root

RUN apt-get update -qq \
    && ln -sf /usr/share/zoneinfo/UTC /etc/localtime \
    && apt-get -y install \
        python-dev \
        python-numpy \
        python-pip \
        imagemagick \
    && localedef -i en_US -f UTF-8 en_US.UTF-8 \
    && rm -rf /packages /var/lib/apt/lists/* \
    && pip install --no-cache-dir \
        pylint==1.9.* \
        jupyter \
        metakernel \
        zmq \
        notebook==5.* \
        hepdata_lib

ENV PYTHONPATH /usr/local/lib/:/usr/local/lib/root/

ENV NB_USER hepdata
ENV NB_UID 1000
RUN useradd --create-home --home-dir /home/${NB_USER} \
    --uid ${NB_UID} ${NB_USER}
ENV HOME /home/${NB_USER}
WORKDIR /home/${NB_USER}
USER ${NB_USER}

COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

# Allow incoming connections on port 8888
EXPOSE 8888

# Specify the default command to run
CMD ["jupyter", "notebook", "--ip", "0.0.0.0"]
