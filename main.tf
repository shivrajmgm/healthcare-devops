provider "aws" {
  region = "ap-south-1" # Mumbai Region
}

resource "aws_security_group" "app_sg" {
  name        = "healthcare-app-sg"
  description = "Allow web traffic"

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "healthcare_server" {
  ami           = "ami-0c2af51e265bd5e0e" # Ubuntu Server
  instance_type = "t2.micro"              # Free tier eligible
  security_groups = [aws_security_group.app_sg.name]

  tags = {
    Name = "Healthcare-Production-Server"
  }
}