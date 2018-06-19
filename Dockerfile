FROM python:3.6.5-alpine
RUN pip install virtualenv
RUN apk add --no-cache build-base bash readline-dev zlib-dev bzip2-dev sqlite-dev python3-dev libressl-dev
WORKDIR /api
ADD . .

RUN pip install . 
ENTRYPOINT [ "gunicorn" ]
CMD ["--help"]
