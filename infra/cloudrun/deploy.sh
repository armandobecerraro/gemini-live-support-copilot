#!/bin/bash
# Deploy all services to Google Cloud Run
# Usage: ./infra/cloudrun/deploy.sh
set -e

PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID}"
REGION="${GCP_REGION:-us-central1}"
IMAGE_PREFIX="${REGION}-docker.pkg.dev/${PROJECT_ID}/supportsight"

# Authenticate Docker to Artifact Registry
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

echo "🚀 Deploying SupportSight Live to Cloud Run — project: ${PROJECT_ID}"

# ── logs-service ──
echo "Building logs-service..."
docker build -t "${IMAGE_PREFIX}/logs-service:latest" ./logs-service
docker push "${IMAGE_PREFIX}/logs-service:latest"
gcloud run deploy supportsight-logs-service \
  --image "${IMAGE_PREFIX}/logs-service:latest" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --port 8090 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5

LOGS_URL=$(gcloud run services describe supportsight-logs-service --region "${REGION}" --format 'value(status.url)')
echo "logs-service deployed: ${LOGS_URL}"

# ── actions-service ──
echo "Building actions-service..."
docker build -t "${IMAGE_PREFIX}/actions-service:latest" ./actions-service
docker push "${IMAGE_PREFIX}/actions-service:latest"
gcloud run deploy supportsight-actions-service \
  --image "${IMAGE_PREFIX}/actions-service:latest" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --port 8091 \
  --memory 1Gi \
  --cpu 2 \
  --set-env-vars "ACTIONS_SERVICE_API_KEY=${ACTIONS_SERVICE_API_KEY}"

ACTIONS_URL=$(gcloud run services describe supportsight-actions-service --region "${REGION}" --format 'value(status.url)')

# ── backend-orchestrator ──
echo "Building backend-orchestrator..."
docker build -t "${IMAGE_PREFIX}/backend:latest" ./backend-orchestrator
docker push "${IMAGE_PREFIX}/backend:latest"
gcloud run deploy supportsight-backend \
  --image "${IMAGE_PREFIX}/backend:latest" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 2 \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest" \
  --set-env-vars "LOGS_SERVICE_URL=${LOGS_URL},ACTIONS_SERVICE_URL=${ACTIONS_URL},ENVIRONMENT=production"

BACKEND_URL=$(gcloud run services describe supportsight-backend --region "${REGION}" --format 'value(status.url)')

# ── frontend ──
echo "Building frontend..."
docker build -t "${IMAGE_PREFIX}/frontend:latest" ./frontend \
  --build-arg NEXT_PUBLIC_API_URL="${BACKEND_URL}"
docker push "${IMAGE_PREFIX}/frontend:latest"
gcloud run deploy supportsight-frontend \
  --image "${IMAGE_PREFIX}/frontend:latest" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --port 3000 \
  --memory 512Mi \
  --set-env-vars "NEXT_PUBLIC_API_URL=${BACKEND_URL}"

FRONTEND_URL=$(gcloud run services describe supportsight-frontend --region "${REGION}" --format 'value(status.url)')

echo ""
echo "✅ All services deployed!"
echo "Frontend:  ${FRONTEND_URL}"
echo "Backend:   ${BACKEND_URL}"
echo "Logs:      ${LOGS_URL}"
echo "Actions:   ${ACTIONS_URL}"
