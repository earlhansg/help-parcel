from pydantic import BaseModel


class FaqId(BaseModel):
    ulid: str


class Faq(FaqId):
    question: str
    answer: str
    embedding: str


class FaqWithScore(Faq):
    score: float
