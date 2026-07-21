import base64

from redis.commands.search.query import Query
from ulid import ULID
from app.models import Faq, FaqId, FaqWithScore


class FaqService:
    def __init__(self, redis_client, embedding_service):
        self.redis = redis_client
        self.embedding_service = embedding_service

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

    async def read(self, ulid: str) -> Faq:
        # The key for the item in Redis
        key = f"faq:{ulid}"

        # Get the item's fields from Redis
        item = await self.redis.hgetall(key)

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

    async def update(
        self, ulid: str, question: str, answer: str, embedding: str
    ) -> Faq:
        # The key for the item in Redis
        key = f"faq:{ulid}"

        # Check if the item exists
        if await self.redis.exists(key) == 0:
            return None

        # Update the item's fields in Redis
        await self.redis.hset(
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

    async def delete(self, ulid: str) -> FaqId:
        # The key for the item in Redis
        key = f"faq:{ulid}"

        # Remove the item from Redis, returning the number of deleted keys
        count = await self.redis.unlink(key)

        # If the item was deleted, return its ID, otherwise return None
        return FaqId(ulid=ulid) if count > 0 else None

    async def search(self, embedding: str) -> list[FaqWithScore]:
        # Create a query to search for items based on the embedding
        query = Query("(*)=>[KNN 4 @embedding $blob as score]")
        query.sort_by("score")
        query.return_fields(
            "ulid", "question", "answer", "embedding", "score"
        )
        query.paging(0, 4)
        query.dialect(3)

        # Decode the base64-encoded embedding and set it as a parameter
        embedding_bytes = base64.b64decode(embedding)
        query_params = {"blob": embedding_bytes}

        # Execute the search query
        response = await self.redis.ft("faq:index").search(query, query_params)
        
        # A place to store the found items
        found_items = []

        # Handle dictionary response format from Redis (keys are in bytes)
        if isinstance(response, dict) and b'results' in response:
            results = response[b'results']
            
            for result in results:
                try:
                    # Extract document ID and attributes - Redis returns bytes keys
                    doc_id = result[b'id'].decode('utf-8') if b'id' in result else ''
                    attributes = result[b'extra_attributes'] if b'extra_attributes' in result else {}
                    
                    # Get the attributes (these are also bytes keys) and decode them
                    ulid_bytes = attributes.get(b'ulid', b'')
                    question_bytes = attributes.get(b'question', b'')
                    answer_bytes = attributes.get(b'answer', b'')
                    embedding_bytes = attributes.get(b'embedding', b'')
                    score_bytes = attributes.get(b'score', b'1.0')
                    
                    # Decode bytes to strings
                    ulid = ulid_bytes.decode('utf-8') if ulid_bytes else doc_id.split(':')[-1]
                    question = question_bytes.decode('utf-8') if question_bytes else ''
                    answer = answer_bytes.decode('utf-8') if answer_bytes else ''
                    score = score_bytes.decode('utf-8') if score_bytes else '1.0'
                    
                    # Handle embedding data
                    if embedding_bytes:
                        embedding_b64 = base64.b64encode(embedding_bytes).decode("utf-8")
                    else:
                        embedding_b64 = ""

                    # Add the found item to the list
                    found_items.append(
                        FaqWithScore(
                            ulid=ulid,
                            question=question,
                            answer=answer,
                            embedding=embedding_b64,
                            score=float(score),
                        )
                    )
                except Exception:
                    # Skip documents that can't be parsed
                    continue

        # return the found items
        return found_items
    
    async def search_by_text(self, query_text: str) -> list[FaqWithScore]:
        """
        Search for FAQs using a text query (converts to embedding internally).
        """
        # Convert text query to embedding
        embedding = self.embedding_service.text_to_embedding(query_text)
        
        # Use existing search method with the generated embedding
        return await self.search(embedding)
