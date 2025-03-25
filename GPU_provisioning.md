# GPU provisioning

Use the instructions to add nodes with GPU in OpenShift cluster running in AWS cloud. Nodes with GPU will be tainted to allow only pods that required GPU to be scheduled to these nodes

More details can be found in following documents [Openshift AI](https://ai-on-openshift.io/odh-rhoai/nvidia-gpus/), [NVIDIA on OpenShift](https://docs.nvidia.com/datacenter/cloud-native/openshift/latest/index.html)

## Add machineset

The easiest way is to use existing machineset manifest and update certain elements. Use worker machineset manifest and modify some of the entries (naming conventions provided as reference only, use own if required.), keep other entries as is:

```yaml
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  name: <clustername>-gpu-<AWSregion>
..............
spec:
  replicas: 1
  selector:
    matchLabels:
      ................
      machine.openshift.io/cluster-api-machineset: <clustername>-gpu-<AWSregion>
  template:
    metadata:
      labels:
        ........
        machine.openshift.io/cluster-api-machineset: <clustername>-gpu-<AWSregion>
    spec:
      ...................
      metadata:
        labels:
          node-role.kubernetes.io/odh-notebook: '' <--- Put your label if needed
      providerSpec:
        value:
          ........................
          instanceType: g5.2xlarge <---- Change vm type if needed
      .............
      taints:
        - effect: NoSchedule
          key: odh-notebook  <--- Use own taint name or skip all together
          value: 'true'
```

Use `kubectl` or `oc` command line to create new machineset `oc apply -f gpu_machineset.yaml`

Depending on type of EC2 instance creation of the new machines make take some
time. Please note that all nodes with GPU will have
labels(`node-role.kubernetes.io/odh-notebook` in our case) and taints
(`odh-notebook`) that we have specified in machineset applied automatically

## Install Node Feature Operator

From OperatorHub install `Node Feature Discovery Operator` , accepting
defaults. Once Operator has been installed, create
`NodeFeatureDiscovery`instance. Use default entries unless you something
specific is needed. Node Feature Discovery Operator will add labels to nodes
based on available hardware resources.

![Diagram](images/node-feature-discovery.png)

## Install NVIDIA GPU Operator

NVIDIA GPU Operator will provision daemonsets with drivers for the GPU to be used by workload running on these nodes . Detailed instructions are available in NVIDIA Documentation [NVIDIA on OpenShift](https://docs.nvidia.com/datacenter/cloud-native/openshift/latest/index.html) .  Following simplified steps for specific setup :

- Install NVIDIA GPU Operator from OperatorHub
- Once operator is ready create `ClusterPolicy` custom resource. Unless required you can use default settings with adding `tolerations` if machineset in first section has been created with taint. Failing to add `tolerations` will prevent drivers to be installed on GPU enabled node :

```yaml
apiVersion: nvidia.com/v1
kind: ClusterPolicy
metadata:
  name: gpu-cluster-policy
spec:
  vgpuDeviceManager:
    enabled: true
  migManager:
    enabled: true
  operator:
    defaultRuntime: crio
    initContainer: {}
    runtimeClass: nvidia
    use_ocp_driver_toolkit: true
  dcgm:
    enabled: true
  gfd:
    enabled: true
  dcgmExporter:
    config:
      name: ''
    enabled: true
    serviceMonitor:
      enabled: true
  driver:
    certConfig:
      name: ''
    enabled: true
    kernelModuleConfig:
      name: ''
    licensingConfig:
      configMapName: ''
      nlsEnabled: false
    repoConfig:
      configMapName: ''
    upgradePolicy:
      autoUpgrade: true
      drain:
        deleteEmptyDir: false
        enable: false
        force: false
        timeoutSeconds: 300
      maxParallelUpgrades: 1
      maxUnavailable: 25%
      podDeletion:
        deleteEmptyDir: false
        force: false
        timeoutSeconds: 300
      waitForCompletion:
        timeoutSeconds: 0
    virtualTopology:
      config: ''
  devicePlugin:
    config:
      default: ''
      name: ''
    enabled: true
  mig:
    strategy: single
  sandboxDevicePlugin:
    enabled: true
  validator:
    plugin:
      env:
        - name: WITH_WORKLOAD
          value: 'false'
  nodeStatusExporter:
    enabled: true
  daemonsets:
    rollingUpdate:
      maxUnavailable: '1'
    tolerations:
      - effect: NoSchedule
        key: odh-notebook
        value: 'true'
    updateStrategy: RollingUpdate
  sandboxWorkloads:
    defaultWorkload: container
    enabled: false
  gds:
    enabled: false
  vgpuManager:
    enabled: false
  vfioManager:
    enabled: true
  toolkit:
    enabled: true
    installDir: /usr/local/nvidia
```

Provisioning NVIDIA daemonsets and compiling drivers may take some time (5-10 minutes)
