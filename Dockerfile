FROM rootproject/root:6.22.06-fedora33

ENV MAGICK_HOME=/usr

LABEL maintainer="Clemens Lange clemens.lange@cern.ch"

# Build-time metadata as defined at http://label-schema.org
ARG BUILD_DATE
ARG VCS_REF
ARG VCS_URL
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="hepdata_lib Docker image" \
      org.label-schema.description="Provide environment in which to run hepdata_lib" \
      org.label-schema.url="https://github.com/HEPData/hepdata_lib" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url=$VCS_URL \
      org.label-schema.vendor="CERN" \
      org.label-schema.schema-version="1.0"

USER root

RUN dnf check-update -q || true \
    && ln -sf /usr/share/zoneinfo/UTC /etc/localtime \
    && dnf -y install \
        which \
        python3-numpy \
        python3-pip \
        ImageMagick \
    && dnf clean all \
    && sed -i '/MVG/d' /etc/ImageMagick-6/policy.xml \
    && sed -i '/PDF/{s/none/read|write/g}' /etc/ImageMagick-6/policy.xml \
    && sed -i '/PDF/ a <policy domain="coder" rights="read|write" pattern="LABEL" />' /etc/ImageMagick-6/policy.xml \
    && cat /etc/ImageMagick-6/policy.xml \
    && python -m pip install --no-cache-dir \
        pylint \
        ipython \
        ipykernel \
        jupyter \
        metakernel \
        zmq \
        notebook \
        hepdata_lib

ENV PYTHONPATH /usr/local/lib/:/usr/local/lib/root/

ENV NB_USER hepdata
ENV NB_UID 1000
RUN useradd --create-home --home-dir /home/${NB_USER} \
    --uid ${NB_UID} ${NB_USER} \
     && sudo usermod -aG wheel ${NB_USER}
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
