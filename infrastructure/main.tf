# Provider configuration
provider "aws" {
  region = var.aws_region
}

# Data source to get default VPC if vpc_id is not provided
data "aws_vpc" "selected" {
  id      = var.vpc_id != "" ? var.vpc_id : null
  default = var.vpc_id == ""
}

# Data source to get subnets in the VPC
data "aws_subnets" "available" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.selected.id]
  }
}

# ECR Repository
resource "aws_ecr_repository" "cell_segmentation" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"
}

# IAM Role for Batch Job
resource "aws_iam_role" "batch_job_role" {
  name = "cell-segmentation-batch-job-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "batch_job_role_policy" {
  role       = aws_iam_role.batch_job_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "s3_access" {
  name = "s3-access"
  role = aws_iam_role.batch_job_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.cell_segmentation.arn}",
          "${aws_s3_bucket.cell_segmentation.arn}/*"
        ]
      }
    ]
  })
}

# Batch Compute Environment
resource "aws_batch_compute_environment" "cell_segmentation" {
  compute_environment_name = var.batch_compute_environment_name

  compute_resources {
    instance_role = aws_iam_instance_profile.ecs_instance_role.arn

    instance_type = ["optimal"] # var.instance_types

    allocation_strategy = "SPOT_PRICE_CAPACITY_OPTIMIZED"

    max_vcpus = var.max_vcpus
    min_vcpus = var.min_vcpus

    type = "SPOT"

    spot_iam_fleet_role = aws_iam_role.spot_fleet_role.arn

    # Use the fetched subnets
    subnets = data.aws_subnets.available.ids

    # You may also need to add security_group_ids
    security_group_ids = [aws_security_group.batch_compute_environment.id]
  }

  service_role = aws_iam_role.batch_service_role.arn
  type         = "MANAGED"
  depends_on   = [aws_iam_role_policy_attachment.batch_service_role]

  lifecycle {
    create_before_destroy = true
  }
}

# Batch Job Queue
resource "aws_batch_job_queue" "cell_segmentation" {
  name     = var.batch_job_queue_name
  state    = "ENABLED"
  priority = 1
  compute_environment_order {
    compute_environment = aws_batch_compute_environment.cell_segmentation.arn
    order               = 1
  }
  lifecycle {
    create_before_destroy = true
  }
}

# Batch Job Definition
resource "aws_batch_job_definition" "cell_segmentation" {
  name = var.batch_job_definition_name
  type = "container"

  container_properties = jsonencode({
    image = "${aws_ecr_repository.cell_segmentation.repository_url}:latest"
    # vcpus  = 4    # Number of vCPUs the job requires
    # memory = 8192 # Memory in MiB the job requires

    jobRoleArn       = aws_iam_role.batch_job_role.arn
    executionRoleArn = aws_iam_role.batch_job_role.arn
    resourceRequirements = [
      {
        type  = "VCPU"
        value = "2" # Reduced from 4
      },
      {
        type  = "MEMORY"
        value = "4096" # Reduced from 8192
      }
    ]
    command = ["uv", "run", "src/main.py", "--input_images", "Ref::input_images", "--output_dirs", "Ref::output_dirs"]
  })

  retry_strategy {
    attempts = 1
  }
}

# IAM Role for Batch Service
resource "aws_iam_role" "batch_service_role" {
  name = "cell-segmentation-batch-service-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "batch.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "batch_service_role" {
  role       = aws_iam_role.batch_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

# IAM Role for ECS Instances
resource "aws_iam_role" "ecs_instance_role" {
  name = "cell-segmentation-ecs-instance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_instance_role" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_instance_profile" "ecs_instance_role" {
  name = "cell-segmentation-ecs-instance-profile"
  role = aws_iam_role.ecs_instance_role.name
}

# IAM Role for Spot Fleet
resource "aws_iam_role" "spot_fleet_role" {
  name = "cell-segmentation-spot-fleet-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "spotfleet.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "spot_fleet_role_policy" {
  role       = aws_iam_role.spot_fleet_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2SpotFleetTaggingRole"
}

# Security Group for Batch Compute Environment
resource "aws_security_group" "batch_compute_environment" {
  name        = "batch-compute-environment-sg"
  description = "Security group for Batch Compute Environment"
  vpc_id      = data.aws_vpc.selected.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "batch-compute-environment-sg"
  }
}

# Create S3 bucket
resource "aws_s3_bucket" "cell_segmentation" {
  bucket = "${var.s3_bucket_prefix}-${random_id.bucket_suffix.hex}"
}

resource "random_id" "bucket_suffix" {
  byte_length = 8
}

# Outputs
output "ecr_repository_url" {
  description = "ECR Repository URL"
  value       = aws_ecr_repository.cell_segmentation.repository_url
}

output "batch_job_queue_arn" {
  description = "Batch Job Queue ARN"
  value       = aws_batch_job_queue.cell_segmentation.arn
}

output "batch_job_definition_arn" {
  description = "Batch Job Definition ARN"
  value       = aws_batch_job_definition.cell_segmentation.arn
}

# Add output for S3 bucket
output "s3_bucket_name" {
  description = "Name of the created S3 bucket"
  value       = aws_s3_bucket.cell_segmentation.id
}
