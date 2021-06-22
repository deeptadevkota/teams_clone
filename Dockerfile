FROM python:3.6-alpine
WORKDIR /home/
RUN apk update  \
    && apk add build-base \
    && apk add --no-cache libressl-dev musl-dev libffi-dev \
    && apk add py3-pip
ADD requirements.txt /home
RUN pip install -r requirements.txt
EXPOSE 8000
CMD /bin/sh; \
    python /home/manage.py runserver 0.0.0.0:8000;
