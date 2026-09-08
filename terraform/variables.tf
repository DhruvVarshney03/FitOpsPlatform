variable "aws_region" {
  description = "LocalStack AWS region."
  type        = string
  default     = "us-east-1"
}

variable "aws_access_key" {
  description = "LocalStack access key."
  type        = string
  default     = "test"
  sensitive   = true
}

variable "aws_secret_key" {
  description = "LocalStack secret key."
  type        = string
  default     = "test"
  sensitive   = true
}

variable "localstack_endpoint" {
  description = "LocalStack S3 endpoint from the host running Terraform."
  type        = string
  default     = "http://localhost:4566"
}

variable "raw_bucket_name" {
  description = "Bucket for raw workbook and normalized artifacts."
  type        = string
  default     = "fitops-raw"
}

variable "kubeconfig_path" {
  description = "Kubeconfig used by the Kubernetes provider."
  type        = string
  default     = "~/.kube/config"
}

variable "kube_context" {
  description = "Kind or Kubernetes context for the FitOps namespace."
  type        = string
  default     = "kind-fitops"
}

variable "kubernetes_namespace" {
  description = "Namespace for FitOps workloads."
  type        = string
  default     = "fitops"
}

variable "enable_kubernetes" {
  description = "Create the FitOps namespace when a Kind cluster is available."
  type        = bool
  default     = false
}
