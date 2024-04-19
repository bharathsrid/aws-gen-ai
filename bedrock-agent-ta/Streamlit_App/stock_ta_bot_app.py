import InvokeAgentBoto
import streamlit as st
import json
import pandas as pd
from PIL import Image, ImageOps, ImageDraw
import random


# sessionId = "MYSESSION" + str(random.randint(1, 100000))

# Streamlit page configuration
st.set_page_config(page_title="Stock Technical Anlysis Bot", page_icon=":robot_face:", layout="wide")

# Function to crop image into a circle
def crop_to_circle(image):
    mask = Image.new('L', image.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0) + image.size, fill=255)
    result = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    result.putalpha(mask)
    return result

# Title
st.title("Stock Technical Anlysis Bot")



# Display a text box for input
prompt = st.text_input("Please enter your query?", max_chars=2000)
prompt = prompt.strip()

# Display a primary button for submission
submit_button = st.button("Submit", type="primary")

# Display a button to end the session
end_session_button = st.button("End Session")

# Sidebar for user input
st.sidebar.title("Rationale")

def filter_trace_data(trace_data, query):
    if query:
        # Filter lines that contain the query
        return "\n".join([line for line in trace_data.split('\n') if query.lower() in line.lower()])
    return trace_data

# Session State Management
if 'history' not in st.session_state:
    st.session_state['history'] = []

# Function to parse and format response
def format_response(response_body):
    try:
        # Try to load the response as JSON
        data = json.loads(response_body)
        # If it's a list, convert it to a DataFrame for better visualization
        if isinstance(data, list):
            return pd.DataFrame(data)
        else:
            return response_body
    except json.JSONDecodeError:
        # If response is not JSON, return as is
        return response_body

# Handling user input and responses
if submit_button and prompt:
    if 'sessionId' not in st.session_state:
        st.session_state['sessionId'] = "MYSESSION" + str(random.randint(1, 100000))
    event = {
        "sessionId": st.session_state['sessionId'],
        "question": prompt
    }
    print("CALLING BOTO HANDLER")
    # response = agenthelper.lambda_handler(event, None)
    response_text, rationale, full_text = InvokeAgentBoto.bedrock_invoke_agent(input=prompt,sessionId=st.session_state['sessionId'])
    print("COMPLETED BOTO HANDLER")
    # try:
    #     # Parse the JSON string
    #     if response and 'body' in response and response['body']:
    #         response_data = json.loads(response['body'])
    #         # print("TRACE & RESPONSE DATA ->  ", response_data)
    #     else:
    #         print("Invalid or empty response received")
    # except json.JSONDecodeError as e:
    #     print("JSON decoding error:", e)
    #     response_data = None

    # rationale=""
    # the_text=""
    # try:
    #     # Extract the response and trace data
    #     llm_response = format_response(response_data['response'])
    #     rationale = response_data['rationale']
    #     the_text = response_data['text']
    # except:
    #     all_data = "..."
    #     llm_response = "Apologies, but an error occurred. Please rerun the application"

    # Use trace_data and formatted_response as needed
    st.sidebar.text_area("", value=rationale, height=300)
    st.sidebar.title("Full Text")
    st.sidebar.text_area("", value=full_text, height=600) 

    st.session_state['history'].append({"question": prompt, "answer": response_text})
    st.session_state['trace_data'] = rationale

if end_session_button:
    print("ENDING SESSION")
    print(f"session history is {st.session_state['history']}")
    st.session_state['history'].append({"question": "Session Ended", "answer": "Thank you for using AnyCompany Support Agent!"})
    response_text, rationale, full_text = InvokeAgentBoto.bedrock_invoke_agent(input="Thanks for your interaction. Please close the session",sessionId=st.session_state['sessionId'],endSession=True)
    print("BACKINAPP")
    globals()['sessionId'] = "MYSESSION" + str(random.randint(1, 100000))
    print(f"NEWSESSION{st.session_state['sessionId']}")
    st.session_state['history'].clear()
    st.session_state.clear()
    st.session_state['history'] = []
    # agenthelper.lambda_handler(event, None)

# Display conversation history
st.write("## Conversation History")

# Load images outside the loop to optimize performance
human_image = Image.open('images/human_face.png')
robot_image = Image.open('images/robot_face.jpg')
circular_human_image = crop_to_circle(human_image)
circular_robot_image = crop_to_circle(robot_image)

for index, chat in enumerate(reversed(st.session_state['history'])):
    # Creating columns for Question
    col1_q, col2_q = st.columns([2, 10])
    with col1_q:
        st.image(circular_human_image, width=125)
    with col2_q:
        # Generate a unique key for each question text area
        st.text_area("Q:", value=chat["question"], height=50, key=f"question_{index}", disabled=True)

    # Creating columns for Answer
    col1_a, col2_a = st.columns([2, 10])
    if isinstance(chat["answer"], pd.DataFrame):
        with col1_a:
            st.image(circular_robot_image, width=100)
        with col2_a:
            # Generate a unique key for each answer dataframe
            st.dataframe(chat["answer"], key=f"answer_df_{index}")
    else:
        with col1_a:
            st.image(circular_robot_image, width=150)
        with col2_a:
            # Generate a unique key for each answer text area
            st.text_area("A:", value=chat["answer"], height=100, key=f"answer_{index}")

# Example Prompts Section
st.write("## Test Prompts")

# Creating a list of prompts for the Knowledge Base section
test_prompts = [
    {"Prompt": "can you give me list of stocks in brtIndex"},
    {"Prompt": "can you give the top three gainers in terms of percentage in the last 6 months in brtIndex"},
    {"Prompt": "CAn you give list of stocks that has grown over 10% in last 6 months and closed above 20 day SMA"},
    {"Prompt": "Which stocks have closed over both 20 SMA and 50 EMA"}
]

# Displaying the Knowledge Base prompts as a table
st.table(test_prompts)
