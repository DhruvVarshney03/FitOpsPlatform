provider "aws" {
  region                      = var.aws_region
  access_key                  = var.aws_access_key
  secret_key                  = var.aws_secret_key
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_use_path_style           = true

  endpoints {
    s3 = var.localstack_endpoint
  }
}

provider "kubernetes" {
  config_path    = var.enable_kubernetes ? var.kubeconfig_path : null
  config_context = var.enable_kubernetes ? var.kube_context : null
}

resource "aws_s3_bucket" "raw" {
  bucket        = var.raw_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "raw" {
  bucket = aws_s3_bucket.raw.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "raw" {
  bucket = aws_s3_bucket.raw.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "kubernetes_namespace" "fitops" {
  count = var.enable_kubernetes ? 1 : 0

  metadata {
    name = var.kubernetes_namespace
    labels = {
      "app.kubernetes.io/part-of"    = "fitops-platform"
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }
}
