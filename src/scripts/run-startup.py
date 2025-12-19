import os

import weaviate

from startup import startup

weaviate_client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_URL"),
    auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
)
try:
    startup(weaviate_client)
    print("Startup completed successfully!")
finally:
    weaviate_client.close()

