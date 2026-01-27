import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from ai_agent import DoctorAppointmentAgent

# --------------------------------------------------
# LOAD AGENT ONCE
# --------------------------------------------------

@st.cache_resource
def load_workflow():
    agent = DoctorAppointmentAgent()
    return agent.workflow()

app = load_workflow()

# --------------------------------------------------
# UI
# --------------------------------------------------

st.set_page_config(page_title="Doctor Appointment AI", layout="centered")
st.title("🩺 Doctor Appointment AI Assistant")

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "pending_state" not in st.session_state:
    st.session_state.pending_state = None

# --------------------------------------------------
# FORM
# --------------------------------------------------

with st.form("appointment_form"):
    user_id = st.text_input("Enter your Identification Number")
    user_query = st.text_input("How can I help you today?")
    submitted = st.form_submit_button("Submit")

# --------------------------------------------------
# HANDLE SUBMISSION
# --------------------------------------------------

# --------------------------------------------------
# HANDLE SUBMISSION
# --------------------------------------------------

if submitted:
    clean_id = user_id.strip()
    clean_query = user_query.strip()

    # ✅ Correct validation
    if not clean_id.isdigit() or len(clean_id) not in (7, 8):
        st.error("Identification Number must be numeric (7 or 8 digits).")

    elif not clean_query:
        st.error("Please enter your query.")

    else:
        initial_state = {
            "messages": [HumanMessage(content=clean_query)],
            "id_number": int(clean_id),
            "query": "",
            "current_reasoning": "",
        }

        with st.spinner("Thinking..."):
            result = app.invoke(initial_state)

        st.session_state.conversation = result["messages"]
        st.session_state.pending_state = result

# --------------------------------------------------
# DISPLAY CONVERSATION
# --------------------------------------------------

if st.session_state.conversation:
    st.subheader("Conversation")

    for msg in st.session_state.conversation:
        if isinstance(msg, HumanMessage):
            st.markdown(f"**🧑 You:** {msg.content}")
        elif isinstance(msg, AIMessage):
            st.markdown(f"**🤖 Assistant:** {msg.content}")

# --------------------------------------------------
# HUMAN-IN-THE-LOOP
# --------------------------------------------------

if st.session_state.pending_state:
    last_message = st.session_state.pending_state["messages"][-1].content.lower()

    if any(word in last_message for word in ["book", "appointment", "scheduled"]):
        st.warning("⚠️ Please confirm before finalizing the appointment")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Confirm Appointment"):
                st.success("Appointment confirmed successfully!")
                st.session_state.pending_state = None

        with col2:
            if st.button("❌ Cancel"):
                st.info("Appointment cancelled.")
                st.session_state.pending_state = None
