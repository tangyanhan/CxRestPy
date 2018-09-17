FROM python:3.6

COPY . /cx
RUN pip install -r /cx/requirements.txt

ENV CX_CONFIG_DIR=/cx/etc/