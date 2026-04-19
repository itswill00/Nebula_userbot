FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg aria2 procps curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

COPY . .

# Jalankan aria2 rpc dan bot secara bersamaan
CMD aria2c --enable-rpc --rpc-listen-all=false --rpc-listen-port=6800 --max-connection-per-server=10 --rpc-max-request-size=100M --daemon && python main.py
