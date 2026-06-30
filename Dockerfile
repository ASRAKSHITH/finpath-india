FROM node:20 AS frontend-builder
WORKDIR /app/finpath-ui
# Copy everything first
COPY finpath-ui/ ./
# Forcefully remove any Windows node_modules that might have been uploaded
RUN rm -rf node_modules
# Install fresh Linux binaries and build
RUN npm install
RUN npm run build

FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Copy built react UI into python environment
COPY --from=frontend-builder /app/finpath-ui/dist ./finpath-ui/dist

# Expose port for Hugging Face Spaces (defaults to 7860)
EXPOSE 7860

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
