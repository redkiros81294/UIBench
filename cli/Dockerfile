FROM python:3.11-slim

# Install system dependencies for Playwright/Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install CLI package (includes its Python deps)
COPY cli/pyproject.toml cli/
COPY cli/ cli/
RUN pip install --no-cache-dir -e cli/

# Install Playwright browser
RUN playwright install chromium

# Copy core package (for RealEngine integration)
COPY core/ core/

# Set entrypoint
ENV PYTHONPATH=/app
ENTRYPOINT ["uibench"]
CMD ["--help"]
