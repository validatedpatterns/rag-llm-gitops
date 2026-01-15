include Makefile-common

# Azure gpu vars
GPU_VM_SIZE ?= Standard_NC8as_T4_v3
GPU_REPLICAS ?= 1
OVERRIDE_ZONE ?=

.PHONY: create-gpu-machineset
create-gpu-machineset: ## Creates a gpu machineset for AWS
	ansible-playbook ansible/playbooks/create-gpu-machineset.yaml

.PHONY: create-gpu-machineset-azure
create-gpu-machineset-azure: ## Creates an Azure GPU machineset (overrides: GPU_VM_SIZE, GPU_REPLICAS, OVERRIDE_ZONE)
	ansible-playbook ansible/playbooks/create-gpu-machineset-azure.yaml \
		-e "gpu_vm_size=$(GPU_VM_SIZE) gpu_replicas=$(GPU_REPLICAS) override_zone=$(OVERRIDE_ZONE)"
