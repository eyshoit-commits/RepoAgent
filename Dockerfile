FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml /app/
COPY README.md /app/README.md
COPY docs /app/docs
COPY config /app/config
COPY src /app/src

RUN pip install --no-cache-dir .

COPY scripts /app/scripts

ENTRYPOINT ["spooky-cli"]
CMD ["--help"]
