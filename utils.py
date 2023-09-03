import os
import openai
import requests
import json
from datetime import datetime 

openai.api_key = "YOUR_OPEN_AI_KEY"
api_key_pinecone = "YOUR_PINE_KEY"
pinecone_environment = "PINE_CONE_ENV"
# pinecone_endpoint = st.secrets["PINECONE_ENDPOINT"]

def get_embeddings_openai(text):
    try:
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        response = response['data']
        return [x["embedding"] for x in response]
    except Exception as e:
        print(f"Error in get_embeddings_openai: {e}")
        raise

def semantic_search(query, index, **kwargs):
    try:
        xq = get_embeddings_openai(query)
        # print("xr----------------xr\n",xq[0])
        

        xr = index.query(vector=xq[0], top_k=kwargs.get('top_k', 2), include_metadata=kwargs.get('include_metadata', True))
       
        if xr.error:
            print(f"Invalid response: {xr}")
            raise Exception(f"Query failed: {xr.error}")

        titles = [r["metadata"]["title"] for r in xr["matches"]]
        transcripts = [r["metadata"]["transcript"] for r in xr["matches"]]
        return list(zip(titles, transcripts))

    except Exception as e:
        print(f"Error in semantic_search: {e}")
        raise

def upload_pinecone(query, index):
    try:
        # xq = get_embeddings_openai(query)
        my_id = index.describe_index_stats()['total_vector_count']
        chunkInfo = (str(my_id),
                 get_embeddings_openai(query),
                 {'title':'', 'transcript':query})
        index.upsert(vectors=[chunkInfo])
        # index.upsert(ids=my_id, vectors=xq[0], include_string=bot_response)
        
    except Exception as e:
        print(f"Error in upload_pinecone: {e}")
        raise