FROM python:3.11-bullseye

RUN useradd song -u 1000 && mkdir /home/song && chown song:song /home/song
COPY . /home/song
WORKDIR /home/song
RUN pip install -r requirements.txt
RUN chown song:song -R . && chmod 755 /home/song/runbot.sh

USER song

ENTRYPOINT ["/home/song/runbot.sh"]