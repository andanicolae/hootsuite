FROM python:2.7.11

RUN pip install pymongo praw

COPY reddit_daemon/ reddit_daemon/
COPY utils/ utils/
COPY input/ input/

CMD python -m reddit_daemon.daemon
