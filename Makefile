# Azure gpu vars
GPU_VM_SIZE ?= Standard_NC8as_T4_v3
GPU_REPLICAS ?= 1
OVERRIDE_ZONE ?=

.PHONY: default
default: help

.PHONY: help
##@ Pattern tasks

# No need to add a comment here as help is described in common/
help:
	@make -f common/Makefile MAKEFILE_LIST="Makefile common/Makefile" help

%:
	make -f common/Makefile $*

.PHONY: install
install: operator-deploy post-install ## installs the pattern and loads the secrets
	@echo "Installed"

.PHONY: create-gpu-machineset
create-gpu-machineset: ## Creates a gpu machineset for AWS
	ansible-playbook ansible/playbooks/create-gpu-machineset.yaml

.PHONY: create-gpu-machineset-azure
create-gpu-machineset-azure: ## Creates an Azure GPU machineset (overrides: GPU_VM_SIZE, GPU_REPLICAS, OVERRIDE_ZONE)
	ansible-playbook ansible/playbooks/create-gpu-machineset-azure.yaml \
		-e "gpu_vm_size=$(GPU_VM_SIZE) gpu_replicas=$(GPU_REPLICAS) override_zone=$(OVERRIDE_ZONE)"

.PHONY: post-install
post-install: ## Post-install tasks
	make load-secrets
	@echo "Done"

.PHONY: test
test:
	@make -f common/Makefile PATTERN_OPTS="-f values-global.yaml -f values-hub.yaml" test
