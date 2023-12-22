resource "aws_elastic_beanstalk_application" "gearupapp" {
  name        = "gearupapp"
  description = "gearupapp backend application"
  tags = {
    Name = "gearupapp"
  }
}
