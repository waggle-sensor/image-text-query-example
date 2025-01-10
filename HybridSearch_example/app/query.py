'''This file implements functions that fetch results from weaviate for the query 
entered by user. There are two functions, testImage and testText for image query and text query
respectively.'''
from HyperParameters import response_limit, query_alpha, max_vector_distance
from weaviate.classes.query import MetadataQuery

def testText(nearText,client):
    # I am fetching top "response_limit" results for the user
    # You can also analyse the result in a better way by taking a look at res.
    # Try printing res in the terminal and see what all contents it has.
    # used this for hybrid search params https://weaviate.io/developers/weaviate/search/hybrid

    #get collection
    collection = client.collections.get("HybridSearchExample")

    # Perform the hybrid search
    res = collection.query.hybrid(
        query=nearText,  # The model provider integration will automatically vectorize the query
        # max_vector_distance=max_vector_distance,
        limit=response_limit,
        alpha=query_alpha,
        return_metadata=MetadataQuery(score=True, explain_score=True),
        query_properties=["caption"], #Keyword search properties, only search "caption" for keywords
    )

    # Extract results
    results = res["data"]["Get"]["HybridSearchExample"]
    objects = []
    scores = []

    for item in results:
        # Append the relevant object data
        objects.append({
            "filename": item.get("filename", ""),
            "caption": item.get("caption", ""),
            "timestamp": item.get("timestamp", ""),
            "link": item.get("link", ""),
        })

        # Append the score data
        scores.append({
            "score": item["_additional"]["score"],
            "explainScore": item["_additional"]["explainScore"],
        })

    # Return results in the required format
    return {
        "objects": tuple(objects),  # Convert objects to a tuple
        "scores": tuple(scores),    # Convert scores to a tuple
    }

# TODO: how will this be implemented in a hybrid search approach? create a caption for the image entered by the user?
# def testImage(nearImage,client):
#     # I am fetching top 3 results for the user, we can change this by making small 
#     # altercations in this function and in upload.html file
#     # # adding a threshold: https://weaviate.io/developers/weaviate/search/similarity#set-a-similarity-threshold
#     imres = client.query.get("ClipExample", ["text", "_additional {certainty} "]).with_near_image(nearImage).do()
#     return {
#         "objects": ((imres['data']['Get']['ClipExample'][0]['text']),(imres['data']['Get']['ClipExample'][1]['text']),(imres['data']['Get']['ClipExample'][2]['text'])),
#         "scores": (imres['data']['Get']['ClipExample'][0]['_additional'],imres['data']['Get']['ClipExample'][1]['_additional'],imres['data']['Get']['ClipExample'][2]['_additional'])
#     }