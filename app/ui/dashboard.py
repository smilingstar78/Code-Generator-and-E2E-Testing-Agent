import streamlit as st
import time
from app.agent.graph import build_graph
from app.agent.state import AgentState

st.set_page_config(
    page_title="Autonomous Code & E2E Testing Agent",
    page_icon="⚡",
    layout="wide"
)

# Custom Dark Theme Styling with Amber Accents
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    h1, h2, h3 { color: #F59E0B !important; }
    .stButton>button {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: black;
        font-weight: bold;
        border: none;
        border-radius: 6px;
    }
    .status-card {
        background-color: #1E293B;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #F59E0B;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Autonomous Code Generation & E2E Testing Agent")
st.caption("Multi-Agent LangGraph System with Docker Ephemeral Sandbox Verification")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. System Specification Prompt")
    user_prompt = st.text_area(
        "Enter instructions for the Autonomous Agent:",
        value="Create a Python math utilities module with functions for factorial, prime checking, and fibonacci series. Include exhaustive Pytest unit tests.",
        height=150
    )
    run_btn = st.button("🚀 Execute Autonomous Pipeline", use_container_width=True)

# Save result state across Streamlit re-renders
if run_btn:
    with col2:
        st.subheader("2. Agent Workflow Execution")
        status_box = st.empty()

        initial_state: AgentState = {
            "specification": user_prompt,
            "file_manifest": [],
            "files": {},
            "test_logs": None,
            "execution_exit_code": 1,
            "iterations": 0,
            "is_complete": False,
            "syntax_errors": []
        }

        status_box.info("🧠 Running Autonomous Agent Workflow (Architect ➔ Coder ➔ AST ➔ Docker)...")
        graph_app = build_graph()
        
        start_time = time.time()
        final_state = graph_app.invoke(initial_state)
        elapsed = round(time.time() - start_time, 2)

        # Store in session state so dropdown selections don't erase data
        st.session_state["final_state"] = final_state
        st.session_state["elapsed"] = elapsed

if "final_state" in st.session_state:
    final_state = st.session_state["final_state"]
    elapsed = st.session_state.get("elapsed", 0)
    
    exit_code = final_state.get("execution_exit_code", 1)
    iterations = final_state.get("iterations", 0)

    with col2:
        if not run_btn:
            st.subheader("2. Agent Workflow Execution")
        if exit_code == 0:
            st.success(f"✅ PASSED inside Docker in {elapsed}s (Fixer Loop Iterations: {iterations})")
        else:
            st.error(f"❌ FAILED after {iterations} iterations.")

    st.markdown("---")
    st.subheader("3. Inspection Workspace")
    
    tab_files, tab_logs = st.tabs(["📁 Generated File Workspace", "🐳 Docker Pytest Logs"])

    with tab_files:
        files = final_state.get("files", {})
        if files:
            selected_file = st.selectbox("Select file to view code:", list(files.keys()), key="file_selector")
            st.code(files[selected_file], language="python")
        else:
            st.warning("No files were generated.")

    with tab_logs:
        st.code(final_state.get("test_logs", "No logs recorded"), language="text")