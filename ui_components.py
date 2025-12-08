# ui_components.py
import streamlit as st
import jd_logic as llm

def render_sidebar():
    """Renders the settings sidebar."""
    st.sidebar.header("Settings")

    if "model_input" not in st.session_state:
        st.session_state.model_input = llm.DEFAULT_MODEL

    model_input = st.sidebar.text_input(
        "Model",
        value=st.session_state.model_input,
        key="model_input"
    )

    if st.sidebar.button("Configure LLM", key="sidebar_config_llm"):
        try:
            llm.configure_llm(model=model_input)
            st.sidebar.success(f"LLM configured using: {model_input}")
        except Exception as e:
            st.sidebar.error(f"Failed to configure LLM: {e}")

    st.sidebar.markdown("---")

def render_question_card(q, index):
    """
    Renders a question card using native Streamlit containers 
    to allow for interactive buttons and state management.
    """
    # 1. Create unique keys for state management
    # Use database ID if available, otherwise fallback to index (for unsaved previews)
    q_id = q.get('id', f"new_{index}")
    ans_key = f"answer_{q_id}"
    
    # 2. Visual Card Container
    with st.container(border=True):
        # --- Header Row: Meta Info ---
        col1, col2 = st.columns([3, 1])
        with col1:
            # Display Index and Skill
            skill_name = q.get('skill', 'General')
            st.markdown(f"**#{index}** • {skill_name}")
            
        with col2:
            # Display Question Type (Technical/Behavioral)
            q_type = q.get('qtype', 'General').upper()
            st.caption(f"{q_type}")
            
        # --- Question Text ---
        # Add a little spacing
        st.write(q.get('prompt'))
        
        # --- Interaction Area ---
        
        # Scenario A: The answer is already generated and stored in session state
        if ans_key in st.session_state:
            st.markdown("---")
            st.markdown("##### 💡 Sample Answer")
            
            answer_text = st.session_state[ans_key]
            
            # Check for empty/failed responses
            if answer_text and answer_text.strip():
                st.info(answer_text)
            else:
                st.error("⚠️ The LLM returned an empty response. Check your API Key and terminal logs.")

            # Close Button to clear the answer from view
            if st.button("Close", key=f"close_{q_id}"):
                del st.session_state[ans_key]
                st.rerun()

        # Scenario B: No answer yet (Show Generate Button)
        else:
            if st.button("Generate Answer ✨", key=f"gen_{q_id}"):
                # 1. Ensure connection
                llm.configure_llm()
                
                # 2. Show loading spinner while generating
                with st.spinner("Drafting a high-quality answer..."):
                    try:
                        # Call the logic layer
                        answer = llm.generate_answer(q.get('prompt'))
                        
                        # Save result to session state
                        st.session_state[ans_key] = answer
                        
                        # Reload to show the result (Scenario A)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Generation failed: {e}")