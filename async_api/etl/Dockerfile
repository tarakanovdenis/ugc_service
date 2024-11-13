FROM python:3.10

WORKDIR /opt/app

COPY ./requirements.txt ./requirements.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

COPY . .
