output "raw_bucket_name" {
  description = "LocalStack bucket containing raw and normalized import artifacts."
  value       = aws_s3_bucket.raw.bucket
}

output "kubernetes_namespace" {
  description = "Namespace reserved for FitOps Kubernetes workloads."
  value       = var.enable_kubernetes ? kubernetes_namespace.fitops[0].metadata[0].name : null
}
