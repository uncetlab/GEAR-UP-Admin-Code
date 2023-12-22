resource "aws_s3_bucket_ownership_controls" "gearupappbucket_ownership_control" {
  bucket = aws_s3_bucket.gearupappbucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "gearupappbucket_acl" {
  depends_on = [aws_s3_bucket_ownership_controls.gearupappbucket_ownership_control]

  bucket = aws_s3_bucket.gearupappbucket.id
  acl    = "private"
}
