FROM python:3.11

WORKDIR /opt/app

COPY ./requirements.txt ./requirements.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

RUN ["chmod", "+x", "./run_auth_service.sh"]

ENTRYPOINT ["bash", "./run_auth_service.sh"]
