FROM python:2.7.11

RUN pip install flask_pymongo flask

COPY web_server/ web_server/
COPY utils/ utils/
COPY input/ input/

CMD python -m web_server.web_server
