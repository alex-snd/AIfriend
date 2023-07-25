from typing import Tuple, List, Dict, Any

from aifriend.app.api.backend.celeryapp import celery_app
from aifriend.app.api.backend.tasksbase import PredictTask


@celery_app.task(bind=True, base=PredictTask)
def predict(self: PredictTask,
            message: str,
            history: List[Dict[str, Any]]
            ) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Celery task implementation that performs text generation.

    Parameters
    ----------
    self : ArtifactsTask
        Celery task base class.
    message : str
        Human message to answer.
    history : List[Dict[str, Any]]
        Chat history.

    Returns
    -------
    (ai_response, updated_history) : Tuple[str, List[Dict[str, Any]]]
        AI friend answer and updated history chat.

    Raises
    ------
    AssertionError:
        If the message is empty.

    """
    from langchain.schema import messages_to_dict
    from aifriend.utils.inference import get_conversation_chain

    assert len(message) != 0, "Human message is empty"

    conversation_chain = get_conversation_chain(llm=self.llm, history=history)
    output = conversation_chain(message)
    history = messages_to_dict(conversation_chain.memory.chat_memory.messages)

    return output['response'], history
