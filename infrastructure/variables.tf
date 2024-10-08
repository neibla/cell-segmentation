variable "aws_region" {
  description = "AWS region to deploy resources"
  default     = "us-west-2"
}

variable "vpc_id" {
  description = "ID of the VPC to use"
  type        = string
  default     = "" # Leave empty to use the default VPC
}

variable "project_name" {
  description = "Name of the project, used in resource naming"
  default     = "cell-segmentation"
}

variable "ecr_repository_name" {
  description = "Name of the ECR repository"
  default     = "cell-segmentation-job"
}

variable "batch_compute_environment_name" {
  description = "Name of the Batch compute environment"
  default     = "cell-segmentation-compute-env"
}

variable "batch_job_queue_name" {
  description = "Name of the Batch job queue"
  default     = "cell-segmentation-job-queue"
}

variable "batch_job_definition_name" {
  description = "Name of the Batch job definition"
  default     = "cell-segmentation-job-def"
}

variable "s3_bucket_prefix" {
  description = "Prefix for the S3 bucket name"
  default     = "cell-segmentation-data"
}

variable "instance_types" {
  description = "List of instance types to use for the Batch compute environment"
  type        = list(string)
  default     = ["optimal"] #"inf1.xlarge"] # "g4dn.xlarge"]
}


variable "max_vcpus" {
  description = "Maximum number of vCPUs for the Batch compute environment"
  type        = number
  default     = 16
}

variable "min_vcpus" {
  description = "Minimum number of vCPUs for the Batch compute environment"
  type        = number
  default     = 0
}
