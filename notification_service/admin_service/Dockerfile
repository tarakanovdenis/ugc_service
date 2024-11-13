FROM python:3.11

# Папка, в которой будут размещаться файлы проекта внутри контейнера
WORKDIR /opt/app

# Копирование в контейнер файлов, которые редко меняются
COPY ./requirements.txt ./requirements.txt

# Установка зависимостей
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Копирование остального (для ускорения сборки образа эту команду стоит размещать ближе к концу файла)
COPY . .

EXPOSE 8000

ENTRYPOINT [ "python", "-m", "main" ]