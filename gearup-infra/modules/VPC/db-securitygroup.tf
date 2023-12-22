resource "aws_security_group" "db-gearup-sg" {
  name        = "db-gearup-sg"
  description = "access internet public"
  vpc_id      = aws_vpc.gearup-vpc.id
  tags = {
    Name = "db-gearup-sg"
  }
}


resource "aws_security_group_rule" "external-postgres-access" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.gearup-sg.id
  security_group_id        = aws_security_group.db-gearup-sg.id

}

resource "aws_security_group_rule" "postgres-access" {
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  self              = true
  security_group_id = aws_security_group.db-gearup-sg.id
}
