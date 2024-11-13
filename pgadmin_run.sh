#!/bin/bash

docker run --rm --name pgadmin \
    --network appnet \
    -p 82:80 \
    -e 'PGADMIN_DEFAULT_EMAIL=root@mail.com' \
    -e 'PGADMIN_DEFAULT_PASSWORD=root' \
    dpage/pgadmin4
