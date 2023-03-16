FROM python:3.11-bullseye

RUN useradd song -u 1000 && mkdir /home/song && chown song:song /home/song
RUN apt update && apt install lsb-release -y
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt update && apt install postgresql-client-14 jq -y
COPY . /home/song
WORKDIR /home/song
RUN pip install snscrape
RUN chown song:song -R . && chmod 755 scraper.sh

USER song

ENTRYPOINT ["/home/song/scraper.sh"]