FROM lscr.io/linuxserver/prowlarr:latest
LABEL Maintainer="bizalu"

# Prepare python environment
ENV PYTHONUNBUFFERED=1
RUN apk add --no-cache python3
RUN if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi

# Install custom init script
WORKDIR /etc/cont-init.d/
COPY scripts/ ./