FROM rootproject/root:6.38.00-ubuntu25.10

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

RUN apt-get update \
    && ln -sf /usr/share/zoneinfo/UTC /etc/localtime \
    && apt-get install -y --no-install-recommends \
        which \
        python3-numpy \
        python3-pip \
        imagemagick \
        ghostscript \
        python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && policy_file=/etc/ImageMagick-7/policy.xml \
    && test -f "${policy_file}" \
    && sed -i '/<\/policymap>/i\  <policy domain="coder" rights="read" pattern="PDF" />' "${policy_file}" \
    && grep -q '<policy domain="coder" rights="read" pattern="PDF" />' "${policy_file}" \
    && python3 -m venv --system-site-packages /opt/venv \
    && /opt/venv/bin/python -m pip install --no-cache-dir \
        pylint \
        ipython \
        ipykernel \
        jupyter \
        metakernel \
        zmq \
        notebook \
        hepdata_lib

ENV PATH="/opt/venv/bin:${PATH}"

ENV NB_USER=hepdata
ENV NB_UID=1000
RUN if ! getent passwd "${NB_UID}" >/dev/null; then \
        useradd --create-home --home-dir "/home/${NB_USER}" \
            --uid "${NB_UID}" "${NB_USER}"; \
    fi \
    && mkdir -p "/home/${NB_USER}" \
    && chown -R "${NB_UID}" "/home/${NB_USER}"
ENV HOME=/home/${NB_USER}
WORKDIR /home/${NB_USER}
USER ${NB_UID}

COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_UID}

# Allow incoming connections on port 8888
EXPOSE 8888

# Specify the default command to run
CMD ["jupyter", "notebook", "--ip", "0.0.0.0"]
