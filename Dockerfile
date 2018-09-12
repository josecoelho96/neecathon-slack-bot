FROM python:3.6-alpine
ENV PYTHONBUFFERED 1
ENV C_FORCE_ROOT true
RUN mkdir /src
WORKDIR /src
ADD ./src /src
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev
RUN pip install -r requirements.pip
CMD python server.py