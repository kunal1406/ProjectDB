# db_utils.py
import pyodbc
import pandas as pd
import streamlit as st

# Adjust this connection string as needed
DB_PATH = r"C:/Users/KUNAL MEHTA/Desktop/ACS Pro/Analysis/Database/ClientWorkflowDB.accdb"
CONN_STR = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={DB_PATH};"

def get_connection():
    return pyodbc.connect(CONN_STR)

# def get_client_details(job_id: int) -> pd.DataFrame:
#     conn = get_connection()
#     query = "SELECT * FROM ClientDetails WHERE JobID = ?"
#     df = pd.read_sql(query, conn, params=[job_id])
#     conn.close()
#     return df


################################################################


def get_client_details(conn, job_id: int) -> pd.DataFrame:
    query = "SELECT * FROM ClientDetails WHERE JobID = ?"
    return pd.read_sql(query, conn, params=[job_id])

def check_workflow_exists_for_job(conn, job_id: int) -> bool:
    query = "SELECT COUNT(*) AS Cnt FROM GeneratedWorkflows WHERE JobID = ?"
    df = pd.read_sql(query, conn, params=[job_id])
    return df['Cnt'].iloc[0] > 0

def generate_workflow_for_job(conn, job_id: int):
    # First fetch client type & job type
    client_df = get_client_details(conn, job_id)
    if len(client_df) == 0:
        st.error("No client details found for this JobID.")
        return
    client_type = client_df['ClientType'].iloc[0]
    job_type = client_df['JobType'].iloc[0]

    # Fetch from WorkflowTemplate
    template_query = "SELECT * FROM WorkflowTemplate WHERE ClientType = ? AND JobType = ?"
    workflow_templates = pd.read_sql(template_query, conn, params=[client_type, job_type])

    if len(workflow_templates) == 0:
        st.warning("No workflow templates found for this combination of ClientType and JobType.")
        return

    # Prepare data to insert into GeneratedWorkflows
    generated_workflows = workflow_templates.copy()
    generated_workflows['JobID'] = job_id
    generated_workflows['JobType'] = job_type
    generated_workflows = generated_workflows[['JobID', 'JobType', 'Sort', 'Task', 'TaskDescription', 'Estimated']]

    insert_query = """
    INSERT INTO GeneratedWorkflows (JobID, JobType, Sort, Task, TaskDescription, EstimatedTime)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor = conn.cursor()
    for _, row in generated_workflows.iterrows():
        cursor.execute(insert_query, row['JobID'], row['JobType'], row['Sort'], row['Task'], row['TaskDescription'], row['Estimated'])
    conn.commit()
    st.success("Workflow generated successfully!")

def get_generated_workflows_for_job(conn, job_id: int) -> pd.DataFrame:
    query = "SELECT WorkflowID, Task, TaskDescription, EstimatedTime, ActualTime, Initials FROM GeneratedWorkflows WHERE JobID = ?"
    return pd.read_sql(query, conn, params=[job_id])

def update_task_in_workflow(conn, workflow_id: int, actual_time: float, initials: str):
    update_query = """
    UPDATE GeneratedWorkflows
    SET ActualTime = ?, Initials = ?
    WHERE WorkflowID = ?
    """
    cursor = conn.cursor()
    cursor.execute(update_query, actual_time, initials, workflow_id)
    conn.commit()

def get_reporting_data(conn) -> pd.DataFrame:
    query = """
    SELECT JobID, SUM(EstimatedTime) AS TotalEstimatedTime, SUM(ActualTime) AS TotalActualTime
    FROM GeneratedWorkflows
    GROUP BY JobID
    """
    return pd.read_sql(query, conn)

#################################################################

# def get_workflow_templates(client_type: str, job_type: str) -> pd.DataFrame:
#     conn = get_connection()
#     query = "SELECT * FROM WorkflowTemplate WHERE ClientType = ? AND JobType = ?"
#     df = pd.read_sql(query, conn, params=[client_type, job_type])
#     conn.close()
#     return df

# def generate_workflows(job_id: int, job_type: str, workflow_templates: pd.DataFrame):
#     # Insert generated workflows
#     conn = get_connection()
#     cursor = conn.cursor()
#     generated_workflows = workflow_templates.copy()
#     generated_workflows['JobID'] = job_id
#     generated_workflows['JobType'] = job_type
#     generated_workflows = generated_workflows[['JobID','JobType','Sort','Task','TaskDescription','Estimated']]

#     insert_query = """
#     INSERT INTO GeneratedWorkflows (JobID, JobType, Sort, Task, TaskDescription, EstimatedTime)
#     VALUES (?, ?, ?, ?, ?, ?)
#     """
#     for _, row in generated_workflows.iterrows():
#         cursor.execute(insert_query, row['JobID'], row['JobType'], row['Sort'], row['Task'], row['TaskDescription'], row['Estimated'])

#     conn.commit()
#     cursor.close()
#     conn.close()

# def fetch_tasks_for_job(job_id: int) -> pd.DataFrame:
#     conn = get_connection()
#     query = """
#     SELECT WorkflowID, Task, TaskDescription, EstimatedTime, ActualTime, Initials
#     FROM GeneratedWorkflows
#     WHERE JobID = ?
#     """
#     df = pd.read_sql(query, conn, params=[job_id])
#     conn.close()
#     return df

# def update_task(workflow_id: int, actual_time: float, initials: str):
#     conn = get_connection()
#     cursor = conn.cursor()
#     update_query = """
#     UPDATE GeneratedWorkflows
#     SET ActualTime = ?, Initials = ?
#     WHERE WorkflowID = ?
#     """
#     cursor.execute(update_query, actual_time, initials, workflow_id)
#     conn.commit()
#     cursor.close()
#     conn.close()

# def get_report():
#     conn = get_connection()
#     query = """
#     SELECT JobID, SUM(EstimatedTime) AS TotalEstimatedTime, SUM(ActualTime) AS TotalActualTime
#     FROM GeneratedWorkflows
#     GROUP BY JobID
#     """
#     df = pd.read_sql(query, conn)
#     conn.close()
#     return df
