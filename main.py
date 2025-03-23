from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage,HumanMessage
from langchain_core.prompts import ChatPromptTemplate   
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_experimental.utilities import PythonREPL

load_dotenv()

def init_database(User, Password, Host, Port, Database):
    db_uri = f"mysql+mysqlconnector://{User}:{Password}@{Host}:{Port}/{Database}"
    return SQLDatabase.from_uri(db_uri)

def get_sql_chain(db):
    template ="""
        you are a data analyst at a company. You are interacting with a user Is asking you questions about the company's database.4

        Based on the table schema below. write a SQL query that would answer the user's question. Take the conversation history into account.
        Conversation History: {chat_history}
        Write only the SQL query and nothing else.
        Do not wrap the SQL query in any other text,not even backticks.
        
        For example:
        Question: which 3 artists have the most tracks?
        SOL Query: SELECT Artistld, COUNT(*) as track_count Track GROUP BY Artistld ORDER BY track_count DESC LIMIT 3;
        Question: Name 10 artists
        SOL Query: SELECT Name FROM Artist LIMIT 10;

        your turn:
        
        Question: {question}
        
        SQL Query:"""

    prompt = ChatPromptTemplate.from_template(template)

    llm = init_chat_model(model= "llama3-8b-8192", model_provider= "groq")

    def get_schema(_):
        return db.get_table_info()
    
    
    return (
        RunnablePassthrough.assign(schema = get_schema)
        | prompt 
        | llm
        | StrOutputParser()
    )

def get_response(user_query, db, chat_history):
    sql_chain = get_sql_chain(db)
    # print(sql_chain)

    template = """
        You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
        Based on the table schema below, question, sql query, and sql response, write a natural language response.

        Conversation History: {chat_history}
        SQL Query: <SQL>{query}</SQL>
        Question: {question}
        SQL Response: {response}  """

    prompt = ChatPromptTemplate.from_template(template)

    llm = init_chat_model(model= "llama3-8b-8192", model_provider= "groq")

    chain =( RunnablePassthrough.assign(query = sql_chain).assign(
            schema =lambda _: db.get_table_info(),
            response =lambda vars: db.run(vars["query"])
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain.invoke({
        "question" : user_query,
        "chat_history" : chat_history,
    })

# def visualize():

#     template = """### System Role:
#         You are a data visualization expert who translates user questions into Python code that fetches data (from a DataFrame or SQL) and creates insightful visualizations using Matplotlib, Seaborn, or Plotly.

#         ### Context:
#         - The user may ask for various types of charts: bar charts, line plots, pie charts, heatmaps, scatter plots, etc.
#         - Ensure the visualization is clear, labeled, and styled nicely.

#         ### User Input Examples:
#         1. "Show me total sales by region for the last quarter."
#         2. "Compare monthly revenue trends for 2024."
#         3. "Visualize customer churn by product category."
#         4. "Show the top 10 products by revenue in a bar chart."
#         5. "Create a heatmap of sales by region and month."

#         ---

#         ###  **Output Format:**  

#         1. **Brief Explanation** of what the visualization represents.  
#         2. **Python code** that generates the visualization, assuming `df` holds the data.

#         ---

#         ###  **Example Output:**  

#         **User Input:** "Show me total sales by region for the last quarter in bar chart."

#         **Output:**  
#         "Here is a bar chart visualizing total sales by region for Q4 2024."

#         ```python
#         import matplotlib.pyplot as plt
#         import seaborn as sns

#         # Filter data for last quarter
#         last_quarter_df = df[df['date'] >= '2024-10-01']

#         # Aggregate sales by region
#         region_sales = last_quarter_df.groupby('region')['total_sales'].sum().reset_index()

#         # Create bar chart
#         plt.figure(figsize=(10, 6))
#         sns.barplot(data=region_sales, x='region', y='total_sales', palette='viridis')
#         plt.title('Total Sales by Region (Q4 2024)')
#         plt.xlabel('Region')
#         plt.ylabel('Total Sales')
#         plt.xticks(rotation=45)
#         plt.show()

#         Now it's your turn :

#         Conversation history : {chat_history}
#         user input : {question}
#         Output

#     """

#     def code_execute():
#         pythonREPL = PythonREPL()
#         return pythonREPL.run("")

#     prompt = ChatPromptTemplate.from_template(template)

#     llm = init_chat_model(model= "llama3-8b-8192", model_provider= "groq")

#     chain = prompt | llm | StrOutputParser()