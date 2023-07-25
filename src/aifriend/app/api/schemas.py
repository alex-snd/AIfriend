from typing import List, Dict, Any, Optional

from pydantic import BaseModel


class HumanMessage(BaseModel):
    """ Content declaration of the request body to communicate with AI friend """

    message: str
    history: List[Dict[str, Any]]

    class Config:
        """ Conversation example for API documentation"""

        schema_extra = {
            "example": {
                "message": "Ha, OK.",
                "history": [
                    {"type": "human",
                     "data": {
                         "content": "Think of a name for automaker that builds family cars with big V8 engines. "
                                    "The name must be a single word and easy to pronounce.",
                         "additional_kwargs": {},
                         "example": False}
                     },
                    {"type": "ai",
                     "data": {
                         "content": "V8Cars - pronounced as 'Vee eeee' or 'Vee Eights.'",
                         "additional_kwargs": {},
                         "example": False
                     }
                     }
                ]
            }
        }


class BaseResponse(BaseModel):
    """ Basic contents declaration of the response body for all API handlers. """

    status: str
    method: str
    status_code: int
    timestamp: str
    url: str

    class Config:
        """ BaseResponse example for API documentation"""

        schema_extra = {
            "example": {
                "status": "Accepted",
                "method": "POST",
                "status_code": 202,
                "timestamp": "2023-07-04T12:53:35.512412",
                "url": "http://localhost:8001/recover",
            }
        }


class TalkResponse(BaseResponse):
    """ Contents declaration of the "talk" handler response body. """

    task_id: Optional[str]

    class Config:
        """ TalkResponse example for API documentation"""

        schema_extra = {
            "example": {
                "status": "Accepted",
                "method": "POST",
                "status_code": 202,
                "timestamp": "2023-07-04T12:53:35.512412",
                "url": "http://localhost:8001/recover",
                "task_id": "909e4817-cca3-4dbf-a598-f7f83c5d60c9"
            }
        }


class AIMessage(BaseResponse):
    """ Contents declaration of the "status" API handler response body. """

    message: Optional[str]
    history: Optional[List[Dict[str, Any]]]
    state: Optional[str]

    class Config:
        """ Conversation example for API documentation"""

        schema_extra = {
            "example": {
                "message": "Similarity embeddings use pre-defined words and phrases to represent concepts, "
                           "whereas search embeddings allow a more granular representation of concepts by "
                           "using words as placeholders in a document to represent similar documents.",
                "history": [
                    {"type": "human",
                     "data": {
                         "content": "Think of a name for automaker that builds family cars with big V8 engines. "
                                    "The name must be a single word and easy to pronounce.",
                         "additional_kwargs": {},
                         "example": False}},
                    {"type": "ai",
                     "data": {
                         "content": "V8Cars - pronounced as 'Vee eeee' or 'Vee Eights.'",
                         "additional_kwargs": {},
                         "example": False}},
                    {"type": "human",
                     "data": {
                         "content": "Ha, OK. what is the difference between Similarity embeddings "
                                    "and search embeddings",
                         "additional_kwargs": {},
                         "example": False}},
                    {"type": "ai",
                     "data": {
                         "content": "Similarity embeddings use pre-defined words and phrases to represent concepts, "
                                    "whereas search embeddings allow a more granular representation of concepts by "
                                    "using words as placeholders in a document to represent similar documents.",
                         "additional_kwargs": {},
                         "example": False}}]
            }
        }
