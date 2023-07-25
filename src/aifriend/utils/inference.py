import re
from typing import List, Dict, Any

import torch
from langchain import PromptTemplate
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.llms import HuggingFacePipeline
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.schema import BaseOutputParser, messages_from_dict
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    StoppingCriteria,
    StoppingCriteriaList,
    pipeline,
    BitsAndBytesConfig
)

from aifriend.config import var


class StopGenerationCriteria(StoppingCriteria):
    """ Help to control the output and prevent the model from rambling or hallucinating questions and conversations """

    def __init__(self, tokens: List[List[str]], tokenizer: AutoTokenizer, device: torch.device):
        stop_token_ids = [tokenizer.convert_tokens_to_ids(t) for t in tokens]

        self.stop_token_ids = [
            torch.tensor(x, dtype=torch.long, device=device) for x in stop_token_ids
        ]

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        for stop_ids in self.stop_token_ids:
            if torch.eq(input_ids[0][-len(stop_ids):], stop_ids).all():
                return True

        return False


class CleanupOutputParser(BaseOutputParser):
    """ Helps to remove the trailing user/human/ai string from the generated output """
    def parse(self, text: str) -> str:
        user_pattern = r"\nUser"
        text = re.sub(user_pattern, "", text)
        human_pattern = r"\nHuman:"
        text = re.sub(human_pattern, "", text)
        ai_pattern = r"\nAI:"
        return re.sub(ai_pattern, "", text).strip()

    @property
    def _type(self) -> str:
        return "output_parser"


def get_llm() -> HuggingFacePipeline:
    if torch.cuda.is_available():
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )

        model = AutoModelForCausalLM.from_pretrained(
            var.MODEL_ID,
            trust_remote_code=True,
            device_map="auto",
            cache_dir=var.CHECKPOINTS_DIR,
            offload_folder=var.OFFLOAD_DIR,
            offload_state_dict=True,
            quantization_config=quantization_config
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            var.MODEL_ID,
            trust_remote_code=True,
            device_map="auto",
            cache_dir=var.CHECKPOINTS_DIR,
            offload_folder=var.OFFLOAD_DIR,
            offload_state_dict=True,
        )

    model = model.eval()
    tokenizer = AutoTokenizer.from_pretrained(var.TOKENIZER_ID, cache_dir=var.CHECKPOINTS_DIR)
    stopping_criteria = StoppingCriteriaList([StopGenerationCriteria(var.STOP_TOKENS, tokenizer, model.device)])

    generation_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=300,
        # max_length=300,
        do_sample=True,
        top_k=10,
        device_map="auto",
        use_cache=True,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,
        stopping_criteria=stopping_criteria,
    )

    return HuggingFacePipeline(pipeline=generation_pipeline)


def get_conversation_chain(llm: HuggingFacePipeline,
                           history: List[Dict[str, Any]]
                           ) -> ConversationChain:
    prompt = PromptTemplate(input_variables=["history", "input"], template=var.INTRODUCTION_PROMPT)

    if history:
        if len(history[0]) > var.FLIRTY_THRESHOLD:
            prompt = PromptTemplate(input_variables=["history", "input"], template=var.FLIRTY_PROMPT)
        elif len(history[0]) > var.FRIEND_THRESHOLD:
            prompt = PromptTemplate(input_variables=["history", "input"], template=var.FRIEND_PROMPT)

    memory = ConversationBufferWindowMemory(
        chat_memory=ChatMessageHistory(messages=messages_from_dict(history)),
        memory_key="history",
        k=var.HISTORY_SIZE,
        return_only_outputs=True)

    return ConversationChain(
        llm=llm,
        memory=memory,
        prompt=prompt,
        output_parser=CleanupOutputParser(),
        verbose=True
    )
