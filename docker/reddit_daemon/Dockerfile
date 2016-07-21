FROM python:2.7.11

RUN pip install pymongo praw

COPY daemon.py reddit_daemon/
COPY __init__.py reddit_daemon/
COPY utils/ utils/
COPY input/ input/

CMD python -m reddit_daemon.daemon
