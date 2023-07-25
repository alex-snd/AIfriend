from datetime import datetime
from functools import wraps
from http import HTTPStatus
from typing import Dict, Callable

from celery.result import AsyncResult
from fastapi import FastAPI, Request, Path
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_fastapi_instrumentator.metrics import latency

from aifriend.app.api.backend.celeryapp import celery_app
from aifriend.app.api.backend.tasks import predict
from aifriend.app.api.schemas import HumanMessage, TalkResponse, BaseResponse, AIMessage
from aifriend.config import log

api = FastAPI(title='AIfriendAPI', description='API for falcon-7b-instruct model')

instrumentator = Instrumentator().instrument(api).expose(api)
instrumentator.add(latency(buckets=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10,)))


@api.on_event('startup')
def startup() -> None:
    """ API startup handler. """

    log.project_logger.info('FatAPI launched')


def construct_response(handler: Callable[..., Dict]) -> Callable[..., Dict]:
    """
    A decorator that wraps a request handler.

    Parameters
    ----------
    handler : Callable[..., Dict]
        Request processing function.

    Returns
    -------
    wrap : Callable[..., Dict]
        Decorated handler.

    """

    @wraps(handler)
    def wrap(request: Request, *args, **kwargs) -> Dict:
        """
        A wrapper that constructs a JSON response for an endpoint's results.

        Parameters
        ----------
        request : Request
            Client request information.

        Returns
        -------
        response : Dict
            The result of the handler function.

        """

        response = handler(request, *args, **kwargs)

        response['method'] = request.method
        response['timestamp'] = datetime.now().isoformat()
        response['url'] = request.url._url

        return response

    return wrap


@api.get('/', tags=['General'])
@construct_response
def index(request: Request) -> Dict:
    """
    Healthcheck handler.

    Parameters
    ----------
    request : Request
        Client request information.

    Returns
    -------
    Dict:
        OK phrase as a Dict response.

    """

    return {
        'status': HTTPStatus.OK.phrase,
        'status_code': HTTPStatus.OK
    }


@api.post('/talk', tags=['Prediction'], response_model=TalkResponse)
@construct_response
def talk(request: Request, payload: HumanMessage) -> Dict:
    """
    Talk to AI friend.

    Parameters
    ----------
    request : Request
        Client request information.
    payload : HumanMessage
        Message for conversation.

    Returns
    -------
    response : AIMessage
        AI friend response.

    """

    task = predict.delay(payload.message, payload.history)

    response = {
        'status': HTTPStatus.ACCEPTED.phrase,
        'status_code': HTTPStatus.ACCEPTED,
        'task_id': task.id
    }

    return response


@api.get('/status/{task_id}', tags=['Prediction'], response_model=AIMessage)
@construct_response
def status(request: Request,
           task_id: str = Path(...,
                               title='The ID of the task to get status',
                               regex=r'[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}')
           ) -> Dict:
    """
    Get a celery task status.

    Parameters
    ----------
    request : Request
        Client request information.
    task_id : str
        Celery task id.

    Returns
    -------
    response : AIMessage
        Response containing the status of the celery task in the 'state' and 'progress'
        fields if it's still in process,
        error information in 'message' and 'status_code' fields if it's failed,
        otherwise the result of keyless reading in the 'chains' field.

    """

    task = AsyncResult(task_id, app=celery_app)

    if task.failed():
        response = {
            'status': str(task.info),
            'status_code': HTTPStatus.CONFLICT
        }

    elif task.ready():
        message, history = task.get()

        response = {
            'status': HTTPStatus.OK.phrase,
            'status_code': HTTPStatus.OK,
            'message': message,
            'history': history,
        }
    else:
        response = {
            'status': HTTPStatus.PROCESSING.phrase,
            'status_code': HTTPStatus.PROCESSING,
            'state': task.status,
        }

    return response


@api.delete('/{task_id}', tags=['Prediction'], response_model=BaseResponse)
@construct_response
def delete_prediction(request: Request,
                      task_id: str = Path(...,
                                          title='The ID of the task to forget',
                                          regex=r'[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}')
                      ) -> Dict:
    """
    Delete task result in the celery backend database.

    Parameters
    ----------
    request : Request
        Client request information.
    task_id : str
        Task ID to delete its result from celery backend database.

    Returns
    -------
    response : Dict
        OK phrase.

    """

    task = AsyncResult(task_id, app=celery_app)

    if task.ready():
        task.forget()
    else:
        task.revoke(terminate=True)

    response = {
        'status': HTTPStatus.OK.phrase,
        'status_code': HTTPStatus.OK
    }

    return response
