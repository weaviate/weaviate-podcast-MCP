import weaviate

def startup(weaviate_client: weaviate.Client):
    pass

def sync_new_pods():
    pass

def _check_if_pod_collection_exists():
    pass

def _create_pod_collections():
    pass

def _upload_pods():
    pods = []
    for pod in os.listdir("podcast-summaries"):
        with open(f"podcast-summaries/{pod}", "r") as f:
            pod_summary = f.read()
    pods.append({
        "pod_number": pod.split(".")[0],
        "pod_summary": pod_summary
    })

def _sync_new_pods():
    pass