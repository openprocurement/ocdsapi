FROM python:3.6.5-alpine
RUN apk add --no-cache build-base bash readline-dev zlib-dev bzip2-dev sqlite-dev python3-dev libressl-dev
WORKDIR /api
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
RUN pip install . 
ENTRYPOINT [ "gunicorn" ]
CMD ["--help"]
