import redis
import redis.asyncio as aioredis
from redis import ResponseError
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType

# redis host
host = "localhost"

# redis port
port = 6379

# the name of the index
index_name = "faq:index"

# only look at keys that start with "faq:"
prefixes = ["faq:"]

# index keys that are hashes
index_type = IndexType.HASH

# connect to Redis on localhost and port 6379, change for your Redis
# Use async Redis client for async operations
db = aioredis.Redis(host=host, port=port, protocol=3, decode_responses=False)
# Keep sync client for index setup
sync_db = redis.Redis(host=host, port=port, protocol=3, decode_responses=False)

# the index definition
definition = IndexDefinition(prefix=prefixes, index_type=index_type)

# the schema for the index treats the question and answer as text fields
# and the embedding as a vector field (384 dims for all-MiniLM-L6-v2)
schema = (
    TextField("question"),
    TextField("answer"),
    VectorField(
        "embedding",
        "FLAT",
        {"TYPE": "FLOAT32", "DIM": 384, "DISTANCE_METRIC": "COSINE"},
    ),
)

try:
    # check if the index exists (using sync client for setup)
    sync_db.ft(index_name).info()
except ResponseError as err:
    # if we get anything other than the expected error, raise it
    if "no such index" not in str(err) and "Unknown index name" not in str(err):
        raise err
    # create the index if it doesn't exist
    sync_db.ft(index_name).create_index(fields=schema, definition=definition)
