import os

import pytest
import requests
from ocp_resources.machine_set import MachineSet
from ocp_resources.node import Node
from ocp_resources.pod import Pod
from ocp_resources.resource import Resource
from ocp_resources.route import Route
from playwright.sync_api import expect, sync_playwright
from validatedpatterns_tests.interop import components, subscription


def _route_url(openshift_dyn_client, namespace, name):
    routes = [
        route
        for route in Route.get(
            dyn_client=openshift_dyn_client, namespace=namespace, name=name
        )
    ]

    assert (
        len(routes) == 1
    ), f"Expected to find the route '{name}' in the namespace '{namespace}'"

    spec = routes[0].instance.spec
    scheme = "https" if getattr(spec, "tls", None) else "http"
    return f"{scheme}://{spec.host}"


@pytest.mark.parametrize(
    "openshift_dyn_client",
    ["VP_HUBCONFIG"],
    indirect=True,
)
def test_subscription_status(openshift_dyn_client):
    expected_subs = {
        "openshift-gitops-operator": ["openshift-gitops-operator"],
        "prometheus": ["llm-monitoring"],
        "grafana-operator": ["llm-monitoring"],
        "nfd": ["openshift-nfd"],
        "gpu-operator-certified": ["nvidia-gpu-operator"],
    }

    subscription.assert_subscription_status(openshift_dyn_client, expected_subs)


@pytest.mark.parametrize(
    "openshift_dyn_client",
    ["VP_HUBCONFIG"],
    indirect=True,
)
def test_site_reachable(openshift_dyn_client):
    components.assert_site_reachable(openshift_dyn_client)


@pytest.mark.parametrize(
    "openshift_dyn_client",
    ["VP_HUBCONFIG"],
    indirect=True,
)
def test_pod_count(openshift_dyn_client):
    projects = {"rag-llm": 4}

    errors = []
    for key in projects.keys():
        pods = [pod for pod in Pod.get(dyn_client=openshift_dyn_client, namespace=key)]
        expected_count = projects[key]
        actual_count = len(pods)

        if actual_count < expected_count:
            errors.append(
                f"Expected the namespace '{key}' to contain at least {expected_count} pods but it actually contains {actual_count} pods"
            )

    assert not errors, "\n".join(errors)


@pytest.mark.parametrize(
    "openshift_dyn_client",
    ["VP_HUBCONFIG"],
    indirect=True,
)
def test_llm_ui_route(openshift_dyn_client):
    # _route_url asserts that exactly one 'llm-ui' route exists in 'rag-llm'.
    url = _route_url(openshift_dyn_client, "rag-llm", "llm-ui")

    response = requests.get(url, verify=False, timeout=60)
    assert (
        response.status_code == 200
    ), f"Expected a 200 from the llm-ui route '{url}' but got {response.status_code}"


@pytest.mark.parametrize(
    "openshift_dyn_client",
    ["VP_HUBCONFIG"],
    indirect=True,
)
def test_vllm_inference_service_route(openshift_dyn_client):
    base_url = _route_url(openshift_dyn_client, "rag-llm", "vllm-inference-service")

    models_url = f"{base_url}/v1/models"
    models_response = requests.get(models_url, verify=False, timeout=60)
    assert (
        models_response.status_code == 200
    ), f"Expected a 200 from '{models_url}' but got {models_response.status_code}"

    models = models_response.json().get("data", [])
    assert models, f"Expected vLLM to be serving at least one model at '{base_url}'"
    model = models[0]["id"]

    completions_url = f"{base_url}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Reply with a short greeting."}],
        "max_tokens": 20,
    }
    response = requests.post(completions_url, json=payload, verify=False, timeout=300)
    assert (
        response.status_code == 200
    ), f"Expected a 200 from '{completions_url}' but got {response.status_code}: {response.text}"

    content = response.json()["choices"][0]["message"]["content"]
    assert (
        content
    ), f"Expected a non-empty completion from the LLM at '{completions_url}'"


@pytest.mark.parametrize(
    "openshift_dyn_client",
    ["VP_HUBCONFIG"],
    indirect=True,
)
def test_nodefeaturediscovery(openshift_dyn_client):
    name = "nfd-instance"
    namespace = "openshift-nfd"

    class NodeFeatureDiscovery(Resource):
        api_group = "nfd.openshift.io"
        api_version = "v1"
        kind = "NodeFeatureDiscovery"

    nfds = [
        nfd
        for nfd in NodeFeatureDiscovery.get(
            dyn_client=openshift_dyn_client, namespace=namespace, name=name
        )
    ]

    assert (
        len(nfds) == 1
    ), f"Expected to find the NodeFeatureDiscovery '{name}' in the namespace '{namespace}'"


@pytest.mark.parametrize(
    "openshift_dyn_client",
    ["VP_HUBCONFIG"],
    indirect=True,
)
def test_gpu_clusterpolicy(openshift_dyn_client):
    name = "rag-llm-gpu-cluster-policy"
    expected_tolerations = [
        {"effect": "NoSchedule", "key": "odh-notebook", "value": "true"}
    ]

    class ClusterPolicy(Resource):
        api_group = "nvidia.com"
        api_version = "v1"
        kind = "ClusterPolicy"

    policies = [
        policy
        for policy in ClusterPolicy.get(dyn_client=openshift_dyn_client, name=name)
    ]

    assert len(policies) == 1, f"Expected to find the ClusterPolicy '{name}'"

    actual_tolerations = [
        item.to_dict() for item in policies[0].instance.spec.daemonsets.tolerations
    ]

    assert (
        actual_tolerations == expected_tolerations
    ), f"Expected the ClusterPolicy '{name}' to contain the tolerations '{expected_tolerations}' but it actually contains '{actual_tolerations}'"


@pytest.mark.parametrize(
    "openshift_dyn_client",
    ["VP_HUBCONFIG"],
    indirect=True,
)
def test_gpu_machineset(openshift_dyn_client):
    namespace = "openshift-machine-api"
    machinesets = [
        ms
        for ms in MachineSet.get(dyn_client=openshift_dyn_client, namespace=namespace)
    ]

    gpu_machinesets = [ms for ms in machinesets if "-gpu-" in ms.instance.metadata.name]
    assert (
        len(gpu_machinesets) == 1
    ), f"Expected to find a GPU MachineSet in the namespace '{namespace}'"

    gpu_machineset = gpu_machinesets[0]
    gpu_machineset_name = gpu_machineset.instance.metadata.name

    actual_taints = [
        item.to_dict() for item in gpu_machineset.instance.spec.template.spec.taints
    ]
    expected_taints = [{"effect": "NoSchedule", "key": "odh-notebook", "value": "true"}]
    assert (
        actual_taints == expected_taints
    ), f"Expected GPU MachineSet '{gpu_machineset_name}' to contain the taints '{expected_taints}' but it actually contains '{actual_taints}'"

    actual_labels = [
        item for item in gpu_machineset.instance.spec.template.spec.metadata.labels
    ]
    expected_labels = [("node-role.kubernetes.io/odh-notebook", "")]
    assert (
        actual_labels == expected_labels
    ), f"Expected GPU MachineSet '{gpu_machineset_name}' to contain the labels '{expected_labels}' but it actually contains '{actual_labels}'"


@pytest.mark.parametrize(
    "openshift_dyn_client",
    ["VP_HUBCONFIG"],
    indirect=True,
)
def test_gpu_node_role_labels_pods(openshift_dyn_client):
    def is_gpu_node(node: Node) -> bool:
        node_labels = [label for label in node.instance.metadata.labels]
        odh_label = ("node-role.kubernetes.io/odh-notebook", "")
        worker_label = ("node-role.kubernetes.io/worker", "")

        return odh_label in node_labels and worker_label in node_labels

    gpu_nodes = [
        node for node in Node.get(dyn_client=openshift_dyn_client) if is_gpu_node(node)
    ]

    num_gpu_nodes = len(gpu_nodes)
    assert (
        num_gpu_nodes == 1
    ), f"Expected to find 1 GPU Node but actually found '{num_gpu_nodes}'"

    namespace = "nvidia-gpu-operator"
    gpu_node_name = gpu_nodes[0].instance.metadata.name
    nvidia_pods = [
        pod
        for pod in Pod.get(dyn_client=openshift_dyn_client, namespace=namespace)
        if pod.instance.spec.nodeName == gpu_node_name
        and "nvidia" in pod.instance.metadata.name
    ]

    actual_count = len(nvidia_pods)
    expected_count = 8
    assert (
        actual_count == expected_count
    ), f"Expected to find {expected_count} Nvidia pods on Node '{gpu_node_name}' but actually found {actual_count}"


@pytest.mark.parametrize(
    "openshift_dyn_client",
    ["VP_HUBCONFIG"],
    indirect=True,
)
def test_ragllm_ui(openshift_dyn_client):
    rag_ui_url = _route_url(openshift_dyn_client, "rag-llm", "llm-ui")
    grafana_url = _route_url(
        openshift_dyn_client, "llm-monitoring", "ai-llm-grafana-route"
    )

    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".results")
    os.makedirs(results_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        context.set_default_timeout(120_000)
        page = context.new_page()
        try:
            # Generate a proposal in the RAG-LLM demo UI
            page.goto(rag_ui_url)
            page.get_by_role("textbox", name="Customer Enter the customer").fill(
                "validated-patterns-qe"
            )
            page.get_by_role("textbox", name="Product Enter the Red Hat").fill(
                "RedHat OpenShift AI"
            )
            page.get_by_role("button", name="Generate").click()

            # Wait for generation to complete, then submit a rating
            rating = page.get_by_role("radio", name="3")
            expect(rating).to_be_visible(timeout=180_000)
            rating.check()

            # Add a provider on the Configuration tab
            page.get_by_role("tab", name="Configuration").click()
            page.get_by_role("button", name="Add Provider").click()
            page.get_by_role("listbox", name="Providers").click()
            page.get_by_role("option", name="OpenAI").click()
            page.get_by_role("textbox", name="Model Enter the model name").fill(
                "gpt-4o-mini"
            )
            page.get_by_role("textbox", name="URL Enter the URL").fill(
                "https://api.openai.com/v1/chat/completions"
            )
            page.get_by_test_id("password").fill("12121212")
            page.get_by_role("button", name="Add", exact=True).click()

            toast_close = page.get_by_test_id("toast-close")
            expect(toast_close).to_be_visible()
            toast_close.click()
            page.screenshot(path=os.path.join(results_dir, "ragllm-add-provider.png"))

            # Check the Grafana LLM ratings dashboard
            gpage = context.new_page()
            gpage.goto(grafana_url)
            gpage.get_by_role("link", name="Dashboards").click()
            gpage.get_by_role("link", name="llm-monitoring").click()

            feedback = gpage.get_by_role("link", name="MODEL FEEDBACK/RATING")
            expect(feedback).to_be_visible()
            feedback.click()
            gpage.screenshot(
                path=os.path.join(results_dir, "ragllm-grafana-dashboard.png")
            )
        finally:
            context.close()
            browser.close()
