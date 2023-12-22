
resource "tls_private_key" "gearup-key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "gearup-key" {
  key_name   = "gearup-key"
  public_key = tls_private_key.gearup-key.public_key_openssh
}

resource "local_file" "ssh_key" {
  filename = "${aws_key_pair.gearup-key.key_name}.pem"
  content  = tls_private_key.gearup-key.private_key_pem
}
