
resource "aws_s3_bucket" "gearupappbucket" {
  bucket = "gearupappbucket"

  tags = {
    Name = "gearupapp"
  }
}

resource "aws_s3_bucket_versioning" "gearupappbucket_versioning" {
  bucket = aws_s3_bucket.gearupappbucket.id
  versioning_configuration {
    status = "Enabled"
  }
}
