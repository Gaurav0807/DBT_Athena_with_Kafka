provider "aws" {
    region = "us-east-1"
    alias = "aws_region" 
}

resource "aws_s3_bucket" "testing_bucket" {
    bucket = "aws-dbt-kafka-demo-bucket"
  
}