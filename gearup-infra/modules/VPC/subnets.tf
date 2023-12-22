
# subnets
resource "aws_subnet" "publicsubnet-us-east-1a" {
  vpc_id                  = aws_vpc.gearup-vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = "true"

  tags = {
    project = "Gearup"
  }
}

resource "aws_subnet" "privatesubnet-us-east-1a" {
  vpc_id            = aws_vpc.gearup-vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1a"

  tags = {
    project = "Gearup"
  }
}


resource "aws_subnet" "publicsubnet-us-east-1b" {
  vpc_id                  = aws_vpc.gearup-vpc.id
  cidr_block              = "10.0.3.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = "true"

  tags = {
    project = "Gearup"
  }
}

resource "aws_subnet" "privatesubnet-us-east-1b" {
  vpc_id            = aws_vpc.gearup-vpc.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = "us-east-1b"

  tags = {
    project = "Gearup"
  }
}


resource "aws_subnet" "publicsubnet-us-east-1c" {
  vpc_id                  = aws_vpc.gearup-vpc.id
  cidr_block              = "10.0.5.0/24"
  availability_zone       = "us-east-1c"
  map_public_ip_on_launch = "true"

  tags = {
    project = "Gearup"
  }
}

resource "aws_subnet" "privatesubnet-us-east-1c" {
  vpc_id            = aws_vpc.gearup-vpc.id
  cidr_block        = "10.0.6.0/24"
  availability_zone = "us-east-1c"

  tags = {
    project = "Gearup"
  }
}
