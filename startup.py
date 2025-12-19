import os

import weaviate
from weaviate.classes.config import Property, DataType

def startup(weaviate_client: weaviate.Client):
    if not weaviate_client.collections.exists("WeaviatePodcast"):
        _create_pod_collections(weaviate_client)

def _create_pod_collections(weaviate_client: weaviate.Client):
    return weaviate_client.collections.create(
        "WeaviatePodcast",
        properties=[
            Property(name="pod_number", data_type=DataType.INT),
            Property(name="pod_summary", data_type=DataType.TEXT),
        ],
    )

def _upload_pods(collection: weaviate.Collection):
    pods = []
    for pod_filename in os.listdir("podcast-summaries"):
        with open(f"podcast-summaries/{pod_filename}", "r") as f:
            pod_summary = f.read()
        pods.append({
            "pod_number": pod_filename.split(".")[0],
            "pod_summary": pod_summary
        })
    with collection.batch.fixed_size(batch_size=100) as batch:
        for pod in pods:
            batch.add_object(
                collection=collection,
                properties=pod
            )