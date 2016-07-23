FROM python:2.7.11

RUN pip install flask_pymongo flask

COPY web_server.py /web_server/
COPY __init__.py /web_server/
COPY utils/ /utils/

ENV PYTHONPATH /:$PYTHONPATH
CMD python -m web_server.web_server
