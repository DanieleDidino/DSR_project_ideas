import streamlit as st

# https://towardsdatascience.com/build-your-own-chatgpt-like-app-with-streamlit-20d940417389
# Keeping track of conversation history
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

# https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps#build-a-chatgpt-like-app
import openai
import streamlit as st


openai.api_key = st.secrets["OPENAI_API_KEY"]

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display user message in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # emulate streaming
        for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})


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
