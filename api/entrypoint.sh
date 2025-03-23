#!/bin/bash

# 遇到执行出错，直接终止脚本的执行
set -o errexit

if [[ "${MODE}" == "worker" ]]; then
    celery --app=celery_worker.celery_inst worker --pool=${CELERY_WORKER_CLASS:-prefork} --concurrency=${CELERY_WORKER_AMOUNT:-1} --loglevel=${CELERY_WORKER_LOG_LEVEL:-INFO} \
        --queues=${CELERY_QUEUES:-celery,default}
elif [[ "${MODE}" == "beat" ]]; then
    celery --app=celery_instance.celery_inst beat --loglevel=INFO
elif [[ "${MODE}" == "api" ]]; then
    uvicorn \
        --host="${SERVER_WORKER_BIND_ADDRESS:-0.0.0.0}" \
        --port="${SERVER_WORKER_PORT:-18888}" \
        --workers=${SERVER_WORKER_AMOUNT:-1} \
        app:app
fi