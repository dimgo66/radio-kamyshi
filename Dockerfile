FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y icecast2 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd -m -g icecast icecast

# Копируем конфиги
COPY icecast.xml /etc/icecast2/icecast.xml
COPY status.html /usr/share/icecast2/web/status.html

EXPOSE 8000 8001 8443

CMD ["/bin/bash", "-c", "chown -R icecast:icecast /etc/icecast2 /usr/share/icecast2 /var/log/icecast2 || true && su icecast -c 'icecast2 -c /etc/icecast2/icecast.xml'"] 