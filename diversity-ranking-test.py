import os
from pathlib import Path

import weaviate
from weaviate.agents.query import QueryAgent
from weaviate.classes.config import Configure, DataType, Property

DATA_DIR = Path(__file__).parent / "data" / "podcast-descriptions"
COLLECTION_NAME = "Podcasts"

# Load all podcast descriptions into a local dictionary
podcast_descriptions = {}
for path in DATA_DIR.glob("*.txt"):
    pod_number = path.stem
    with open(path, encoding="utf-8") as f:
        podcast_descriptions[pod_number] = f.read().strip()

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.environ["WEAVIATE_URL"],
    auth_credentials=weaviate.auth.AuthApiKey(os.environ["WEAVIATE_API_KEY"]),
)

if client.collections.exists(COLLECTION_NAME) == False:
    client.collections.create(
        name=COLLECTION_NAME,
        properties=[
            Property(name="pod_number", data_type=DataType.INT),
            Property(name="description", data_type=DataType.TEXT),
        ],
        vector_config=Configure.Vectors.text2vec_weaviate(),
    )

    podcasts = client.collections.get(COLLECTION_NAME)

    files = sorted(DATA_DIR.glob("*.txt"))
    with podcasts.batch.dynamic() as batch:
        for path in files:
            batch.add_object(
                properties={
                    "pod_number": int(path.stem),
                    "description": path.read_text(encoding="utf-8").strip(),
                }
            )

    failed = podcasts.batch.failed_objects
    print(f"Uploaded {len(files) - len(failed)} / {len(files)} podcasts")
    if failed:
        print(f"Failed: {len(failed)}")
        for f in failed[:5]:
            print(f"  - {f}")

# Connect to QA
system_prompt = """
I want to find podcasts that are similar to the one provided.
"""

qa = QueryAgent(
    client=client, collections=["Podcasts"], system_prompt=system_prompt
)

# --- Example usage: select a podcast to use as query and exclude it from the results ---

def exclude_pod_used_as_query(search_response, selected_pod_number):
    """Return result objects, excluding the podcast used as the query."""
    return [
        obj
        for obj in search_response.search_results.objects
        if str(obj.properties["pod_number"]) != selected_pod_number
    ]

# User can set this pod_number to the one they want to use as the search query
selected_pod_number = "135"  # e.g., "135", change to any available key in podcast_descriptions

query_text = podcast_descriptions[selected_pod_number]

print(f"Results for episode {selected_pod_number} as query WITHOUT diversity ranking:")
search_response = qa.search(query_text, limit=5)
print(type(search_response))
print(len(search_response.search_results.objects))

results = exclude_pod_used_as_query(search_response, selected_pod_number)

for obj in results:
    print(f"Podcast: {obj.properties['pod_number']}")

print(f"\nResults for episode {selected_pod_number} as query WITH diversity ranking:")
search_response = qa.search(query_text, limit=5, diversity_weight=0.8)

print(type(search_response))
print(len(search_response.search_results.objects))
results = exclude_pod_used_as_query(search_response, selected_pod_number)

for obj in results:
    print(f"Podcast: {obj.properties['pod_number']}")

client.close()