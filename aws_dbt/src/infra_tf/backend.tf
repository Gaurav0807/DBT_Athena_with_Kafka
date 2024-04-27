terraform {
  backend "s3" {
    bucket = "aws-dbt-kafka-demo-bucket"
    key = "terraform_state_file/de_terraform.tfstate"
    region = "us-east-1"
  }
}