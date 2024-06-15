#Last package update 15 June 2024
FROM lscr.io/linuxserver/prowlarr:latest
LABEL Maintainer="bizalu"

# Prepare python environment
ENV PYTHONUNBUFFERED=1
RUN apk -U upgrade --no-cache
RUN apk add --no-cache python3 py3-defusedxml
RUN if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi


# Install custom post files
COPY services/ /etc/s6-overlay/s6-rc.d/
RUN find /etc/s6-overlay/s6-rc.d/ -name run -exec chmod u+x {} \;

# Install custom post script
COPY custom-script/ /etc/cont-post.d/
RUN chmod u+x /etc/cont-post.d/*