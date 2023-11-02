# This is a streamlit app with chat history

from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock
import boto3
from botocore.config import Config
from langchain import PromptTemplate,SagemakerEndpoint,SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.chains import create_sql_query_chain
from sqlalchemy import create_engine


import streamlit as st
import boto3

def get_schema(_):
    return athena_db_connection.get_table_info()



st.set_page_config(page_title="StreamlitChatMessageHistory", page_icon="📖")
st.title("📖 StreamlitChatMessageHistory")

"""
A basic example of using StreamlitChatMessageHistory to help LLMChain remember messages in a conversation.
The messages are stored in Session State across re-runs automatically. You can view the contents of Session State
in the expander below. View the
[source code for this app](https://github.com/langchain-ai/streamlit-agent/blob/main/streamlit_agent/basic_memory.py).
"""

# Set up memory
# msgs = StreamlitChatMessageHistory(key="langchain_messages")
msgs = StreamlitChatMessageHistory()

print("MSGS SET")
# memory = ConversationBufferMemory(chat_memory=msgs)
# memory = ConversationBufferMemory(return_messages=True)
memory = ConversationBufferMemory(memory_key="history", chat_memory=msgs)


if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you?")

view_messages = st.expander("View the message contents in session state")

# initiate Bedrock
bedrock_run_time = boto3.client(service_name='bedrock-runtime')


inference_modifier = {
    "temperature": 1,
    "top_p": .999,
    "top_k": 250,
    "max_tokens_to_sample": 300,
    "stop_sequences": ["\n\nHuman:"]
}
bedrock_llm = Bedrock(
    model_id="anthropic.claude-v2",
    client=bedrock_run_time,
    model_kwargs=inference_modifier,
)


# Get an OpenAI API Key before continuing   
# if "openai_api_key" in st.secrets:
#     openai_api_key = st.secrets.openai_api_key
# else:
#     openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
# if not openai_api_key:
#     st.info("Enter an OpenAI API Key to continue")
#     st.stop()

# Set up the LLMChain, passing in memory
template = """You are an AI chatbot having a conversation with a human.

{history}
Human: {human_input}
AI: """
prompt = PromptTemplate(input_variables=["history", "human_input"], template=template)
# llm_chain = LLMChain(llm=OpenAI(openai_api_key=openai_api_key), prompt=prompt, memory=memory)



"""
Here we will build the required parameter to connect athena and query database.
1. Data is stored in S3 and metadata in Glue metastore.
2. Create a profille which will have access to the required service.
3. if the database exists and s3 buckets exists use them else create.

"""
region = 'us-east-1'
athena_url = f"athena.{region}.amazonaws.com" 
athena_port = '443' #Update, if port is different
athena_db = 'demo-emp-deb-2' #from user defined params
glue_databucket_name='athena-query-bucket-bharsrid'
s3stagingathena = f's3://{glue_databucket_name}/athenaresults/' 
athena_wkgrp = 'primary' 
athena_connection_string = f"awsathena+rest://@{athena_url}:{athena_port}/{athena_db}?s3_staging_dir={s3stagingathena}/&work_group={athena_wkgrp}"

print(athena_connection_string)
athena_engine = create_engine(athena_connection_string, echo=True)
athena_db_connection = SQLDatabase(athena_engine)



bedrock_chain = LLMChain(
    llm=bedrock_llm,
    prompt=prompt,
    verbose=True,
    memory=memory,
)


# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# If user inputs a new prompt, generate and draw a new response
if prompt := st.chat_input():
    st.chat_message("human").write(prompt)
    # Note: new messages are saved to history automatically by Langchain during run
    response = bedrock_chain.run(prompt)
    st.chat_message("ai").write(response)

# Draw the messages at the end, so newly generated ones show up immediately
with view_messages:
    """
    Memory initialized with:
    ```python
    msgs = StreamlitChatMessageHistory(key="langchain_messages")
    memory = ConversationBufferMemory(chat_memory=msgs)
    ```

    Contents of `st.session_state.langchain_messages`:
    """
    view_messages.json(st.session_state.langchain_messages)
