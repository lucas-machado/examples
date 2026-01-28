output "model_repository_bucket_name" {
  value = aws_s3_bucket.triton_models.id
}

output "eks_connect_command" {
  value = "aws eks update-kubeconfig --name ${module.eks.cluster_name} --region us-east-1"
}

output "triton_iam_role_arn" {
  value = module.triton_irsa_role.iam_role_arn
}