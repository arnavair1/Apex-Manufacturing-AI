import streamlit as st

from src.agents.groq_agent import run_agent


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Apex Manufacturing AI",
    page_icon="🏭",
    layout="wide",
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("🏭 Apex Manufacturing AI")

st.markdown(
    """
    ### Manufacturing Intelligence Platform

    Ask questions about production, machines, failures,
    downtime, quality, sensors, maintenance, and
    manufacturing operations.
    """
)


st.divider()


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.header("Apex Manufacturing AI")

    st.markdown(
        """
        **AI-powered manufacturing intelligence**

        This system combines:

        - 📊 Manufacturing analytics
        - 🤖 Groq AI
        - 🧠 Machine learning
        - 📚 RAG knowledge retrieval
        - 🔧 Manufacturing tools
        - 🗄️ SQLite database
        """
    )

    st.divider()

    st.subheader("Quick Questions")

    if st.button(
        "Which machines need attention?",
        use_container_width=True,
    ):

        st.session_state.question = (
            "Which machines need attention?"
        )


    if st.button(
        "What is the overall production efficiency?",
        use_container_width=True,
    ):

        st.session_state.question = (
            "What is the overall production efficiency?"
        )


    if st.button(
        "Investigate MCH-004-01-01",
        use_container_width=True,
    ):

        st.session_state.question = (
            "Investigate MCH-004-01-01"
        )


    if st.button(
        "What should we check when a machine has high vibration?",
        use_container_width=True,
    ):

        st.session_state.question = (
            "What should we check when a machine has high vibration?"
        )


# ---------------------------------------------------------
# QUESTION INPUT
# ---------------------------------------------------------

if "question" not in st.session_state:

    st.session_state.question = ""


question = st.text_area(
    "Ask Apex AI",
    value=st.session_state.question,
    height=130,
    placeholder=(
        "Example: Which machines need attention?"
    ),
)


# ---------------------------------------------------------
# ASK BUTTON
# ---------------------------------------------------------

if st.button(
    "🚀 Ask Apex AI",
    type="primary",
    use_container_width=True,
):

    question = question.strip()


    if not question:

        st.warning(
            "Please enter a manufacturing question."
        )

    else:

        with st.spinner(
            "Apex AI is analyzing the manufacturing data..."
        ):

            try:

                answer = run_agent(question)

                st.session_state.question = question

                st.divider()

                st.subheader("🤖 AI Response")

                st.markdown(answer)

            except Exception as error:

                st.error(
                    "The AI agent encountered an error."
                )

                st.code(
                    str(error)
                )


# ---------------------------------------------------------
# INFORMATION SECTION
# ---------------------------------------------------------

st.divider()

st.subheader("System Capabilities")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Manufacturing Data",
        "12 datasets",
    )


with col2:

    st.metric(
        "Machines",
        "60",
    )


with col3:

    st.metric(
        "ML",
        "Failure Prediction",
    )


with col4:

    st.metric(
        "AI",
        "Groq",
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "Apex Manufacturing AI • Analytics • ML • RAG • Groq"
)