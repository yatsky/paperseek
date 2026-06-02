# syntax=docker/dockerfile:1

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN useradd --create-home --shell /usr/sbin/nologin paperseek

COPY pyproject.toml README.md LICENSE ./
COPY paperseek ./paperseek

RUN python -m pip install --upgrade pip \
    && python -m pip install .

USER paperseek

EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/api/sources', timeout=3).read()" || exit 1

CMD ["uvicorn", "paperseek.web_app:app", "--host", "0.0.0.0", "--port", "8765"]
