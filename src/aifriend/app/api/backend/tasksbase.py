import celery


class PredictTask(celery.Task):
    def __init__(self):
        super(PredictTask, self).__init__()
        self.llm = None

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed).
        Avoids the need to load model on each task request.

        """

        if not self.llm:
            from aifriend.utils.inference import get_llm

            self.update_state(state='LOADING')
            self.llm = get_llm()

        self.update_state(state='PREDICT')

        return self.run(*args, **kwargs)
