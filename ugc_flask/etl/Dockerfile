FROM python:3.10

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /opt/app

COPY ./requirements.txt ./requirements.txt

RUN pip install --upgrade pip \
    && pip install --no-cache -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]