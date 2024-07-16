# Test Cases for E2E Demo.

- [Provisioning of GPU Node](https://github.com/validatedpatterns-sandbox/rag-llm-gitops/blob/main/GPU_provisioning.md)

  - MachineSet is created.
    - Name of the machine set <clustername>-gpu-<AWSregion>. This should not be a hard requirement though. 
    - Machine set has taint section
      ```yaml
      taints:
        - effect: NoSchedule
          key: odh-notebook  <--- Use own taint name or skip all together
          value: 'true'
      ```

    - MachineSet has a label
      ```yaml
       metadata:
         labels:
           node-role.kubernetes.io/odh-notebook: '' <--- Put your label if needed
      ```

    - MachineSet instance type
      ```yaml
       providerSpec:
         value:
         ........................
         instanceType: g5.2xlarge <---- Change vm type if needed
      ```

    - The nodes are provisioned with the proper label. The number of pods running should be greater than 20.
      ![labeled nodes](https://validatedpatterns.io/images/rag-llm-gitops/ragllm-label-nodes.png)

    - NVIDIA pods should be running on the nodes. Check the pods running on the GPU nodes.
      ![nvidia pods](https://validatedpatterns.io/images/rag-llm-gitops/ragllm-pattern-running-pods.png)

  - Verify Node Feature Discovery Operator is installed:
    - Select Installed Operators from the left Navigation Bar and under Projects, select All Projects. Node Discover Feature Operator should be installed
      ![nfd operator](https://validatedpatterns.io/images/rag-llm-gitops/ragllm-nfd-operator.png)

    - Click on the Node Feature Discovery Operator. Under NodeFeatureDiscovery an instance should be created. Status should be Available.
      ![nfd instance](https://validatedpatterns.io/images/rag-llm-gitops/ragllm-nfd-instance.png)


  - Verify NVIDIA GPU Operator is installed.
    - NVIDIA GPU Operator is installed
      
      ![nvidia operator](https://validatedpatterns.io/images/rag-llm-gitops/ragllm-nvidia-operator.png)

    - Click on the NVIDIA GPU Operator and click on ClusterPolicy. A gpu-cluster-policy should exist
      ![nvidia clusterpolicies](https://validatedpatterns.io/images/rag-llm-gitops/ragllm-nvidia-clusterpolicies.png)    

    - Click on the gpu-cluster-policy and click on the YAML tab. The YAML should contain the tolerations
      ```yaml
       tolerations:
         - effect: NoSchedule
           key: odh-notebook
           value: 'true'
      ```

- Application provisioned correctly.
  - Click on the rag-llm namespace
  
    - By Default, EDB Operator will be deployed, which will deploy PGVECTOR vector database, 6 pods should be running
      ![ragllm pgvector pods](https://validatedpatterns.io/images/rag-llm-gitops/rag-llm-pgvector.png)

    - If the global.db.type is set to REDIS in the values-global.yaml, four pods should be running
      ![ragllm pods](https://validatedpatterns.io/images/rag-llm-gitops/rag-llm.png)
  
    - Click on Networking → Routes from the left Navigation panel. An llm-ui route should exist
      ![llm-ui route](https://validatedpatterns.io/images/rag-llm-gitops/ragllm-application_route.png)

    - Click on the link under Location column and it should launch the application
      ![llm-ui application](https://validatedpatterns.io/images/rag-llm-gitops/ragllm-model-application.png)

    - Enter customer name as ‘IBM’ and for product enter ‘RedHat OpenShift’ and click Generate. A project proposal should be generated
      ![llm-ui project](https://validatedpatterns.io/images/rag-llm-gitops/ragllm-application-running.png)

    - Click on Ratings to rate the model.

- Verify Grafana and Prometheus are installed correctly.
  - By default, Grafana application is deployed in llm-monitoring namespace.To launch the Grafana Dashboard, follow the instructions below:
    - Grab the credentials of Grafana Application
      - Navigate to Workloads --> Secrets
      - Click on the grafana-admin-credentials and copy the `GF_SECURITY_ADMIN_USER`, `GF_SECURITY_ADMIN_PASSWORD`
    - Launch Grafana Dashboard
      - Navigate to Networking --> Routes in the llm-monitoring namespace.
      - Click on the Location link for grafana-route.
      - Enter the Grafana admin credentials.
      - Ratings are displayed for each model
    - Grafana Dashboard is displayed
      
      ![llm-ui grafana](https://validatedpatterns.io/images/rag-llm-gitops/ragllm-grafana.png)



	

