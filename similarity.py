import numpy as np

from image_engine import ImageEngine
from config import SIMILARITY_THRESHOLD


class SimilarityEngine:

    def __init__(self, database, image_engine):

        self.database = database
        self.image_engine = image_engine


    def search_similar_items(
        self,
        query_image,
        top_k=5
    ):

        # Extract features from uploaded image
        query_embedding = (
            self.image_engine.extract_features(
                query_image
            )
        )

        # Retrieve registered found objects
        items = self.database.get_items(
            item_type="found"
        )

        results = []

        for item in items:

            try:

                stored_embedding = (
                    self.image_engine.extract_features(
                        item["image_path"]
                    )
                )

                # Calculate image similarity
                similarity = (
                    self.image_engine.calculate_similarity(
                        query_embedding,
                        stored_embedding
                    )
                )

                results.append({

                    "item": item,

                    "similarity": similarity,

                    "percentage": round(
                        max(0.0, similarity) * 100,
                        2
                    )

                })

            except Exception as error:

                print(
                    f"Could not process item "
                    f"{item['id']}: {error}"
                )

        # Sort by similarity score
        results.sort(
            key=lambda result: result["similarity"],
            reverse=True
        )

        # Return top matching results
        return results[:top_k]


    def get_confirmed_matches(
        self,
        query_image,
        top_k=5
    ):

        results = self.search_similar_items(
            query_image,
            top_k
        )

        return [
            result
            for result in results
            if result["similarity"] >= SIMILARITY_THRESHOLD
        ]
