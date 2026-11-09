FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Prevent Python from writing .pyc files & buffer stdout/stderr
ENV PYTHONTDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install testing utilities upfront with increased timeout and pinned versions
RUN pip install --no-cache-dir --default-timeout=100 pytest==8.3.4 pytest-json-report==1.5.0

# Create a non-root user for executing generated code safely
RUN useradd -m sandboxuser
USER sandboxuser

CMD ["pytest", "--tb=short"]