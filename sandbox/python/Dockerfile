# Python Sandbox Docker Image
# Minimal, secure Python environment for code execution

FROM python:3.11-alpine

# Set up non-root user for security
RUN addgroup -S sandbox && adduser -S sandbox -G sandbox

# Install only allowed packages
RUN pip install --no-cache-dir \
    numpy==1.24.3 \
    pandas==2.0.3

# Set resource limits (can be overridden)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Disable network (enforced at runtime)
# No EXPOSE or network configuration

# Set working directory
WORKDIR /sandbox

# Switch to non-root user
USER sandbox

# Default command
CMD ["python3"]
