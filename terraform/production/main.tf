# ============================================================================
# TERRAFORM CONFIGURATION - TECNOCURSOS AI PRODUCTION
# ============================================================================
# 
# Infraestrutura como código para deployment em produção
# Seguindo as melhores práticas de:
# - AWS Well-Architected Framework
# - Terraform best practices
# - FastAPI deployment patterns
# - Security hardening
# - High availability
# - Cost optimization
#
# Autor: TecnoCursos AI System
# Data: 17/01/2025
# ============================================================================

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.10"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
  
  backend "s3" {
    bucket         = "tecnocursos-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "tecnocursos-terraform-locks"
  }
}

# ============================================================================
# PROVIDERS CONFIGURATION
# ============================================================================

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "TecnoCursos AI"
      Environment = "production"
      ManagedBy   = "Terraform"
      Owner       = "DevOps Team"
      CostCenter  = "Engineering"
    }
  }
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
    }
  }
}

# ============================================================================
# DATA SOURCES
# ============================================================================

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

# ============================================================================
# LOCALS
# ============================================================================

locals {
  name            = "tecnocursos-${var.environment}"
  cluster_version = "1.28"
  
  vpc_cidr = "10.0.0.0/16"
  azs      = slice(data.aws_availability_zones.available.names, 0, 3)
  
  tags = {
    Project     = "TecnoCursos AI"
    Environment = var.environment
    GithubRepo  = "tecnocursos/tecnocursos-ai"
  }
}

# ============================================================================
# VPC AND NETWORKING
# ============================================================================

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "${local.name}-vpc"
  cidr = local.vpc_cidr
  
  azs             = local.azs
  private_subnets = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 4, k)]
  public_subnets  = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k + 48)]
  intra_subnets   = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k + 52)]
  
  enable_nat_gateway = true
  single_nat_gateway = false  # Multi-AZ NAT for HA
  enable_vpn_gateway = false
  
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  # VPC Flow Logs
  enable_flow_log                      = true
  create_flow_log_cloudwatch_iam_role  = true
  create_flow_log_cloudwatch_log_group = true
  
  public_subnet_tags = {
    "kubernetes.io/cluster/${local.name}" = "shared"
    "kubernetes.io/role/elb"               = 1
  }
  
  private_subnet_tags = {
    "kubernetes.io/cluster/${local.name}" = "shared"
    "kubernetes.io/role/internal-elb"     = 1
  }
  
  tags = local.tags
}

# ============================================================================
# SECURITY GROUPS
# ============================================================================

resource "aws_security_group" "additional" {
  name_prefix = "${local.name}-additional"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    cidr_blocks = [
      "10.0.0.0/8",
      "172.16.0.0/12",
      "192.168.0.0/16",
    ]
  }
  
  tags = local.tags
}

# ============================================================================
# EKS CLUSTER
# ============================================================================

module "eks" {
  source = "terraform-aws-modules/eks/aws"
  
  cluster_name    = local.name
  cluster_version = local.cluster_version
  
  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true
  
  # OIDC Identity provider
  cluster_identity_providers = {
    sts = {
      client_id = "sts.amazonaws.com"
    }
  }
  
  # Encryption key
  create_kms_key = true
  cluster_encryption_config = {
    resources        = ["secrets"]
    provider_key_arn = module.eks.kms_key_arn
  }
  
  kms_key_deletion_window_in_days = 7
  enable_kms_key_rotation         = true
  
  # Cluster access entry
  enable_cluster_creator_admin_permissions = true
  
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }
  
  eks_managed_node_groups = {
    # General purpose nodes
    general = {
      name           = "general"
      use_name_prefix = true
      
      subnet_ids = module.vpc.private_subnets
      
      min_size     = 2
      max_size     = 10
      desired_size = 3
      
      ami_type       = "AL2_x86_64"
      instance_types = ["t3.large"]
      
      capacity_type        = "ON_DEMAND"
      force_update_version = true
      
      ebs_optimized           = true
      disable_api_termination = false
      enable_monitoring       = true
      
      block_device_mappings = {
        xvda = {
          device_name = "/dev/xvda"
          ebs = {
            volume_size           = 100
            volume_type           = "gp3"
            iops                  = 3000
            throughput            = 150
            encrypted             = true
            delete_on_termination = true
          }
        }
      }
      
      metadata_options = {
        http_endpoint               = "enabled"
        http_tokens                 = "required"
        http_put_response_hop_limit = 2
        instance_metadata_tags      = "disabled"
      }
      
      create_iam_role          = true
      iam_role_name            = "EKSNodeGroupRole-${local.name}"
      iam_role_use_name_prefix = false
      iam_role_description     = "EKS managed node group IAM role"
      iam_role_tags = {
        Purpose = "Protector of the kubelet"
      }
      iam_role_additional_policies = {
        AmazonSSMManagedInstanceCore = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
      }
      
      schedules = {
        scale-down = {
          min_size     = 0
          max_size     = 0
          desired_size = 0
          start_time   = "2024-01-01T22:00:00Z"
          end_time     = "2024-01-02T06:00:00Z"
          timezone     = "America/Sao_Paulo"
          recurrence   = "0 22 * * MON-FRI"
        }
      }
      
      tags = {
        ExtraTag = "EKS managed node group"
      }
    }
    
    # High memory nodes for video processing
    video_processing = {
      name           = "video-processing"
      use_name_prefix = true
      
      subnet_ids = module.vpc.private_subnets
      
      min_size     = 1
      max_size     = 5
      desired_size = 1
      
      ami_type       = "AL2_x86_64"
      instance_types = ["c5.2xlarge"]
      
      capacity_type = "SPOT"
      
      taints = {
        dedicated = {
          key    = "video-processing"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      }
      
      labels = {
        workload = "video-processing"
      }
      
      tags = {
        ExtraTag = "Video processing node group"
      }
    }
  }
  
  # Cluster security group additional rules
  cluster_security_group_additional_rules = {
    ingress_nodes_ephemeral_ports_tcp = {
      description                = "Nodes on ephemeral ports"
      protocol                   = "tcp"
      from_port                  = 1025
      to_port                    = 65535
      type                       = "ingress"
      source_node_security_group = true
    }
  }
  
  # Node security group additional rules
  node_security_group_additional_rules = {
    ingress_self_all = {
      description = "Node to node all ports/protocols"
      protocol    = "-1"
      from_port   = 0
      to_port     = 0
      type        = "ingress"
      self        = true
    }
    
    ingress_cluster_to_node_all_traffic = {
      description                   = "Cluster API to Nodegroup all traffic"
      protocol                      = "-1"
      from_port                     = 0
      to_port                       = 0
      type                          = "ingress"
      source_cluster_security_group = true
    }
    
    egress_all = {
      description      = "Node all egress"
      protocol         = "-1"
      from_port        = 0
      to_port          = 0
      type             = "egress"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    }
  }
  
  tags = local.tags
}

# ============================================================================
# RDS DATABASE
# ============================================================================

module "rds" {
  source = "terraform-aws-modules/rds/aws"
  
  identifier = "${local.name}-mysql"
  
  engine            = "mysql"
  engine_version    = "8.0"
  instance_class    = "db.t3.medium"
  allocated_storage = 100
  max_allocated_storage = 1000
  
  db_name  = "tecnocursos"
  username = "admin"
  manage_master_user_password = true
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  
  maintenance_window = "Mon:00:00-Mon:03:00"
  backup_window      = "03:00-06:00"
  
  monitoring_interval    = "30"
  monitoring_role_name   = "${local.name}-RDSEnhancedMonitoringRole"
  create_monitoring_role = true
  
  tags = local.tags
  
  # DB subnet group
  create_db_subnet_group = true
  subnet_ids             = module.vpc.private_subnets
  
  # DB parameter group
  family = "mysql8.0"
  
  # DB option group
  major_engine_version = "8.0"
  
  # Database Deletion Protection
  deletion_protection = true
  
  enabled_cloudwatch_logs_exports = ["audit", "error", "general", "slowquery"]
  create_cloudwatch_log_group     = true
  
  backup_retention_period = 7
  copy_tags_to_snapshot  = true
  
  performance_insights_enabled = true
  performance_insights_retention_period = 7
  
  create_db_parameter_group = true
  parameters = [
    {
      name  = "innodb_buffer_pool_size"
      value = "134217728"
    }
  ]
}

resource "aws_security_group" "rds" {
  name_prefix = "${local.name}-rds"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = [local.vpc_cidr]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(local.tags, {
    Name = "${local.name}-rds"
  })
}

# ============================================================================
# ELASTICACHE REDIS
# ============================================================================

resource "aws_elasticache_subnet_group" "redis" {
  name       = "${local.name}-redis-subnet"
  subnet_ids = module.vpc.private_subnets
  
  tags = local.tags
}

resource "aws_security_group" "redis" {
  name_prefix = "${local.name}-redis"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [local.vpc_cidr]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(local.tags, {
    Name = "${local.name}-redis"
  })
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "${local.name}-redis"
  description                = "Redis cluster for TecnoCursos AI"
  
  node_type                  = "cache.t3.micro"
  port                       = 6379
  parameter_group_name       = "default.redis7"
  
  num_cache_clusters         = 2
  automatic_failover_enabled = true
  multi_az_enabled          = true
  
  subnet_group_name = aws_elasticache_subnet_group.redis.name
  security_group_ids = [aws_security_group.redis.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  maintenance_window = "sun:05:00-sun:09:00"
  snapshot_window    = "02:00-05:00"
  snapshot_retention_limit = 5
  
  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis.name
    destination_type = "cloudwatch-logs"
    log_format       = "text"
    log_type         = "slow-log"
  }
  
  tags = local.tags
}

resource "aws_cloudwatch_log_group" "redis" {
  name              = "/aws/elasticache/${local.name}"
  retention_in_days = 7
  
  tags = local.tags
}

# ============================================================================
# S3 BUCKETS
# ============================================================================

resource "aws_s3_bucket" "media" {
  bucket = "${local.name}-media-${random_string.bucket_suffix.result}"
  
  tags = local.tags
}

resource "aws_s3_bucket_public_access_block" "media" {
  bucket = aws_s3_bucket.media.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "media" {
  bucket = aws_s3_bucket.media.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "media" {
  bucket = aws_s3_bucket.media.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "media" {
  bucket = aws_s3_bucket.media.id
  
  rule {
    id     = "delete_old_versions"
    status = "Enabled"
    
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
  
  rule {
    id     = "transition_to_ia"
    status = "Enabled"
    
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# ============================================================================
# CLOUDFRONT DISTRIBUTION
# ============================================================================

resource "aws_cloudfront_distribution" "media" {
  origin {
    domain_name = aws_s3_bucket.media.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.media.bucket}"
    
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.media.cloudfront_access_identity_path
    }
  }
  
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "TecnoCursos AI Media Distribution"
  default_root_object = "index.html"
  
  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.media.bucket}"
    
    forwarded_values {
      query_string = false
      
      cookies {
        forward = "none"
      }
    }
    
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }
  
  price_class = "PriceClass_All"
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  viewer_certificate {
    cloudfront_default_certificate = true
  }
  
  tags = local.tags
}

resource "aws_cloudfront_origin_access_identity" "media" {
  comment = "TecnoCursos AI Media OAI"
}

# ============================================================================
# ALB FOR EKS
# ============================================================================

module "alb_controller" {
  source = "terraform-aws-modules/eks/aws//modules/aws-load-balancer-controller"
  
  cluster_name                             = module.eks.cluster_name
  cluster_endpoint                         = module.eks.cluster_endpoint
  cluster_version                          = module.eks.cluster_version
  oidc_provider_arn                        = module.eks.oidc_provider_arn
  
  tags = local.tags
}

# ============================================================================
# MONITORING AND LOGGING
# ============================================================================

resource "aws_cloudwatch_log_group" "application" {
  name              = "/aws/eks/${local.name}/application"
  retention_in_days = 7
  
  tags = local.tags
}

# ============================================================================
# OUTPUTS
# ============================================================================

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ids attached to the cluster control plane"
  value       = module.eks.cluster_security_group_id
}

output "cluster_name" {
  description = "Kubernetes Cluster Name"
  value       = module.eks.cluster_name
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = module.rds.db_instance_endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
  sensitive   = true
}

output "s3_bucket_media" {
  description = "S3 bucket name for media files"
  value       = aws_s3_bucket.media.bucket
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.media.domain_name
} 