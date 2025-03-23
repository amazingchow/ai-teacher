#!/bin/bash

# 启动4个worker
celery -A tasks worker --loglevel=info --concurrency=4 