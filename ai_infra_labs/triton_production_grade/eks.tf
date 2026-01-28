module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "triton-inference-cluster"
  cluster_version = "1.31"

  enable_cluster_creator_admin_permissions = true

  # Permite acesso público para o nosso lab
  cluster_endpoint_public_access = true

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnets

  eks_managed_node_groups = {
    # Node para o Triton (Com GPU)
    gpu_nodes = {
      instance_types = ["g4dn.xlarge"] # GPU NVIDIA T4
      capacity_type  = "SPOT"          # Economia agressiva

      ami_type = "AL2_x86_64_GPU"

      min_size     = 1
      max_size     = 1
      desired_size = 1

      # Importante para Kubernetes com GPU
      labels = {
        "hardware-type" = "gpu"
      }
    }
  }
}