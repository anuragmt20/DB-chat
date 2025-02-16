import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Function to connect to the database
def connect_to_database():
    db_host = st.text_input("Host")
    db_port = st.text_input("Port", value="5432")  # Default for PostgreSQL
    db_user = st.text_input("Username")
    db_password = st.text_input("Password", type="password")
    db_name = st.text_input("Database Name", value="Nacdme")

    if st.button("Connect"):
        try:
            connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            engine = create_engine(connection_string)
            with engine.connect() as conn:
                st.success("Connection successful!")
                st.session_state.engine = engine
        except Exception as e:
            st.error(f"Connection failed: {e}")

# Function to process user queries
def process_query(query):
    if 'engine' not in st.session_state:
        return "Please connect to a database first."

    try:
        if "how many rows" in query.lower():
            table_name = query.split("in table")[-1].strip().strip("'")
            sql = f"SELECT COUNT(*) FROM {table_name};"
            with st.session_state.engine.connect() as conn:
                result = conn.execute(sql).fetchone()
                return f"There are {result[0]} rows in the '{table_name}' table."
        elif "what tables" in query.lower():
            return get_schema()
        else:
            return "I'm not sure how to answer that."
    except Exception as e:
        return f"Error: {e}"

# Function to get the schema of the database
def get_schema():
    if 'engine' not in st.session_state:
        return "Please connect to a database first."

    try:
        with st.session_state.engine.connect() as conn:
            result = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
            tables = [row[0] for row in result]
            return f"Tables in the database: {', '.join(tables)}"
    except Exception as e:
        return f"Error: {e}"

# Function to load the dataset from CSV and insert into the database
def load_and_insert_csv():
    if 'engine' not in st.session_state:
        st.error("Please connect to a database first.")
        return

    # Load the dataset
    try:
        df = pd.read_csv('customers.csv')  # Ensure this file is in the same directory or provide the full path
        st.write("Data Preview:")
        st.dataframe(df)

        # Insert data into the database
        if st.button("Insert Data into Database"):
            try:
                table_name = st.text_input("Table Name to Insert Data Into", value="customers")
                df.to_sql(table_name, st.session_state.engine, if_exists='append', index=False)
                st.success(f"Data inserted into '{table_name}' table successfully!")
            except Exception as e:
                st.error(f"Error inserting data: {e}")
    except Exception as e:
        st.error(f"Error loading CSV: {e}")

# Main function to run the Streamlit app
def main():
    st.title("Chat with Your Database")
    st.write("Connect to your database and start asking questions!")

    connect_to_database()
    load_and_insert_csv()  # Call the function to load and insert CSV data

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Ask a question:")
    if st.button("Submit"):
        st.session_state.chat_history.append({"user": user_input})
        response = process_query(user_input)
        st.session_state.chat_history.append({"bot": response})

    for chat in st.session_state.chat_history:
        if "user" in chat:
            st.write(f"**You:** {chat['user']}")
        if "bot" in chat:
            st.write(f"**Bot:** {chat['bot']}")

if __name__ == "__main__":
    main()