# base image
FROM python:3.10-slim-bookworm as base
WORKDIR /app/api
# Install Poetry
ENV POETRY_VERSION=1.8.3
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade poetry==${POETRY_VERSION}
# Configure Poetry
ENV POETRY_CACHE_DIR=/tmp/poetry_cache
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_VIRTUALENVS_CREATE=true

FROM base as packages
# Install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry source add --priority=primary mirrors https://pypi.tuna.tsinghua.edu.cn/simple/
RUN poetry install --sync --no-cache --no-root

# production stage
FROM base AS production
WORKDIR /app/api
ENV DEPLOY_ENV PRODUCTION
ENV TZ UTC
# Copy Python environment and packages
ENV VIRTUAL_ENV=/app/api/.venv
COPY --from=packages ${VIRTUAL_ENV} ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
# Copy source code
COPY . /app/api/
RUN mkdir -p /app/api/logs /app/api/storage /app/api/storage/results
EXPOSE 18888
# Copy entrypoint
COPY ./entrypoint.sh /app/api/
RUN chmod +x /app/api/entrypoint.sh
ENTRYPOINT ["/bin/bash", "/app/api/entrypoint.sh"]