terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Configuration du backend S3 pour stocker le state
  backend "s3" {
    bucket  = "infrastats-g1mg06"
    key     = "g1mg06.tfstate"
    region  = "eu-west-3"
    encrypt = true
  }
}

# 1. S3 Bucket for Data and ML Models
resource "aws_s3_bucket" "data_bucket" {
  bucket = "s3-g1mg06"  
  force_destroy = true 
}

# Enable versioning for the data bucket (Best Practice)
resource "aws_s3_bucket_versioning" "data_bucket_versioning" {
  bucket = aws_s3_bucket.data_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# 2. ECR Repository for Docker Images
resource "aws_ecr_repository" "mlops_repo" {
  name                 = "ecr-g1mg06" 
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# Output the names to confirm creation
output "s3_bucket_name" {
  value = aws_s3_bucket.data_bucket.bucket
}

output "ecr_repository_url" {
  value = aws_ecr_repository.mlops_repo.repository_url
}