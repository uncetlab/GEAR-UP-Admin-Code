resource "aws_elastic_beanstalk_environment" "gearup360" {
  name                = "gearup360"
  application         = aws_elastic_beanstalk_application.gearupapp.name
  solution_stack_name = "64bit Amazon Linux 2023 v4.1.2 running Docker"
  tier                = "WebServer"


  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "IamInstanceProfile"
    value     = var.gearup_beanstalk_instance_profile.name
  }
  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "InstanceType"
    value     = "t2.medium"
  }
  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "EC2KeyName"
    value     = aws_key_pair.gearup-key.key_name
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "VPCId"
    value     = var.gearpu-vpc-id
  }

  setting {
    namespace = "aws:ec2:vpc"
    name      = "Subnets"
    value     = var.publicsubnet-us-east-1b
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "SecurityGroups"
    value     = var.gearup-sg
  }
}
