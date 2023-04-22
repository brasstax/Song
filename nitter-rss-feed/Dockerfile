FROM python:3.11-bullseye
ENV ZED_VERSION=v1.7.0

RUN useradd song -u 1000 && mkdir /home/song && chown song:song /home/song
RUN apt update && apt install lsb-release -y
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt update && apt install postgresql-client-14 -y
RUN wget https://github.com/brimdata/zed/releases/download/${ZED_VERSION}/zed-${ZED_VERSION}.linux-amd64.tar.gz && tar -zxvf zed-${ZED_VERSION}.linux-amd64.tar.gz -C /usr/local/bin
COPY . /home/song
WORKDIR /home/song
RUN pip install feedparser psycopg[pool]
RUN chown song:song -R . && chmod 755 scraper.sh

USER song

ENTRYPOINT ["/home/song/scraper.sh"]