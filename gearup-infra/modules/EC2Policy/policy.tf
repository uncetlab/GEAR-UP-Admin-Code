resource "aws_iam_instance_profile" "gearup_beanstalk_instance_profile" {
  name = "gearup_beanstalk_instance_profile"
  role = aws_iam_role.gearup-aws-elasticbeanstalk-ec2-role.name
}

resource "aws_iam_role" "gearup-aws-elasticbeanstalk-ec2-role" {
  name = "gearup-aws-elasticbeanstalk-ec2-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "AWSElasticBeanstalkMulticontainerDocker_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkMulticontainerDocker"
  role       = aws_iam_role.gearup-aws-elasticbeanstalk-ec2-role.name
}

resource "aws_iam_role_policy_attachment" "AWSElasticBeanstalkWebTier_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"
  role       = aws_iam_role.gearup-aws-elasticbeanstalk-ec2-role.name
}
resource "aws_iam_role_policy_attachment" "AWSElasticBeanstalkWorkerTier_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWorkerTier"
  role       = aws_iam_role.gearup-aws-elasticbeanstalk-ec2-role.name
}
