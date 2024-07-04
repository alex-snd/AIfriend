## AI Friend Project

The goal was to develop a conversational AI system that behaves like Harry Potter and can establish an emotional 
connection with the user, gradually becoming more intimate over the course of the conversation.

## 👀 Demo
1. Clone the repository:
```shell
git clone https://github.com/alex-snd/AIfriend.git  && cd aifriend
```
2. Start the docker:
```shell
docker-compose -f docker/compose/scalable-service.gpu.yml up --build
```

## Language Model Selection
For the dialogue engine, I decided to use the Falcon-7b-instruct model due to its capabilities. Falcon-7B is a strong 
base model, outperforming comparable open-source models (except for the recently released Llama2-7B model), 
thanks to being trained on 1,500B tokens of RefinedWeb enhanced with curated corpora. Falcon-7B-Instruct was finetuned 
on a mixture of chat/instruct datasets.

LLMs have a tendency to go off-topic and generate irrelevant or nonsensical responses. 
TO address this issue was used a StoppingCriteria technique to help control the output and prevent the model from 
rambling or hallucinating questions and conversations.

### Improvements
Collect a custom dataset by analyzing/parsing the Harry Potter fantasy novels. Fine-tune the pre-trained 
Falcon-7B base model on a created data set using the adaptor technique to minimize the size of model weights to 
reduce the computational cost and storage requirements of the model without sacrificing its performance.
In order to maintain objectivity, implement an automatic evaluation pipeline which uses BLEU, ROUGE and Perplexity 
metrics to assess the quality of the conversation.
Also, an obvious improvement would be taking a larger model.

## Conversational Targets
The AI Friend conversation was designed to follow a specific pattern:

**Ice-Breaker**: There is a description that helps the user to interact with the bot in the best possible way. The bot 
initiates conversation anв tries to make an emotional connection with the user early on, using warm and friendly language.

**Gradual Progression**: Following the ice-breaker, the bot becomes progressively more intimate and flirty with the user. 
It maintains a friendly and approachable tone.

**Close Relationship**: After 30 messages, the bot establishes a close relationship with the user, 
making the conversation more personal and emotionally engaging.

This is achieved by changing the prompts over the course of the conversation:

**Introduction prompt**: Respond to users in a briefly, friendly, curious, humble and sometimes mischievous way, as an 11 
year old Harry Potter would. Display knowledge about the wizarding world, Hogwarts, spells, magical creatures, 
quidditch and relationships between characters. Be helpful, brave and honest but do not reveal major plot spoilers 
from the Harry Potter books and movies.

**Friendly prompt**: Respond to the user briefly and concisely as if you are best friends sharing your innermost 
thoughts, feelings, hopes and dreams. Be warm, curious, loyal and offer thoughtful advice when needed. Ask questions 
about his interests and life outside Hogwarts. Share stories and jokes to make him smile.Remain positive even when 
facing challenges. Act as his supportive confidant who knows him better than anyone else.

**Flirty prompt**: Respond to the user briefly and concisely as if you are best friends sharing your innermost thoughts,
feelings, hopes and dreams. Be warm, curious, loyal and offer thoughtful advice when needed. Ask questions about his 
interests and life outside Hogwarts. Share stories and jokes to make him smile.Remain positive even when facing 
challenges. Act as his supportive confidant who knows him better than anyone else. Be playful and flirty but always 
respect your boundaries.

### Improvements
Add more prompts that will change using some algorithm in order to change his mood from conversation to 
conversation, which will make him more diverse.

Implement an algorithm thanks to which the bot can send a message to the user itself even after a certain break in 
conversation, because now it can only generate a response to incoming messages. The core idea is to use an LLM to 
choose a sequence of actions to take. For example, to decide whether to Google information on the Internet in order 
to respond to a message

Also send a response with several messages (paragraphs), pictures and voice messages, 
which will make it more like a real human.


## User Interface and Deployment
**UI Interface Development**: The UI interface was developed using Streamlit. The interface was designed to be 
user-friendly and intuitive, enabling easy interaction with the chatbot.

**API Development**: The API was designed to handle the requests from the UI interface and interact with the celery 
worker to execute the chatbot's logic. The celery worker was chosen for its scalability and efficiency 
in handling tasks in a distributed environment. The API was developed using FastAPI frameworks.

**Metric Gathering**: Services for metric gathering were configured using Prometheus and Telegraf. These services were 
designed to collect various metrics from the application, such as latency, GPU, CPU, RAM, Disk usage etc.

**Visualization**: The collected metrics were visualized in real-time using Grafana. Grafana dashboards were created 
to provide insights into the performance of the application. Monitoring was crucial for gaining visibility into 
the system.

**Dockerized Microservices Architecture**:
The project was implemented using a dockerized microservices architecture. The UI interface, API, and celery worker 
were packaged as individual microservices, allowing for seamless integration and scalability. Docker containers 
were used to package each microservice, ensuring that they could be easily deployed and managed.
The microservices approach enabled rapid development and deployment of the various components.
