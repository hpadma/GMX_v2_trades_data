#!/bin/bash

prisma db push
prisma generate

python3.9 src/main.py &

python3.9 src/fastapi/app.py &

wait -n

exit $?
