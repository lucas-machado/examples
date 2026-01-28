# 1. Definimos a "Política": O QUE pode ser feito e ONDE.
resource "aws_iam_policy" "triton_s3_policy" {
  name        = "TritonS3ReadPolicy"
  description = "Permite que o Triton leia modelos do bucket S3"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["s3:GetObject", "s3:ListBucket"]
        Effect   = "Allow"
        Resource = [
          aws_s3_bucket.triton_models.arn,
          "${aws_s3_bucket.triton_models.arn}/*"
        ]
      }
    ]
  })
}

# 2. Criamos a "Role": A Identidade que o Kubernetes vai assumir.
module "triton_irsa_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "triton-s3-access-role"

  # Aqui o Terraform faz a ponte: conecta o OIDC do cluster com a Role da AWS
  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["default:triton-server-sa"] # Namespace:NomeDoServiceAccount
    }
  }

  role_policy_arns = {
    policy = aws_iam_policy.triton_s3_policy.arn
  }
}