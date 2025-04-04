import logging
import os
import re
import subprocess

import pytest
from ocp_resources.machine_set import MachineSet
from ocp_resources.node import Node

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
    for node in nodes:
        logger.info(node.instance.metadata.name)
        labels = node.instance.metadata.labels
        logger.info(labels)
        label_str = str(labels)

        odh_label = "'node-role.kubernetes.io/odh-notebook': ''"
        worker_label = "'node-role.kubernetes.io/worker': ''"

        if odh_label in label_str and worker_label in label_str:
            gpu_nodes.append(node)

    # logger.info(node_count)

    if len(gpu_nodes) == 3:
        logger.info("PASS: Found 'worker' and 'odh-notebook' GPU node-role labels")
    else:
        err_msg = "Could not find 'worker' and 'odh-notebook' GPU node-role label"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    """
    Check for the expected number of pods deployed on GPU nodes
    """
    logger.info("Checking pod count on GPU nodes")

    for gpu_node in gpu_nodes:
        name = gpu_node.instance.metadata.name
        field_select = "--field-selector=spec.host=" + name
        pod_count = 0
        expected_count = 20
        failed_nodes = []
        cmd_out = subprocess.run(
            [oc, "get", "pod", "-A", field_select, "--no-headers"], capture_output=True
        )

        if cmd_out.stdout:
            out_decoded = cmd_out.stdout.decode("utf-8")
            logger.info(node.instance.metadata.name + "\n" + out_decoded)
            out_split = out_decoded.splitlines()

            for line in out_split:
                if "Completed" in line:
                    continue
                else:
                    pod_count += 1

            if pod_count < expected_count:
                failed_nodes.append(node.instance.metadata.name)
        else:
            assert False, cmd_out.stderr

    if failed_nodes:
        err_msg = f"Did not find the expected pod count on: {failed_nodes}"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Found the expected pod count for GPU nodes")
