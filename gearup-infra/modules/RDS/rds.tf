resource "aws_db_subnet_group" "gearup_db_subnet_group" {
  name       = "gearup_db_subnet_group"
  subnet_ids = [var.privatesubnet-us-east-1b, var.privatesubnet-us-east-1c]

  tags = {
    project = "Gearup"
    Name    = "gearup_db"
  }
}

resource "aws_db_instance" "gearup_db" {
  identifier        = "gearupdb"
  allocated_storage = 20
  db_name           = "gearup_db"
  engine            = "postgres"
  # https://docs.aws.amazon.com/AmazonRDS/latest/PostgreSQLReleaseNotes/postgresql-versions.html
  # refer above for setting up engine version
  engine_version         = "13.7"
  instance_class         = "db.t3.medium"
  username               = "postgres"
  password               = "postgres"
  skip_final_snapshot    = true
  publicly_accessible    = false
  vpc_security_group_ids = [var.db-securitygroup]
  db_subnet_group_name   = aws_db_subnet_group.gearup_db_subnet_group.name
  multi_az               = false
}
