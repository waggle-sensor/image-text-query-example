'''This file implements functions that fetch results from weaviate for the query 
entered by user.'''
import HyperParameters as hp
from weaviate.classes.query import MetadataQuery, Move, HybridVector, Rerank
import logging

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
        fusion_type= hp.fusion_alg,
        # max_vector_distance=hp.max_vector_distance,
        auto_limit=hp.autocut_jumps,
        limit=hp.response_limit,
        alpha=hp.query_alpha,
        return_metadata=MetadataQuery(score=True, explain_score=True, certainty=True, distance=True),
        query_properties=["caption"], #Keyword search properties, only search "caption" for keywords
        vector=HybridVector.near_text(
            query=nearText,
            move_away=Move(force=hp.avoid_concepts_force, concepts=hp.concepts_to_avoid), #can this be used as guardrails?
            # distance=hp.max_vector_distance,
            # certainty=hp.near_text_certainty,
        ),
        rerank=Rerank(
            prop="caption", # The property to rerank on
            query=nearText  # If not provided, the original query will be used
    )
    )

    # init
    objects = []
    scores = {}

    # Log the results
    logging.debug("============RESULTS======================")

    # Extract results from QueryReturn object type
    for obj in res.objects:
        #log results
        logging.debug("----------------%s----------------", obj.properties["filename"])
        logging.debug(f"Properties: {obj.properties}")
        logging.debug(f"Score: {obj.metadata.score}")
        logging.debug(f"Explain Score: {obj.metadata.explain_score}")
        
        # Append the relevant object data
        objects.append({
            "filename": obj.properties["filename"],
            "caption": obj.properties["caption"],
            "timestamp": obj.properties["timestamp"],
            "link": obj.properties["link"],
        })

        # Append the score data
        scores[obj.properties['filename']] = {
            "score": obj.metadata.score,
            "explainScore": obj.metadata.explain_score,
            "distance": obj.metadata.distance,
            "certainty": obj.metadata.certainty,
            "rerank_score": obj.metadata.rerank.score
        }

    logging.debug("==============END========================")

    # Return results in the required format
    return {
        "objects": tuple(objects),  # Convert objects to a tuple
        "scores": scores,
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