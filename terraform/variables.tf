variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "DigitalOcean region for the app droplet"
  type        = string
  default     = "sgp1"
}

variable "droplet_name" {
  description = "Name of the production droplet"
  type        = string
  default     = "siu-payment-anomaly-detector"
}

variable "droplet_size" {
  description = "Droplet size for the stack"
  type        = string
  default     = "s-2vcpu-2gb"
}
