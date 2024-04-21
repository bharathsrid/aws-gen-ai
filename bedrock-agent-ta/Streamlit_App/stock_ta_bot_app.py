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
    print("CALLING Bedrock agent")
    # response = agenthelper.lambda_handler(event, None)
    response_text, rationale, full_text = InvokeAgentBoto.bedrock_invoke_agent(input=prompt,sessionId=st.session_state['sessionId'])


    # Use trace_data and formatted_response as needed
    st.sidebar.text_area("", value=rationale, height=300)
    st.sidebar.title("Full Text")
    st.sidebar.text_area("", value=full_text, height=600) 

    st.session_state['history'].append({"question": prompt, "answer": response_text})
    st.session_state['trace_data'] = rationale

if end_session_button:
    print("ENDING SESSION")
    if 'history' in st.session_state:
        print("INENDING")
        st.session_state['history'].append({"question": "Session Ended", "answer": "Thank you for using AnyCompany Support Agent!"})
        st.session_state['history'].clear()
    response_text, rationale, full_text = InvokeAgentBoto.bedrock_invoke_agent(input="Thanks for your interaction. Please close the session",sessionId=st.session_state['sessionId'],endSession=True)
    globals()['sessionId'] = "MYSESSION" + str(random.randint(1, 100000))
    print(f"NEW SESSION Id is {st.session_state['sessionId']}")
    
    st.session_state.clear()
    st.session_state['history'] = []
    # agenthelper.lambda_handler(event, None)

# Display conversation history
st.write("## Conversation History")

# Load images outside the loop to optimize performance
human_image = Image.open('images/human_face_1.png')
robot_image = Image.open('images/robot_face_1.png')
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

    # Creating columns for Answers
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



# Creating a list of prompts for the Knowledge Base section
test_prompts = [
    "Can you give me list of stocks in Nasdaq",
    "Can you give the top three gainers in terms of percentage in the last 6 months in Nifty",
    "Can you give list of stocks that has grown over 10% in last 6 months and closed above 20 day SMA. Use stocks from Nasdaq index",
    "Which stocks have closed over both 20 SMA and 50 EMA in the FTSE index",
    "Can you give list of stocks that has grown over 10% in last 6 months and closed above 20 day SMA and 50 day EMA. Use stocks from FTSE index",
    "of these stocks are there any that have grown over 25% in the last months. If so can you give me the stocks and their growth percent over 6 months"

]

test_prompts_string = ""
# iterate over test prompt and add the number starting with index in the list + 1
for index, prompt in enumerate(test_prompts):
    test_prompts_string = test_prompts_string + str(index + 1) + ". " + prompt + "\n"


st.write("## About the Tool")
about = ""
about = about + "This chatbot uses Amazon Bedrock agents and orchestrates various steps using multiple lambda based tools at its disposal, to get you the answer.\n\n"
about = about + "**The tools at its disposal are**"
about = about + "\n"
about = about + "1. Tool to get stocks in an index. It has data for FTSE, Nasdaq and FTSE indeices\n"
about = about + "2. For a given list of stocks the change percentage over a number of days up to 1 year\n"
about = about + "3. For a given list of stocks get the technical indicators over a number of days. Currently it supports Simple Moving Average (SMA) and Exponenital Moving Average (EMA)\n"

st.markdown(about)

# Displaying the Knowledge Base prompts as a table
# Example Prompts Section
st.write("## Test Prompts")
st.text(test_prompts_string)
