FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml README.md RESEARCH_DATA_TERMS.md PRIVACY.md ./
COPY src ./src
RUN pip install --no-cache-dir .

RUN useradd --create-home --uid 10001 caps && mkdir -p /data && chown -R caps:caps /data /app
USER caps

EXPOSE 8000
ENTRYPOINT ["caps-research-chat"]
