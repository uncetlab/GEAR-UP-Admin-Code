resource "aws_security_group" "gearup-sg" {
  name        = "gearup-sg"
  description = "access internet public"
  vpc_id      = aws_vpc.gearup-vpc.id
  tags = {
    Name = "gearup-sg"
  }
}


resource "aws_security_group_rule" "ssh-access-public" {
  type        = "ingress"
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = aws_security_group.gearup-sg.id
}

resource "aws_security_group_rule" "http-public" {
  type        = "ingress"
  from_port   = 80
  to_port     = 80
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = aws_security_group.gearup-sg.id
}

resource "aws_security_group_rule" "https-public" {
  type        = "ingress"
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = aws_security_group.gearup-sg.id
}


resource "aws_security_group_rule" "access_public_network" {
  type        = "egress"
  from_port   = 0
  to_port     = 0
  protocol    = "-1"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = aws_security_group.gearup-sg.id

}
