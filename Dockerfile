# Build stage - Build React frontend
FROM node:18-alpine as builder

WORKDIR /app

# Copy frontend files
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Production stage - Python backend with FFmpeg
FROM python:3.11-slim

WORKDIR /app

# Install FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Copy frontend build from builder stage
COPY --from=builder /app/dist ../frontend/dist

# Create downloads directory
RUN mkdir -p downloads

# Environment
ENV PORT=5000
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')"

# Start command
CMD ["python", "app.py"]