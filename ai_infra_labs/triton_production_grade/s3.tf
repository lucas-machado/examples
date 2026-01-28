resource "aws_s3_bucket" "triton_models" {
  bucket = "triton-model-repository-${random_id.suffix.hex}" # Nome único
}

resource "random_id" "suffix" {
  byte_length = 4
}