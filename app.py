# app.py
import streamlit as st
import pandas as pd
from db_utils import (
    get_client_details,
    get_connection, 
    check_workflow_exists_for_job,
    generate_workflow_for_job,
    get_generated_workflows_for_job,
    update_task_in_workflow,
    get_reporting_data)


#     get_workflow_templates, 
#     generate_workflows,
#     fetch_tasks_for_job,
#     update_task,
#     get_report
# )

# st.title("Client Workflow Management")

# # 1. User input for JobID
# job_id = st.number_input("Enter JobID:", min_value=1, value=202411)

# if st.button("Fetch Client Details"):
#     client_details = get_client_details(job_id)
#     if len(client_details) == 0:
#         st.error("No client found for this JobID.")
#     else:
#         st.write("Client Details:")
#         st.write(client_details)
#         client_type = client_details['ClientType'].iloc[0]
#         job_type = client_details['JobType'].iloc[0]
        
#         # 2. Generate Workflow if needed
#         st.markdown("### Generate Workflow")
#         if st.button("Generate Workflow"):
#             workflow_templates = get_workflow_templates(client_type, job_type)
#             if len(workflow_templates) == 0:
#                 st.error("No workflow templates found for this client/job type.")
#             else:
#                 generate_workflows(job_id, job_type, workflow_templates)
#                 st.success("Workflow generated successfully!")

# if st.button("Fetch Tasks"):
#     tasks = fetch_tasks_for_job(job_id)
#     if len(tasks) > 0:
#         st.write("Tasks for JobID:", job_id)
#         st.dataframe(tasks)
#     else:
#         st.warning("No tasks found. Make sure you've generated the workflows.")

# # 3. Update a specific task
# st.markdown("### Update a Specific Task")
# workflow_id_to_update = st.number_input("WorkflowID to Update:", min_value=1, value=1)
# actual_time_input = st.number_input("Actual Time:", min_value=0.0, value=10.0, step=1.0)
# initials_input = st.text_input("Initials:", value="AC")

# if st.button("Update Task"):
#     update_task(workflow_id_to_update, actual_time_input, initials_input)
#     st.success("Task updated successfully!")
# # Re-fetch the tasks to show the updated table instantly
#     updated_tasks = fetch_tasks_for_job(job_id)
#     st.write("Updated Tasks:")
#     st.dataframe(updated_tasks)

# # 4. Reporting
# st.markdown("### Reporting / Descriptive Stats")
# if st.button("Show Report"):
#     report_df = get_report()
#     st.write("Report on Total Estimated and Actual Times per Job:")
#     st.dataframe(report_df)


st.title("Client Workflow Management App")

# Sidebar to select job_id
job_id = st.sidebar.number_input("Enter JobID:", value=202411, min_value=1, step=1)

# Create Tabs
tab1, tab2, tab3 = st.tabs(["Client Details", "Workflow Management", "Reporting / Descriptive Stats"])

# -------------------------------------------
# Tab 1: Client Details
# -------------------------------------------
with tab1:
    st.header("Client Details")
    conn = get_connection()
    if st.button("Fetch Client Details"):
        client_df = get_client_details(conn, job_id)
        if len(client_df) == 0:
            st.warning("No client details found for this JobID.")
        else:
            st.dataframe(client_df)

    # If you want filtering options, you can add selectors here
    # Example filter by ClientType or CompanyName:
    # client_type_filter = st.text_input("Filter by ClientType:")
    # if client_type_filter:
    #     # You could refetch or filter the already fetched df if stored in a session state
    #     pass

# -------------------------------------------
# Tab 2: Workflow Management
# -------------------------------------------
with tab2:
    st.header("Workflow Management")

    # Check if workflow already exists for this job_id
    conn = get_connection()
    workflow_exists = check_workflow_exists_for_job(conn, job_id)

    if not workflow_exists:
        st.info("No workflow generated for this JobID.")
        if st.button("Generate Workflow"):
            generate_workflow_for_job(conn, job_id)
            # After generation, re-check and display
            workflow_exists = check_workflow_exists_for_job(conn, job_id)
    else:
        st.success("Workflow already generated for this JobID.")

    # Display the tasks if workflow exists
    if workflow_exists:
        tasks_df = get_generated_workflows_for_job(conn, job_id)
        st.write("Generated Workflow Tasks:")
        st.dataframe(tasks_df)

        # Update a specific task
        st.markdown("### Update a Specific Task")
        workflow_id_to_update = st.number_input("WorkflowID to Update:", min_value=1, value=1)
        actual_time_input = st.number_input("Actual Time:", min_value=0.0, value=10.0, step=1.0)
        initials_input = st.text_input("Initials:", value="AC")

        if st.button("Update Task"):
            update_task_in_workflow(conn, workflow_id_to_update, actual_time_input, initials_input)
            st.success("Task updated successfully!")
            # Re-fetch the tasks to show updated data
            tasks_df = get_generated_workflows_for_job(conn, job_id)
            st.dataframe(tasks_df)

# -------------------------------------------
# Tab 3: Reporting / Descriptive Stats
# -------------------------------------------
with tab3:
    st.header("Reporting / Descriptive Stats")

    conn = get_connection()
    report_df = get_reporting_data(conn)
    st.write("Report on Total Estimated and Actual Times per Job:")
    st.dataframe(report_df)

    # If you want to filter on specific job_id or do additional descriptive stats:
    # For example, let user select a jobID from the report_df to view details
    selected_job_id = st.selectbox("Select JobID to view details:", report_df['JobID'].unique())
    selected_job_data = report_df[report_df['JobID'] == selected_job_id]
    st.write("Selected Job Report:")
    st.dataframe(selected_job_data)