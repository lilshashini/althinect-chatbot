import streamlit as st
import uuid
from datetime import datetime
from typing import List, Dict, Any
from langchain_core.messages import AIMessage, HumanMessage

class SessionManager:
    @staticmethod
    def initialize_sessions():
        """Initialize session state"""
        if "sessions" not in st.session_state:
            st.session_state.sessions = {}
        
        if "active_session_id" not in st.session_state:
            session_id = str(uuid.uuid4())
            st.session_state.sessions[session_id] = {
                "title": "Welcome Chat",
                "messages": [
                    AIMessage(content="Hello! I'm your Production Analytics Bot.")
                ],
                "created_at": datetime.now()
            }
            st.session_state.active_session_id = session_id
    
    @staticmethod
    def create_new_session():
        """Create new chat session"""
        session_id = str(uuid.uuid4())
        st.session_state.sessions[session_id] = {
            "title": "New Chat",
            "messages": [
                AIMessage(content="Hello! How can I help you analyze your production data?")
            ],
            "created_at": datetime.now()
        }
        st.session_state.active_session_id = session_id
        st.rerun()
    
    @staticmethod
    def add_message(message):
        """Add message to current session"""
        if st.session_state.active_session_id in st.session_state.sessions:
            current_messages = st.session_state.sessions[st.session_state.active_session_id]["messages"]
            current_messages.append(message)
            
            # Trim to last 10 messages
            if len(current_messages) > 10:
                st.session_state.sessions[st.session_state.active_session_id]["messages"] = current_messages[-10:]