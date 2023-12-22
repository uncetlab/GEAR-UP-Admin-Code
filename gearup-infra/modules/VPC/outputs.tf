output "publicsubnet-us-east-1a" {
  value = aws_subnet.publicsubnet-us-east-1a.id
}

output "privatesubnet-us-east-1a" {
  value = aws_subnet.privatesubnet-us-east-1a.id
}

output "publicsubnet-us-east-1b" {
  value = aws_subnet.publicsubnet-us-east-1b.id
}

output "privatesubnet-us-east-1b" {
  value = aws_subnet.privatesubnet-us-east-1b.id
}


output "publicsubnet-us-east-1c" {
  value = aws_subnet.publicsubnet-us-east-1c.id
}

output "privatesubnet-us-east-1c" {
  value = aws_subnet.privatesubnet-us-east-1c.id
}

output "db-gearup-sg" {
  value = aws_security_group.db-gearup-sg.id
}

output "gearup-sg" {
  value = aws_security_group.gearup-sg.id
}

output "gearpu-vpc-id" {
  value = aws_vpc.gearup-vpc.id
}
