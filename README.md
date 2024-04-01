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

### Components deployed

The components are deployed in the rag-llm namespace.

- **TGIS Inference Server** A TGIS Inference server is deployed and is configured with Mistral-7b model.

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

- Login to the OpenShift web console.
- Navigate to the Workloads --> Pods.
- Select the `rag-llm` project from the drop down.
- Following pods should be up and running.
  
![Pods](images/rag-llm.PNG)

Note: If the hf-text-generation-server is not running, make sure you have followed the steps to configure a node with GPU from the [instructions](./GPU_provisioning.md) provided above.

### 2: Launch the application

- Navigate to routes, Networking --> Routes
  
  ![Routes](images/routes.PNG)

- Click on the Location link and it should launch the application
  
  ![Application](images/application.PNG)

### 3: Generate the proposal document

- It will use the default provider and model configured as part of the application deployment. The default provider is a Hugging Face model server running in the OpenShift. The model server is deployed with this valdiated pattern and requires a node with GPU.
- Enter any company name
- Enter the product as `RedHat OpenShift`
- Click the `Generate` button, a project proposal should be generated. The project proposal also contains the reference of the RAG content. The project proposal document can be Downloaded in the form of a PDF document.
  
  ![Routes](images/proposal.PNG)

### 4: Add an OpenAI provider

You can optionally add additional providers. The application supports the following providers

- Hugging Face Text Generation Inference Server
- OpenAI
- NVIDIA

Click on the `Add Provider` tab to add a new provider. Fill in the details and click `Add Provider` button. The provider should be added in the `Providers` dropdown uder `Chatbot` tab.

![Routes](images/add_provider.PNG)

### 5: Generate the proposal document using OpenAI provider

Follow the instructions in step 3 to generate the proposal document using the OpenAI provider.

![Routes](images/chatgpt.PNG)

### 6: Rating the provider

You can provide rating to the model by clicking on the `Rate the model` radio button. The rating will be captured as part of the metrics and can help the company which model to deploy in prodcution.
