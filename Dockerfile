FROM python:3.6.5-alpine

RUN apk --no-cache update && apk --no-cache add bash && \
    addgroup ocds && adduser -D -s /bin/bash -h /home/ocds -G ocds ocds
RUN apk --no-cache add git build-base python3-dev libxslt-dev

WORKDIR /home/ocds
RUN pip install git+https://github.com/openprocurement/ocdsapi.git
ADD requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt
ADD . .
RUN pip install .

USER ocds
ENTRYPOINT ["ocds-server"]
CMD ["--config", "server.yml"]
