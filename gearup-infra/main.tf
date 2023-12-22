# for network
module "gearup_vpc" {
  source = "./modules/VPC"
}

# for database
module "gearup_rds" {
  source                   = "./modules/RDS"
  db-securitygroup         = module.gearup_vpc.db-gearup-sg
  privatesubnet-us-east-1b = module.gearup_vpc.privatesubnet-us-east-1b
  privatesubnet-us-east-1c = module.gearup_vpc.privatesubnet-us-east-1c
}

# for static files

module "s3" {
  source = "./modules/S3"
}

module "EC2Policy" {
  source = "./modules/EC2Policy"

}
# for application
module "EB" {
  source                            = "./modules/EB"
  gearpu-vpc-id                     = module.gearup_vpc.gearpu-vpc-id
  gearup_beanstalk_instance_profile = module.EC2Policy.gearup_beanstalk_instance_profile
  publicsubnet-us-east-1a           = module.gearup_vpc.publicsubnet-us-east-1a
  publicsubnet-us-east-1b           = module.gearup_vpc.publicsubnet-us-east-1b
  publicsubnet-us-east-1c           = module.gearup_vpc.publicsubnet-us-east-1c
  gearup-sg                         = module.gearup_vpc.gearup-sg
}
