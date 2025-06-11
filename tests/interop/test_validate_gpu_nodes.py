import logging
import os
import re

import pytest
from ocp_resources.machine_set import MachineSet
from ocp_resources.node import Node
from ocp_resources.pod import Pod

from . import __loggername__

logger = logging.getLogger(__loggername__)

oc = os.environ["HOME"] + "/oc_client/oc"


@pytest.mark.validate_gpu_machineset
def test_validate_gpu_nodes(openshift_dyn_client):
    """
    Check for the existence of the GPU machineset
    """
    logger.info("Checking GPU machineset")
    machinesets = MachineSet.get(
        dyn_client=openshift_dyn_client, namespace="openshift-machine-api"
    )

    found = False
    for machineset in machinesets:
        logger.info(machineset.instance.metadata.name)
        if re.search("gpu", machineset.instance.metadata.name):
            gpu_machineset = machineset
            found = True
            break

    err_msg = "GPU machineset not found"
    if found:
        logger.info(
            f"PASS: Found GPU machineset: {gpu_machineset.instance.metadata.name}"
        )
    else:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    """
    Check for the existence of the GPU machineset taint
    """
    logger.info("Checking GPU machineset taint")

    err_msg = "No taints found for GPU machineset"
    try:
        logger.info(gpu_machineset.instance.spec.template.spec.taints)
    except AttributeError:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    if gpu_machineset.instance.spec.template.spec.taints == "None":
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    logger.info(
        f"PASS: Found GPU machineset taint: {gpu_machineset.instance.spec.template.spec.taints}"
    )

    """
    Check for the existence of the GPU machineset label
    """
    logger.info("Checking GPU machineset label")

    err_msg = "No label found for GPU machineset"
    try:
        logger.info(gpu_machineset.instance.spec.template.spec.metadata.labels)
    except AttributeError:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    labels = str(gpu_machineset.instance.spec.template.spec.metadata.labels)
    if labels == "None":
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    logger.info(f"PASS: Found GPU machineset labels: {labels}")

    """
    Check for the existence of the GPU machineset instance type
    """
    logger.info("Checking GPU machineset instance type")

    err_msg = "No instanceType found for GPU machineset"
    try:
        logger.info(
            machineset.instance.spec.template.spec.providerSpec.value.instanceType
        )
    except AttributeError:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    instance_type = str(
        machineset.instance.spec.template.spec.providerSpec.value.instanceType
    )
    if instance_type == "None":
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    logger.info(f"PASS: Found GPU machineset instance type: {instance_type}")


@pytest.mark.validate_gpu_node_role_labels_pods
def test_validate_gpu_node_role_labels_pods(openshift_dyn_client):
    """
    Check for the expected node-role labels for GPU nodes
    """
    logger.info("Checking GPU node-role labels")

    nodes = Node.get(dyn_client=openshift_dyn_client)
    gpu_nodes = []
    expected_count = 1
    for node in nodes:
        logger.info(node.instance.metadata.name)
        labels = node.instance.metadata.labels
        logger.info(labels)
        label_str = str(labels)

        odh_label = "'node-role.kubernetes.io/odh-notebook': ''"
        worker_label = "'node-role.kubernetes.io/worker': ''"

        if odh_label in label_str and worker_label in label_str:
            gpu_nodes.append(node)

    if len(gpu_nodes) == int(expected_count):
        logger.info("PASS: Found 'worker' and 'odh-notebook' GPU node-role labels")
    else:
        err_msg = "Could not find 'worker' and 'odh-notebook' GPU node-role label"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    """
    Check for the expected number of pods deployed on GPU nodes
    """
    logger.info("Checking pod count on GPU nodes")

    # We are assuming one GPU node
    gpu_node = gpu_nodes[0].instance.metadata.name
    nvidia_pods = []
    expected_count = 8
    project = "nvidia-gpu-operator"
    pods = Pod.get(dyn_client=openshift_dyn_client, namespace=project)

    for pod in pods:
        if "nvidia" in pod.instance.metadata.name:
            logger.info(f"nvidia pod: {pod.instance.metadata.name}")
            if gpu_node in pod.instance.spec.nodeName:
                logger.info(f"nvidia pod node name: {pod.instance.spec.nodeName}")
                nvidia_pods.append(pod.instance.metadata.name)

    if len(nvidia_pods) == int(expected_count):
        logger.info("PASS: Found the expected nvidia pod count for GPU nodes")
    else:
        err_msg = "Did not find the expected nvidia pod count for GPU nodes"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
