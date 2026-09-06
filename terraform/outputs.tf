output "public_ip" {
  description = "Public IP of the deployed droplet"
  value       = digitalocean_droplet.app.ipv4_address
}

output "vpc_id" {
  description = "VPC ID used by the project"
  value       = digitalocean_vpc.main.id
}
