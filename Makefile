# Azure gpu vars
GPU_VM_SIZE ?= Standard_NC8as_T4_v3
GPU_REPLICAS ?= 1
OVERRIDE_ZONE ?=

# Override the install target to include EDB pull secret creation
.PHONY: install
install: create-edb-pull-secret pattern-install ## Installs the pattern onto a cluster (creates EDB pull secret first, then loads secrets)

.PHONY: create-edb-pull-secret
create-edb-pull-secret: ## Creates the EDB operator pull secret from values-secret.yaml
	@echo "Creating EDB Postgres Operator pull secret..."
	@ansible-playbook ansible/playbooks/create-edb-pull-secret.yaml

.PHONY: create-gpu-machineset
create-gpu-machineset: ## Creates a gpu machineset for AWS
	ansible-playbook ansible/playbooks/create-gpu-machineset.yaml

.PHONY: create-gpu-machineset-azure
create-gpu-machineset-azure: ## Creates an Azure GPU machineset (overrides: GPU_VM_SIZE, GPU_REPLICAS, OVERRIDE_ZONE)
	ansible-playbook ansible/playbooks/create-gpu-machineset-azure.yaml \
		-e "gpu_vm_size=$(GPU_VM_SIZE) gpu_replicas=$(GPU_REPLICAS) override_zone=$(OVERRIDE_ZONE)"

# Include common Makefile targets (after our overrides)
include Makefile-common
