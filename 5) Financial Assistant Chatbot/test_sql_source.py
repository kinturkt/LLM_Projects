# Testing with a simple question for Postgres SQL Data Source

from agent_files.sql_agent import generate_sql_response

question = "What was the total revenue for Prologis Atlantic Station 1 in 2023?"
result = generate_sql_response(question)
print(f"Question: {question}")
print(f"Answer: {result}")