
# internet gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.gearup-vpc.id

  tags = {
    project = "Gearup"
  }
}

# elastic ip

resource "aws_eip" "nat_eip" {
  # vpc = true
  depends_on = [aws_internet_gateway.igw]
}

# nat gateway
resource "aws_nat_gateway" "ngw" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.privatesubnet-us-east-1a.id

  tags = {
    project = "Gearup"
  }
  depends_on = [aws_internet_gateway.igw]
}
