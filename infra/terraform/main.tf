# SupportSight Live — Infrastructure as Code
# Category: UI Navigator / Live Agents
# Hackathon: Gemini Live Agent Challenge

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ── Cloud Run Services ──

# Backend Orchestrator
resource "google_cloud_run_v2_service" "backend" {
  name     = "supportsight-backend"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "us-central1-docker.pkg.dev/${var.project_id}/supportsight/backend:latest"
      env {
        name  = "ENVIRONMENT"
        value = "production"
      }
      env {
        name  = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = "gemini-api-key"
            version = "latest"
          }
        }
      }
    }
    scaling {
      max_instance_count = 10
    }
  }
}

# Frontend
resource "google_cloud_run_v2_service" "frontend" {
  name     = "supportsight-frontend"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "us-central1-docker.pkg.dev/${var.project_id}/supportsight/frontend:latest"
      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = google_cloud_run_v2_service.backend.uri
      }
    }
  }
}

# ── IAM ──

resource "google_cloud_run_v2_service_iam_member" "public_backend" {
  location = var.region
  name     = google_cloud_run_v2_service.backend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service_iam_member" "public_frontend" {
  location = var.region
  name     = google_cloud_run_v2_service.frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
