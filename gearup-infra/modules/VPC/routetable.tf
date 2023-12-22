
# route table private

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.gearup-vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.ngw.id
  }

  tags = {
    project = "Gearup"
  }
}
# associations private
resource "aws_route_table_association" "private-us-east-1a" {
  subnet_id      = aws_subnet.privatesubnet-us-east-1a.id
  route_table_id = aws_route_table.private.id
}
resource "aws_route_table_association" "private-us-east-1b" {
  subnet_id      = aws_subnet.privatesubnet-us-east-1b.id
  route_table_id = aws_route_table.private.id
}
resource "aws_route_table_association" "private-us-east-1c" {
  subnet_id      = aws_subnet.privatesubnet-us-east-1c.id
  route_table_id = aws_route_table.private.id
}


# route table public
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.gearup-vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    project = "Gearup"
  }
}

# associations public
resource "aws_route_table_association" "public-us-east-1a" {
  subnet_id      = aws_subnet.publicsubnet-us-east-1a.id
  route_table_id = aws_route_table.public.id
}
resource "aws_route_table_association" "public-us-east-1b" {
  subnet_id      = aws_subnet.publicsubnet-us-east-1b.id
  route_table_id = aws_route_table.public.id
}
resource "aws_route_table_association" "public-us-east-1c" {
  subnet_id      = aws_subnet.publicsubnet-us-east-1c.id
  route_table_id = aws_route_table.public.id
}
