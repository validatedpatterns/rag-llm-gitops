# Document Generation Demo with LLM and RAG

## Introduction

This deployment is based on `validated pattern framework` that uses GitOps to easily provision all operators and apps. It deploys a Chatbot application that leverages the power of Large Language Models (LLMs) in conjunction with the Retrieval-Augmented Generation (RAG) framework running on Red Hat OpenShift to generate a project proposal for a given Red Hat product.

## Pre-requisites

- Podman
- Red Hat Openshift cluster running in AWS. Supported regions are us-west-2 and us-east-1.
- GPU Node to run Hugging Face Text Generation Inference server on Red Hat OpenShift cluster.
- Create a fork of the [rag-llm-gitops](https://github.com/validatedpatterns/rag-llm-gitops.git) git repository.

## Demo Description & Architecture

The goal of this demo is to demonstrate a Chatbot LLM application augmented with data from Red Hat product documentation running on Red Hat OpenShift. It deploys an LLM application that connects to multiple LLM providers such as OpenAI, Hugging Face, and NVIDIA NIM. The application generates a project proposal for a Red Hat product

### Key Features

- LLM Application augmented with content from Red Hat product documentation.
- Multiple LLM providers (OpenAI, Hugging Face, NVIDIA)
- Redis Vector Database to store embeddings of RedHat product documentation.
- Monitoring dashboard to provide key metrics such as ratings
- GitOps setup to deploy e2e demo (frontend / vector database / served models)


![Overview](https://gitlab.com/osspa/portfolio-architecture-examples/-/raw/main/images/intro-marketectures/rag-demo-vp-marketing-slide.png)

_Figure 1. Overview of the validated pattern for RAG Demo with Red Hat OpenShift_


![Logical](https://gitlab.com/osspa/portfolio-architecture-examples/-/raw/main/images/logical-diagrams/rag-demo-vp-ld.png)

_Figure 2. Logical diagram of the RAG Demo with Red Hat OpenShift._


#### RAG Demo Workflow

![Overview of workflow](https://gitlab.com/osspa/portfolio-architecture-examples/-/raw/main/images/schematic-diagrams/rag-demo-vp-sd.png)

_Figure 3. Schematic diagram for workflow of RAG demo with Red Hat OpenShift._


#### RAG Data Ingestion

![ingestion](https://gitlab.com/osspa/portfolio-architecture-examples/-/raw/main/images/schematic-diagrams/rag-demo-vp-ingress-sd.png)

_Figure 4. Schematic diagram for Ingestion of data for RAG._


#### RAG Augmented Query


![query](https://gitlab.com/osspa/portfolio-architecture-examples/-/raw/main/images/schematic-diagrams/rag-demo-vp-query-sd.png)

_Figure 5. Schematic diagram for RAG demo augmented query._


In Figure 5, we can see RAG augmented query. Llama 2 model is used for for language processing, LangChain to
integrate different tools of the LLM-based application together and to process the PDF
files and web pages, Redis is used to store vectors, HuggingFace TGI is used to serve the Llama 2 model, Gradio is used for user interface and object storage to store language model and other datasets. Solution components are deployed as microservices in the Red Hat OpenShift cluster.


#### Download diagrams
View and download all of the diagrams above in our open source tooling site.

[Open Diagrams](https://www.redhat.com/architect/portfolio/tool/index.html?#gitlab.com/osspa/portfolio-architecture-examples/-/raw/main/diagrams/rag-demo-vp.drawio)




![Diagram](images/diagram.png)
_Figure 6. Proposed demo architecture with OpenShift AI_

### Components deployed

- **Hugging Face Text Generation Inference Server:** The pattern deploys a Hugging Face TGIS server. The server deploys `mistral-community/Mistral-7B-v0.2` model. The server will require a GPU node.
- **Redis Server:** A Redis Server is deployed to store vector embeddings created from Red Hat product documentation.
- **Populate VectorDb Job:** The job creates the embeddings and populates the vector database (Redis).
- **LLM Application:** This is a Chatbot application that can generate a project proposal by augmenting the LLM with the Red Hat product documentation stored in vector db.
- **Prometheus:** Deploys a prometheus instance to store the various metrics from the LLM application and TGIS server.
- **Grafana:** Deploys Grafana application to visualize the metrics.

## Deploying the demo

### Cloning repository

```sh
git clone https://github.com/<<your-username>>/rag-llm-gitops.git
cd rag-llm-gitops
oc login --token=<> --server=<> # login to Openshift cluster
podman machine start
# Copy values-secret.yaml.template to ~/values-secret-rag-llm-gitops.yaml.
# You should never check-in these files
# Add secrets to the values-secret.yaml that needs to be added to the vault.
cp values-secret.yaml.template ~/values-secret-rag-llm-gitops.yaml
```

### Provision GPU MachineSet

As a pre-requisite to deploy the application using the validated pattern, GPU nodes should be provisioned along with Node Feature Discovery Operator and NVIDIA GPU operator. To provision GPU Nodes

Following command will take about 5-10 minutes.

```sh
./pattern.sh make create-gpu-machineset
```

Wait till the nodes are provisioned and running.

![Diagram](images/nodes.png)

Alternatiely, follow the [instructions](./GPU_provisioning.md) to manually install GPU nodes, Node Feature Discovery Operator and NVIDIA GPU operator.

### Deploy application

Following commands will take about 15-20 minutes

> **Validated pattern will be deployed**

```sh
./pattern.sh make install
```

### 1: Verify the installation

- Login to the OpenShift web console.
- Navigate to the Workloads --> Pods.
- Select the `rag-llm` project from the drop down.
- Following pods should be up and running.

![Pods](images/rag-llm.png)

Note: If the hf-text-generation-server is not running, make sure you have followed the steps to configure a node with GPU from the [instructions](./GPU_provisioning.md) provided above.

### 2: Launch the application

- Click the `Application box` icon in the header, and select `Retrieval-Augmented-Generation (RAG) LLM Demonstration UI`

![Launch Application](images/launch-application.png)

- It should launch the application

  ![Application](images/application.png)

### 3: Generate the proposal document

- It will use the default provider and model configured as part of the application deployment. The default provider is a Hugging Face model server running in the OpenShift. The model server is deployed with this valdiated pattern and requires a node with GPU.
- Enter any company name
- Enter the product as `RedHat OpenShift`
- Click the `Generate` button, a project proposal should be generated. The project proposal also contains the reference of the RAG content. The project proposal document can be Downloaded in the form of a PDF document.

  ![Routes](images/proposal.png)

### 4: Add an OpenAI provider

You can optionally add additional providers. The application supports the following providers

- Hugging Face Text Generation Inference Server
- OpenAI
- NVIDIA

Click on the `Add Provider` tab to add a new provider. Fill in the details and click `Add Provider` button. The provider should be added in the `Providers` dropdown uder `Chatbot` tab.

![Routes](images/add_provider.png)

### 5: Generate the proposal document using OpenAI provider

Follow the instructions in step 3 to generate the proposal document using the OpenAI provider.

![Routes](images/chatgpt.png)

### 6: Rating the provider

You can provide rating to the model by clicking on the `Rate the model` radio button. The rating will be captured as part of the metrics and can help the company which model to deploy in prodcution.

### 7: Grafana Dashboard

By default, Grafana application is deployed in `llm-monitoring` namespace.To launch the Grafana Dashboard, follow the instructions below:

- Grab the credentials of Grafana Application
  - Navigate to Workloads --> Secrets
  - Click on the grafana-admin-credentials and copy the GF_SECURITY_ADMIN_USER, GF_SECURITY_ADMIN_PASSWORD
- Launch Grafana Dashboard
  - Click the `Application box` icon in the header, and select `Grafana UI for LLM ratings`
 ![Launch Application](images/launch-application.png)
  - Enter the Grafana admin credentials.
  - Ratings are displayed for each model.

![Routes](images/monitoring.png)
