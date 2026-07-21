from pydantic import BaseModel


class FaqId(BaseModel):
    ulid: str


class Faq(FaqId):
    question: str
    answer: str
    embedding: str


class FaqWithScore(Faq):
    score: float

class FaqCreate(BaseModel):
    question: str
    answer: str
    embedding: str

class FaqSearchRequest(BaseModel):
    query: str  # The text query like "where is my refund"