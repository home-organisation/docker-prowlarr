FROM lscr.io/linuxserver/prowlarr:latest
LABEL Maintainer="bizalu"

# Prepare python environment
ENV PYTHONUNBUFFERED=1
RUN apk add --no-cache python3
RUN if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi

RUN python3 -m ensurepip
RUN rm -r /usr/lib/python*/ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools wheel
RUN if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install custom post files
COPY services/ /etc/s6-overlay/s6-rc.d/
RUN find /etc/s6-overlay/s6-rc.d/ -name run -exec chmod u+x {} \;

# Install custom post script
COPY custom-script/ /etc/cont-post.d/
RUN chmod u+x /etc/cont-post.d/*