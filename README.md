# Document Generation Demo with LLM and RAG

## Introduction

This deployment is based on `validated pattern framework` that uses GitOps to easily provision all operators and apps. It deploys a Chatbot application that leverages the power of Large Language Models (LLMs) in conjunction with the Retrieval-Augmented Generation (RAG) framework running on Red Hat OpenShift to generate a project proposal for a given Red Hat product.

## Pre-requisites

- Podman
- Red Hat Openshift cluster
- [GPU Node](./GPU_provisioning.md) to run Hugging Face Text Generation Inference server on Red Hat OpenShift cluster.
- Create a fork of the [rag-llm-gitops](https://github.com/validatedpatterns/rag-llm-gitops.git) git repository.

## Demo Description & Architecture

The goal of this demo is to demonstrate a Chatbot LLM application augmented with RAG content running on Red Hat OpenShift. It deploys an LLM application that connects to multiple LLM providers such as OpenAI, Hugging Face, and NVIDIA NIM. The application generates a project proposal for a Red Hat product

### Key Features

- LLM Application augmented with RAG content of Red Hat products
- Multiple LLM providers (OpenAI, Hugging Face, NVIDIA)
- Redis Vector Database for RAG content
- Monitoring dashboard to provide key metrics such as ratings
- GitOps setup to deploy e2e demo (frontend / vector database / served models)

![Diagram](images/diagram.PNG)

## Deploying the demo

Following commands will take about 15-20 minutes
>**Validated pattern will be deployed**

```sh
git clone https://github.com/<<your-username>>/rag-llm-gitops.git
cd rag-llm-gitops
oc login --token=<> --server=<> # login to Openshift cluster
podman machine start
cp values-secret.yaml.template ~/values-secret-rag-llm-gitops.yaml
./pattern.sh make install
```

### 1: Verify the installation

### 2: Launch the application

### 3: Generate the proposal document

### 4: Add an OpenAI provider

### 5: Generate the proposal document using OpenAI provider

### 6: Rating the provider

### 7: Metrics dashboard
