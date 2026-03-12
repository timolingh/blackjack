FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps for building any wheels (e.g., numpy)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app

# Install deps and project
RUN pip install --no-cache-dir -r requirements-dev.txt \
    && pip install --no-cache-dir -e .

# Default command: run the bankroll simulator
CMD ["python", "bankroll_simulator.py"]
