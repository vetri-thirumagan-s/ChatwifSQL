import streamlit as st
from main import init_database 
from main import get_sql_chain
from main import get_response
from langchain_core.messages import AIMessage, HumanMessage

st.set_page_config(page_title="Chat with SQL", page_icon=":speech_balloon:")

st.title("Chat with Database")

with st.sidebar:
    st.subheader("Settings")
    st.text_input(label= "Host", value="localhost", key= "Host")
    st.text_input(label= "Port", value= "3306", key= "Port")
    st.text_input(label= "User", value= "root", key= "User")
    st.text_input(label= "Password", value= "qwerty123", key= "Password")
    st.text_input(label= "Database", value= "Chinook", key= "Database")
    
    if st.button(label= "Connect"):
        with st.spinner("Connecting to Database"):
            db = init_database(
                st.session_state["User"],
                st.session_state["Password"],
                st.session_state["Host"],
                st.session_state["Port"],
                st.session_state["Database"],
            )
            st.session_state.db = db
            st.success("Connected to Database")



if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content= """Hello, I'm a SQL Assistant. Ask me anything about your database""")
        ]

for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

user_query = st.chat_input("Type a message....")

if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content = user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        # sql_chain = get_sql_chain(st.session_state.db)
        # response = sql_chain.invoke({
        #     "chat_history" : st.session_state.chat_history,
        #     "question" : user_query
        # })
        response = get_response(user_query= user_query,db= st.session_state.db,chat_history=st.session_state.chat_history)
        st.markdown(response)
    
    st.session_state.chat_history.append(AIMessage(content= response))