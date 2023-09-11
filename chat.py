import streamlit as st

## Llama chat
# https://llama2.streamlit.app/
# https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/
# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I assist you today?"}
    ]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


def clear_chat_history():
    st.session_state.messages = [
        {"role": "assistant", "content": "How may I assist you today?"}
    ]


st.sidebar.button("Clear Chat History", on_click=clear_chat_history)


# Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot
def generate_llama2_response(prompt_input):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run(
        "a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5",
        input={
            "prompt": f"{string_dialogue} {prompt_input} Assistant: ",
            "temperature": temperature,
            "top_p": top_p,
            "max_length": max_length,
            "repetition_penalty": 1,
        },
    )
    return output


# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ""
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)


import random
import time

## Chat with streaming
# https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps
import streamlit as st

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

# https://towardsdatascience.com/build-your-own-chatgpt-like-app-with-streamlit-20d940417389

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]


def generate_response(prompt):
    st.session_state["messages"].append({"role": "user", "content": prompt})

    completion = openai.ChatCompletion.create(
        model=model, messages=st.session_state["messages"]
    )
    response = completion.choices[0].message.content
    st.session_state["messages"].append({"role": "assistant", "content": response})


# Displaying the conversation
from streamlit_chat import message

if st.session_state["generated"]:
    with response_container:
        for i in range(len(st.session_state["generated"])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")
            message(st.session_state["generated"][i], key=str(i))

# Printing additional information
total_tokens = completion.usage.total_tokens
prompt_tokens = completion.usage.prompt_tokens
completion_tokens = completion.usage.completion_tokens

if model_name == "GPT-3.5":
    cost = total_tokens * 0.002 / 1000
else:
    cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000

st.write(
    f"Model used: {st.session_state['model_name'][i]}; Number of tokens: {st.session_state['total_tokens'][i]}; Cost: ${st.session_state['cost'][i]:.5f}"
)

### the following worked partly
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(
        message["role"],
        # avatar=avatar,
    ):
        st.markdown(message["content"])


# Accept user input
if prompt := st.chat_input("How can I help?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display user message in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

    # Iterate through the messages and generate responses
    for message in st.session_state.messages:
        if message["role"] == "user":
            # Generate response from your custom model
            # Use the custom query engine to get the response
            response = functions.get_response(message["content"], query_engine)
            full_response += response

            # Display the response
            message_placeholder.markdown(full_response + "▌")

    # Append to session_state.messages
    st.session_state.messages.append({"role": "assistant", "content": response})


## Another solution
## Chat
# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User-provided prompt
if prompt := st.chat_input("How may I help?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    pdb.set_trace()
    # Display user message in chat message container
    with st.chat_message("user"):
        st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Sifting through the documents..."):
                response = functions.get_response(prompt, query_engine_to_use)
                st.write(response)
        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)


#### Steramlit things to try later
# st.info(
#     "This app is maintained by the deities of paper work.\n"
#     "You can learn more about us at [officegods.com](https://officegods.com).",
#     icon="ℹ️",
# )


## avatar - little picture shown instead of the robot
# avatar = np.array(Image.open(".streamlit/hengst.png"))
