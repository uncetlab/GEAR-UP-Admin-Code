resource "aws_vpc" "gearup-vpc" {
  cidr_block = var.cidr_block

  tags = {
    project = "Gearup"
    Name    = "Gearup-VPC"
  }
}
