# ============================================================================
# TERRAFORM VARIABLES - TECNOCURSOS AI PRODUCTION
# ============================================================================
# 
# Definição de variáveis para configuração da infraestrutura
# Seguindo as melhores práticas de:
# - Terraform variable conventions
# - Type safety
# - Documentation
# - Default values
# - Validation
#
# Autor: TecnoCursos AI System
# Data: 17/01/2025
# ============================================================================

# ============================================================================
# GENERAL CONFIGURATION
# ============================================================================

variable "environment" {
  description = "Environment name (production, staging, development)"
  type        = string
  default     = "production"
  
  validation {
    condition     = contains(["production", "staging", "development"], var.environment)
    error_message = "Environment must be production, staging, or development."
  }
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "tecnocursos-ai"
  
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Project name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "owner" {
  description = "Owner of the infrastructure"
  type        = string
  default     = "DevOps Team"
}

variable "contact_email" {
  description = "Contact email for infrastructure issues"
  type        = string
  default     = "devops@tecnocursos.ai"
  
  validation {
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.contact_email))
    error_message = "Contact email must be a valid email address."
  }
}

# ============================================================================
# AWS CONFIGURATION
# ============================================================================

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
  
  validation {
    condition = contains([
      "us-east-1", "us-east-2", "us-west-1", "us-west-2",
      "eu-west-1", "eu-west-2", "eu-central-1",
      "ap-southeast-1", "ap-southeast-2", "ap-northeast-1",
      "sa-east-1"
    ], var.aws_region)
    error_message = "AWS region must be a valid AWS region."
  }
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

# ============================================================================
# NETWORKING CONFIGURATION
# ============================================================================

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
  
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use single NAT Gateway (cost optimization)"
  type        = bool
  default     = false
}

variable "enable_vpn_gateway" {
  description = "Enable VPN Gateway"
  type        = bool
  default     = false
}

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames in VPC"
  type        = bool
  default     = true
}

variable "enable_dns_support" {
  description = "Enable DNS support in VPC"
  type        = bool
  default     = true
}

# ============================================================================
# EKS CLUSTER CONFIGURATION
# ============================================================================

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = ""
}

variable "cluster_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"
  
  validation {
    condition     = can(regex("^1\\.(2[4-9]|[3-9][0-9])$", var.cluster_version))
    error_message = "Cluster version must be a valid Kubernetes version (1.24 or higher)."
  }
}

variable "cluster_endpoint_public_access" {
  description = "Enable public API server endpoint"
  type        = bool
  default     = true
}

variable "cluster_endpoint_private_access" {
  description = "Enable private API server endpoint"
  type        = bool
  default     = true
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "List of CIDR blocks that can access the Amazon EKS public API server endpoint"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "create_aws_auth_configmap" {
  description = "Whether to create the aws-auth configmap"
  type        = bool
  default     = true
}

variable "manage_aws_auth_configmap" {
  description = "Whether to manage the aws-auth configmap"
  type        = bool
  default     = true
}

# ============================================================================
# NODE GROUPS CONFIGURATION
# ============================================================================

variable "node_groups" {
  description = "Map of EKS managed node group definitions"
  type = map(object({
    instance_types = list(string)
    min_size       = number
    max_size       = number
    desired_size   = number
    capacity_type  = string
    ami_type       = string
    disk_size      = number
    labels         = map(string)
    taints = list(object({
      key    = string
      value  = string
      effect = string
    }))
  }))
  
  default = {
    general = {
      instance_types = ["t3.large"]
      min_size       = 2
      max_size       = 10
      desired_size   = 3
      capacity_type  = "ON_DEMAND"
      ami_type       = "AL2_x86_64"
      disk_size      = 100
      labels         = {}
      taints         = []
    }
    
    video_processing = {
      instance_types = ["c5.2xlarge"]
      min_size       = 1
      max_size       = 5
      desired_size   = 1
      capacity_type  = "SPOT"
      ami_type       = "AL2_x86_64"
      disk_size      = 200
      labels = {
        workload = "video-processing"
      }
      taints = [
        {
          key    = "video-processing"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      ]
    }
  }
}

# ============================================================================
# RDS CONFIGURATION
# ============================================================================

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
  
  validation {
    condition = contains([
      "db.t3.micro", "db.t3.small", "db.t3.medium", "db.t3.large",
      "db.r5.large", "db.r5.xlarge", "db.r5.2xlarge"
    ], var.rds_instance_class)
    error_message = "RDS instance class must be a valid DB instance type."
  }
}

variable "rds_allocated_storage" {
  description = "Initial allocated storage for RDS (GB)"
  type        = number
  default     = 100
  
  validation {
    condition     = var.rds_allocated_storage >= 20 && var.rds_allocated_storage <= 65536
    error_message = "RDS allocated storage must be between 20 and 65536 GB."
  }
}

variable "rds_max_allocated_storage" {
  description = "Maximum allocated storage for RDS auto-scaling (GB)"
  type        = number
  default     = 1000
  
  validation {
    condition     = var.rds_max_allocated_storage >= var.rds_allocated_storage
    error_message = "RDS max allocated storage must be greater than or equal to allocated storage."
  }
}

variable "rds_engine_version" {
  description = "MySQL engine version"
  type        = string
  default     = "8.0"
  
  validation {
    condition     = contains(["8.0", "5.7"], var.rds_engine_version)
    error_message = "RDS engine version must be 8.0 or 5.7."
  }
}

variable "rds_backup_retention_period" {
  description = "Backup retention period in days"
  type        = number
  default     = 7
  
  validation {
    condition     = var.rds_backup_retention_period >= 0 && var.rds_backup_retention_period <= 35
    error_message = "RDS backup retention period must be between 0 and 35 days."
  }
}

variable "rds_backup_window" {
  description = "Preferred backup window"
  type        = string
  default     = "03:00-06:00"
}

variable "rds_maintenance_window" {
  description = "Preferred maintenance window"
  type        = string
  default     = "Mon:00:00-Mon:03:00"
}

variable "rds_deletion_protection" {
  description = "Enable deletion protection for RDS"
  type        = bool
  default     = true
}

variable "rds_multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = true
}

variable "rds_performance_insights_enabled" {
  description = "Enable Performance Insights"
  type        = bool
  default     = true
}

# ============================================================================
# REDIS CONFIGURATION
# ============================================================================

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.micro"
  
  validation {
    condition = contains([
      "cache.t3.micro", "cache.t3.small", "cache.t3.medium",
      "cache.r5.large", "cache.r5.xlarge"
    ], var.redis_node_type)
    error_message = "Redis node type must be a valid ElastiCache node type."
  }
}

variable "redis_num_cache_clusters" {
  description = "Number of cache clusters (nodes) in the replication group"
  type        = number
  default     = 2
  
  validation {
    condition     = var.redis_num_cache_clusters >= 1 && var.redis_num_cache_clusters <= 6
    error_message = "Redis num cache clusters must be between 1 and 6."
  }
}

variable "redis_parameter_group_name" {
  description = "Parameter group name for Redis"
  type        = string
  default     = "default.redis7"
}

variable "redis_port" {
  description = "Port number for Redis"
  type        = number
  default     = 6379
  
  validation {
    condition     = var.redis_port > 0 && var.redis_port <= 65535
    error_message = "Redis port must be between 1 and 65535."
  }
}

variable "redis_snapshot_retention_limit" {
  description = "Number of days to retain automatic snapshots"
  type        = number
  default     = 5
  
  validation {
    condition     = var.redis_snapshot_retention_limit >= 0 && var.redis_snapshot_retention_limit <= 35
    error_message = "Redis snapshot retention limit must be between 0 and 35 days."
  }
}

variable "redis_snapshot_window" {
  description = "Daily time range for automatic snapshots"
  type        = string
  default     = "02:00-05:00"
}

variable "redis_maintenance_window" {
  description = "Weekly time range for maintenance"
  type        = string
  default     = "sun:05:00-sun:09:00"
}

variable "redis_at_rest_encryption_enabled" {
  description = "Enable encryption at rest for Redis"
  type        = bool
  default     = true
}

variable "redis_transit_encryption_enabled" {
  description = "Enable encryption in transit for Redis"
  type        = bool
  default     = true
}

# ============================================================================
# S3 CONFIGURATION
# ============================================================================

variable "s3_bucket_versioning" {
  description = "Enable versioning for S3 bucket"
  type        = bool
  default     = true
}

variable "s3_lifecycle_transitions" {
  description = "S3 lifecycle transitions"
  type = list(object({
    days          = number
    storage_class = string
  }))
  default = [
    {
      days          = 30
      storage_class = "STANDARD_IA"
    },
    {
      days          = 90
      storage_class = "GLACIER"
    }
  ]
}

variable "s3_noncurrent_version_expiration_days" {
  description = "Days after which noncurrent versions expire"
  type        = number
  default     = 30
  
  validation {
    condition     = var.s3_noncurrent_version_expiration_days > 0
    error_message = "S3 noncurrent version expiration days must be greater than 0."
  }
}

# ============================================================================
# CLOUDFRONT CONFIGURATION
# ============================================================================

variable "cloudfront_price_class" {
  description = "CloudFront distribution price class"
  type        = string
  default     = "PriceClass_All"
  
  validation {
    condition = contains([
      "PriceClass_All", "PriceClass_200", "PriceClass_100"
    ], var.cloudfront_price_class)
    error_message = "CloudFront price class must be PriceClass_All, PriceClass_200, or PriceClass_100."
  }
}

variable "cloudfront_default_ttl" {
  description = "Default TTL for CloudFront distribution"
  type        = number
  default     = 3600
  
  validation {
    condition     = var.cloudfront_default_ttl >= 0
    error_message = "CloudFront default TTL must be 0 or greater."
  }
}

variable "cloudfront_max_ttl" {
  description = "Maximum TTL for CloudFront distribution"
  type        = number
  default     = 86400
  
  validation {
    condition     = var.cloudfront_max_ttl >= var.cloudfront_default_ttl
    error_message = "CloudFront max TTL must be greater than or equal to default TTL."
  }
}

# ============================================================================
# MONITORING CONFIGURATION
# ============================================================================

variable "cloudwatch_log_retention_days" {
  description = "CloudWatch log retention period in days"
  type        = number
  default     = 7
  
  validation {
    condition = contains([
      1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653
    ], var.cloudwatch_log_retention_days)
    error_message = "CloudWatch log retention days must be a valid retention period."
  }
}

variable "enable_container_insights" {
  description = "Enable CloudWatch Container Insights for EKS"
  type        = bool
  default     = true
}

variable "enable_application_insights" {
  description = "Enable CloudWatch Application Insights"
  type        = bool
  default     = true
}

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

variable "enable_guardduty" {
  description = "Enable GuardDuty for threat detection"
  type        = bool
  default     = true
}

variable "enable_config" {
  description = "Enable AWS Config for compliance monitoring"
  type        = bool
  default     = true
}

variable "enable_cloudtrail" {
  description = "Enable CloudTrail for API logging"
  type        = bool
  default     = true
}

variable "enable_security_hub" {
  description = "Enable Security Hub for security findings"
  type        = bool
  default     = true
}

variable "kms_key_deletion_window" {
  description = "KMS key deletion window in days"
  type        = number
  default     = 7
  
  validation {
    condition     = var.kms_key_deletion_window >= 7 && var.kms_key_deletion_window <= 30
    error_message = "KMS key deletion window must be between 7 and 30 days."
  }
}

# ============================================================================
# COST OPTIMIZATION
# ============================================================================

variable "enable_cost_optimization" {
  description = "Enable cost optimization features"
  type        = bool
  default     = true
}

variable "spot_instance_percentage" {
  description = "Percentage of spot instances to use"
  type        = number
  default     = 50
  
  validation {
    condition     = var.spot_instance_percentage >= 0 && var.spot_instance_percentage <= 100
    error_message = "Spot instance percentage must be between 0 and 100."
  }
}

variable "enable_scheduled_scaling" {
  description = "Enable scheduled scaling for non-production hours"
  type        = bool
  default     = true
}

# ============================================================================
# BACKUP CONFIGURATION
# ============================================================================

variable "backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 30
  
  validation {
    condition     = var.backup_retention_days >= 1 && var.backup_retention_days <= 365
    error_message = "Backup retention days must be between 1 and 365."
  }
}

variable "backup_schedule" {
  description = "Cron expression for backup schedule"
  type        = string
  default     = "cron(0 2 * * ? *)"  # Daily at 2 AM UTC
}

variable "enable_cross_region_backup" {
  description = "Enable cross-region backup replication"
  type        = bool
  default     = true
}

# ============================================================================
# DISASTER RECOVERY
# ============================================================================

variable "enable_disaster_recovery" {
  description = "Enable disaster recovery setup"
  type        = bool
  default     = true
}

variable "dr_region" {
  description = "Disaster recovery region"
  type        = string
  default     = "us-west-2"
}

variable "rpo_target_minutes" {
  description = "Recovery Point Objective in minutes"
  type        = number
  default     = 60
  
  validation {
    condition     = var.rpo_target_minutes > 0
    error_message = "RPO target must be greater than 0 minutes."
  }
}

variable "rto_target_minutes" {
  description = "Recovery Time Objective in minutes"
  type        = number
  default     = 240
  
  validation {
    condition     = var.rto_target_minutes > 0
    error_message = "RTO target must be greater than 0 minutes."
  }
}

# ============================================================================
# FEATURE FLAGS
# ============================================================================

variable "feature_flags" {
  description = "Feature flags for conditional resource creation"
  type = object({
    enable_waf                = bool
    enable_shield_advanced    = bool
    enable_api_gateway        = bool
    enable_lambda_functions   = bool
    enable_step_functions     = bool
    enable_eventbridge        = bool
    enable_sns_notifications  = bool
    enable_sqs_queues        = bool
  })
  
  default = {
    enable_waf                = false
    enable_shield_advanced    = false
    enable_api_gateway        = false
    enable_lambda_functions   = false
    enable_step_functions     = false
    enable_eventbridge        = false
    enable_sns_notifications  = true
    enable_sqs_queues        = true
  }
}

# ============================================================================
# RESOURCE TAGS
# ============================================================================

variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
} 