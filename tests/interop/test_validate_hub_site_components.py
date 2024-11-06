import logging
import os
import subprocess

import pytest
from ocp_resources.pod import Pod
from ocp_resources.route import Route
from openshift.dynamic.exceptions import NotFoundError
from ocp_resources.storage_class import StorageClass
from validatedpatterns_tests.interop import application, components

from . import __loggername__

logger = logging.getLogger(__loggername__)

oc = os.environ["HOME"] + "/oc_client/oc"


@pytest.mark.test_validate_hub_site_components
def test_validate_hub_site_components(openshift_dyn_client):
    logger.info("Checking Openshift version on hub site")
    version_out = components.dump_openshift_version()
    logger.info(f"Openshift version:\n{version_out}")

    logger.info("Dump PVC and storageclass info")
    pvcs_out = components.dump_pvc()
    logger.info(f"PVCs:\n{pvcs_out}")

    for sc in StorageClass.get(dyn_client=openshift_dyn_client):
        logger.info(sc.instance)


@pytest.mark.validate_hub_site_reachable
def test_validate_hub_site_reachable(kube_config, openshift_dyn_client):
    logger.info("Check if hub site API end point is reachable")
    err_msg = components.validate_site_reachable(kube_config, openshift_dyn_client)
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Hub site is reachable")


@pytest.mark.check_pod_status_hub
def test_check_pod_status(openshift_dyn_client):
    logger.info("Checking pod status")
    projects = [
        "nvidia-gpu-operator",
        "rag-llm"
    ]
    err_msg = components.check_pod_status(openshift_dyn_client, projects)
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Pod status check succeeded.")


@pytest.mark.check_pod_count_hub
def test_check_pod_count_hub(openshift_dyn_client):
    logger.info("Checking pod count")
    projects = {
        "rag-llm": 4
    }

    failed = []
    for key in projects.keys():
        logger.info(f"Checking project: {key}")
        pods = Pod.get(dyn_client=openshift_dyn_client, namespace=key)

        count = 0
        for pod in pods:
            logger.info(pod.instance.metadata.name)
            count += 1

        logger.info(f"Found {count} pods")
        if count < projects[key]: failed.append(key)

    if len(failed) > 0:
        err_msg = f"Failed to find the expected pod count for: {failed}"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Found the expected pod count")


@pytest.mark.validate_argocd_reachable_hub_site
def test_validate_argocd_reachable_hub_site(openshift_dyn_client):
    logger.info("Check if argocd route/url on hub site is reachable")
    err_msg = components.validate_argocd_reachable(openshift_dyn_client)
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Argocd is reachable")


@pytest.mark.validate_llm_ui_route
def test_validate_llm_ui_route(openshift_dyn_client):
    namespace = "rag-llm"
    logger.info("Check for the existence of the llm-ui route")
    try:
        for route in Route.get(
            dyn_client=openshift_dyn_client,
            namespace=namespace,
            name="llm-ui",
        ):
            logger.info(route.instance.spec.host)
    except NotFoundError:
        err_msg = "llm-ui url/route is missing in rag-llm namespace"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    logger.info("PASS: Found llm-ui route")


@pytest.mark.validate_nodefeaturediscovery
def test_validate_nodefeaturediscovery():
    namespace = "openshift-nfd"
    name = "nfd-instance"
    logger.info("Check for nodefeaturediscovery instance")

    cmd_out = subprocess.run(
        [oc, "get", "NodeFeatureDiscovery", "-n", namespace, name, "--no-headers"], capture_output=True
    )
    if cmd_out.stdout:
        logger.info(cmd_out.stdout.decode("utf-8"))
        logger.info("PASS: Found nodefeaturediscovery instance")
    else:
        assert False, cmd_out.stderr


@pytest.mark.validate_gpu_clusterpolicy
def test_validate_gpu_clusterpolicy():
    name = "rag-llm-gpu-cluster-policy"
    tolerations = '"tolerations":[{"effect":"NoSchedule","key":"odh-notebook","value":"true"}]'
    logger.info("Check for GPU clusterpolicy")

    cmd_out = subprocess.run(
        [oc, "get", "ClusterPolicy", "-o", "yaml", name], capture_output=True
    )
    if cmd_out.stdout:
        logger.info(cmd_out.stdout.decode("utf-8"))
        
        if tolerations in cmd_out.stdout.decode("utf-8"):
            logger.info("PASS: Found GPU clusterpolicy and tolerations")
        else:
            err_msg =f"FAIL: Expected tolerations not found"
            logger.error(f"FAIL: {err_msg}")
            assert False, err_msg
    else:
        assert False, cmd_out.stderr


@pytest.mark.validate_argocd_applications_health_hub_site
def test_validate_argocd_applications_health_hub_site(openshift_dyn_client):
    logger.info("Get all applications deployed by argocd on hub site")
    projects = ["openshift-gitops", "rag-llm-gitops-hub"]
    unhealthy_apps = application.get_argocd_application_status(
        openshift_dyn_client, projects
    )
    if unhealthy_apps:
        err_msg = "Some or all applications deployed on hub site are unhealthy"
        logger.error(f"FAIL: {err_msg}:\n{unhealthy_apps}")
        assert False, err_msg
    else:
        logger.info("PASS: All applications deployed on hub site are healthy.")
