import base64

from redis.commands.search.query import Query
from ulid import ULID
from app.models import Faq, FaqId, FaqWithScore


class FaqService:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def create(self, question: str, answer: str, embedding: str) -> Faq:
        # Generate a new ULID for the item
        ulid = str(ULID())

        # The key for the item in Redis
        key = f"faq:{ulid}"  # Changed prefix to match index

        # Add the item to Redis
        await self.redis.hset(
            key,
            mapping={
                "ulid": ulid,
                "question": question,
                "answer": answer,
                "embedding": base64.b64decode(embedding),
            },
        )

        # Return the newly created item
        return Faq(
            ulid=ulid,
            question=question,
            answer=answer,
            embedding=embedding,
        )

    def read(self, ulid: str) -> Faq:
        # The key for the item in Redis
        key = f"item:{ulid}"

        # Get the item's fields from Redis
        item = self.redis.hgetall(key)

        # If the item doesn't exist, return None
        if not item:
            return None

        # Decode the fields and return the item
        return Faq(
            ulid=item[b"ulid"].decode("utf-8"),
            question=item[b"question"].decode("utf-8"),
            answer=item[b"answer"].decode("utf-8"),
            embedding=base64.b64encode(item[b"embedding"]).decode("utf-8"),
        )

    def update(
        self, ulid: str, question: str, answer: str, embedding: str
    ) -> Faq:
        # The key for the item in Redis
        key = f"faq:{ulid}"

        # Check if the item exists
        if self.redis.exists(key) > 0:
            return None

        # Update the item's fields in Redis
        self.redis.hset(
            key,
            mapping={
                "ulid": ulid,
                "question": question,
                "answer": answer,
                "embedding": base64.b64decode(embedding),
            },
        )

        # Return the updated item
        return Faq(
            ulid=ulid,
            question=question,
            answer=answer,
            embedding=embedding,
        )

    def delete(self, ulid: str) -> FaqId:
        # The key for the item in Redis
        key = f"item:{ulid}"

        # Remove the item from Redis, returning the number of deleted keys
        count = self.redis.unlink(key)

        # If the item was deleted, return its ID, otherwise return None
        return FaqId(ulid=ulid) if count > 0 else None

    def search(self, embedding: str) -> list[FaqWithScore]:
        # Create a query to search for items based on the embedding
        query = Query("(*)=>[KNN 4 @embedding $blob as score]")
        query.sort_by("score")
        query.return_fields(
            "ulid", "question", "answer", "embedding", "score"
        )
        query.paging(0, 4)
        query.dialect(3)

        # Decode the base64-encoded embedding and set it as a parameter
        bytes = base64.b64decode(embedding)
        query_params = {"blob": bytes}

        # Execute the search query
        response = self.redis.ft("item:index").search(query, query_params)
        results = response[b"results"]

        # A place to store the found items
        found_items = []

        # Iterate through the results and extract the relevant fields
        # and convert them to the ItemWithScore model
        for result in results:
            # get the attributes from the result
            attributes = result[b"extra_attributes"]

            # get the desired attributes
            ulid = attributes[b"ulid"].decode("utf-8")
            question = attributes[b"question"].decode("utf-8")
            answer = attributes[b"answer"].decode("utf-8")
            embedding = attributes[b"embedding"]
            score = attributes[b"score"]

            # add the found item to the list
            found_items.append(
                FaqWithScore(
                    ulid=ulid,
                    question=question,
                    answer=answer,
                    embedding=base64.b64encode(embedding).decode("utf-8"),
                    score=score,
                )
            )

        # return the found items
        return found_items
