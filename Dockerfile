FROM lscr.io/linuxserver/prowlarr:latest
LABEL Maintainer="bizalu"

# Prepare python environment
ENV PYTHONUNBUFFERED=1
RUN apk add --no-cache python3
RUN if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi

# Install custom post files
WORKDIR /etc/s6-overlay/s6-rc.d/
COPY services/ ./

# Install custom post script
WORKDIR /etc/cont-post.d/
COPY custom-script/ ./