import streamlit as st
import sqlite3
import pandas as pd

# SQLite 연결 및 샘플 쿼리 테이블 초기화
def initialize_sample_query_db():
    conn = sqlite3.connect("sample_queries.db")
    cursor = conn.cursor()
    # 샘플 쿼리 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sample_queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL
    )
    """)
    conn.commit()

    # 기본 샘플 쿼리 삽입 (중복 방지)
    cursor.execute("SELECT COUNT(*) FROM sample_queries")
    if cursor.fetchone()[0] == 0:
        default_queries = [
            "SELECT * FROM employees;",
            "SELECT name, salary FROM employees WHERE salary > 60000;",
            "SELECT department, AVG(salary) as average_salary FROM employees GROUP BY department;"
        ]
        cursor.executemany("INSERT INTO sample_queries (query) VALUES (?)", [(q,) for q in default_queries])
        conn.commit()

    conn.close()

# 샘플 쿼리 읽기
def get_sample_queries():
    conn = sqlite3.connect("sample_queries.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, query FROM sample_queries")
    queries = cursor.fetchall()
    conn.close()
    return queries

# 샘플 쿼리 추가
def add_sample_query(query):
    conn = sqlite3.connect("sample_queries.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sample_queries (query) VALUES (?)", (query,))
    conn.commit()
    conn.close()

# 샘플 쿼리 삭제
def delete_sample_query(query_id):
    conn = sqlite3.connect("sample_queries.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sample_queries WHERE id = ?", (query_id,))
    conn.commit()
    conn.close()

# SQLite 데이터베이스 초기화 함수
def initialize_employee_db():
    conn = sqlite3.connect("test_database.db")
    cursor = conn.cursor()

    # 샘플 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        department TEXT NOT NULL,
        salary REAL NOT NULL
    )
    """)
    conn.commit()

    # 샘플 데이터 추가
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0:  # 데이터가 없는 경우 샘플 데이터 추가
        sample_data = [
            ("Alice", 30, "HR", 50000),
            ("Bob", 40, "Engineering", 75000),
            ("Charlie", 35, "Finance", 60000),
            ("David", 28, "Engineering", 52000),
            ("Eve", 45, "Management", 85000),
        ]
        cursor.executemany("""
        INSERT INTO employees (name, age, department, salary)
        VALUES (?, ?, ?, ?)
        """, sample_data)
        conn.commit()

    conn.close()

# SQL 실행 함수
def execute_sql_query(query):
    conn = sqlite3.connect("test_database.db")
    try:
        result = pd.read_sql_query(query, conn)
        conn.close()
        return result
    except Exception as e:
        conn.close()
        return str(e)

# 앱 초기화
initialize_sample_query_db()
st.set_page_config(layout="wide")
# Streamlit UI
st.title("SQL 연습 앱")

# 데이터베이스 초기화 버튼
if st.button("Initialize Employee Database"):
    initialize_employee_db()
    st.success("Employee database initialized with sample data!")

# SQL 쿼리 입력
st.subheader("SQL Query Execution")
query = st.text_area("Enter your SQL query here:", height=200)

# SQL 실행 버튼
if st.button("Execute Query"):
    if query.strip():
        result = execute_sql_query(query)
        if isinstance(result, pd.DataFrame):
            st.write("Query Result:")
            st.dataframe(result)
        else:
            st.error(f"Error: {result}")
    else:
        st.warning("Please enter a SQL query.")

# 샘플 쿼리 추가
st.subheader("Manage Sample Queries")
if st.button("Save Query as Sample"):
    if query.strip():
        add_sample_query(query)
        st.success("Query added to sample queries!")
    else:
        st.warning("Please enter a query to save.")

# 샘플 쿼리 표시 및 삭제
st.subheader("Saved Sample Queries")
sample_queries = get_sample_queries()
for query_id, sample_query in sample_queries:
    col1, col2 = st.columns([9, 1])
    with col1:
        st.code(sample_query)
    with col2:
        if st.button("Delete", key=f"delete-{query_id}"):
            delete_sample_query(query_id)
            st.experimental_rerun()


# 샘플 쿼리 제공
st.subheader("Sample Queries")
st.code("""
-- Select all employees
SELECT * FROM employees;

-- Find employees with a salary greater than 60000
SELECT * FROM employees WHERE salary > 60000;

-- Count the number of employees in each department
SELECT department, COUNT(*) as employee_count FROM employees GROUP BY department;

-- Calculate average salary by department
SELECT department, AVG(salary) as average_salary FROM employees GROUP BY department;
""")
