FROM python:3.6.5-alpine

RUN apk --no-cache update && apk --no-cache add bash && \
    addgroup ocds && adduser -D -s /bin/bash -h /home/ocds -G ocds ocds
RUN apk add --no-cache build-base readline-dev zlib-dev bzip2-dev sqlite-dev python3-dev libressl-dev git libffi-dev postgresql-dev

WORKDIR /home/ocds
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt
COPY . .
RUN pip install -e .

USER ocds
CMD [ "/bin/sh" ]

