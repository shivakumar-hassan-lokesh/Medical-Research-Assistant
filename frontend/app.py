import streamlit as st
import requests
import uuid
import time
import os

from datetime import datetime

# ----------------------------
# PASSWORD PROTECTION
# ----------------------------
APP_PASSWORD = "medassist@group4"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align:center;'>🔐 MedAssist AI Login</h2>", unsafe_allow_html=True)
    password_input = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        if password_input == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")

    st.stop()



API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


# Page configuration
st.set_page_config(
    page_title="MedAssist AI - Research Assistant", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "MedAssist AI - Your intelligent medical research companion"
    }
)

# Load custom CSS
with open("frontend/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session states
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None
if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False
if "uploaded_files_list" not in st.session_state:
    st.session_state.uploaded_files_list = []
if "processing" not in st.session_state:
    st.session_state.processing = False
if "last_processed_message" not in st.session_state:
    st.session_state.last_processed_message = ""
if "message_processing" not in st.session_state:
    st.session_state.message_processing = False

# Create initial chat session
if st.session_state.current_chat is None:
    new_id = str(uuid.uuid4())[:8]
    st.session_state.chats[new_id] = {
        "messages": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "title": "New Research Session"
    }
    st.session_state.current_chat = new_id

# Sidebar
with st.sidebar:
    # Logo and branding
    st.markdown("""
        <div class="sidebar-header">
            <div class="logo-container">
                <span class="logo">🏥</span>
                <h2 class="brand-name">MedAssist AI</h2>
            </div>
            <p class="tagline">Intelligent Medical Research Assistant</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # New chat button
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("New Session", use_container_width=True, key="new_chat_btn"):
            new_id = str(uuid.uuid4())[:8]
            st.session_state.chats[new_id] = {
                "messages": [],
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "title": "New Research Session"
            }
            st.session_state.current_chat = new_id
            st.session_state.pdf_uploaded = False
            st.session_state.uploaded_files_list = []
            st.rerun()
    
    with col2:
        if st.button("Clear All", use_container_width=True, key="clear_btn"):
            st.session_state.chats = {}
            st.session_state.current_chat = None
            st.session_state.pdf_uploaded = False
            st.session_state.uploaded_files_list = []
            st.rerun()
    
    # Chat history
    st.markdown("<h3 class='sidebar-section-title'>Research History</h3>", unsafe_allow_html=True)
    
    if st.session_state.chats:
        for chat_id in reversed(list(st.session_state.chats.keys())):
            chat_data = st.session_state.chats[chat_id]
            is_active = chat_id == st.session_state.current_chat
            
            if st.button(
                f"{'🔵' if is_active else '⚪'} {chat_data['title'][:20]}...",
                key=f"chat_{chat_id}",
                use_container_width=True,
                help=f"Created: {chat_data['created_at']}"
            ):
                st.session_state.current_chat = chat_id
                # Check if this chat has uploaded files
                if chat_data["messages"]:
                    st.session_state.pdf_uploaded = True
                st.rerun()
    else:
        st.markdown("<p class='empty-state'>No research sessions yet</p>", unsafe_allow_html=True)
    
    # Stats section
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<h3 class='sidebar-section-title'> Session Stats</h3>", unsafe_allow_html=True)
    
    current_chat_data = st.session_state.chats.get(st.session_state.current_chat, {})
    messages_count = len(current_chat_data.get("messages", []))
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Messages", messages_count)
    with col2:
        st.metric("PDFs", len(st.session_state.uploaded_files_list))

# Main content area
main_container = st.container()

with main_container:
    # Header
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">
                <span class="gradient-text">Medical Research Assistant</span>
            </h1>
            <p class="subtitle">Upload medical PDFs and ask questions powered by advanced AI</p>
        </div>
    """, unsafe_allow_html=True)
    
    current_chat_id = st.session_state.current_chat
    
    # Upload section (shown when no PDFs uploaded)
    if not st.session_state.pdf_uploaded:
        st.markdown("""
            <div class="upload-section">
                <div class="upload-card">
                    <div class="upload-icon">📄</div>
                    <h2>Upload Medical Documents</h2>
                    <p class="upload-description">
                        Support for medical research papers, clinical reports, and scientific documents
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="pdf_uploader"
        )
        
        if uploaded_files:
            st.session_state.processing = True

            progress_bar = st.progress(0)
            status_text = st.empty()

            st.session_state.uploaded_files_list = []

            for idx, file in enumerate(uploaded_files):
                status_text.text(f"Processing {file.name}...")
                progress_bar.progress((idx + 1) / len(uploaded_files))

                try:
                    files = {"file": (file.name, file, "application/pdf")}
                    response = requests.post(f"{API_URL}/upload", files=files)

                    # Parse backend response
                    resp = response.json()

                    # ❌ Backend rejected PDF → show message and stop
                    if resp.get("status") == "error":
                        st.error(f"❌ {file.name} is NOT a medical document.")
                        st.session_state.processing = False
                        st.stop()

                    # ✔ Backend accepted PDF
                    st.session_state.uploaded_files_list.append(file.name)

                except Exception as e:
                    st.error(f"Error uploading {file.name}: {str(e)}")
                    st.stop()

            status_text.empty()
            progress_bar.empty()

            st.success(f"Successfully processed {len(st.session_state.uploaded_files_list)} PDF(s)")
            st.session_state.pdf_uploaded = True
            st.session_state.processing = False
            st.rerun()

        
        # Features showcase
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">🤖</div>
                    <h3>AI-Powered Analysis</h3>
                    <p>Advanced language models analyze your medical documents with precision</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">🔍</div>
                    <h3>Smart Search</h3>
                    <p>Intelligent retrieval system finds relevant information instantly</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">✨</div>
                    <h3>Validated Answers</h3>
                    <p>Multi-agent validation ensures accurate and safe medical information</p>
                </div>
            """, unsafe_allow_html=True)
    
    # Chat interface (shown after PDFs uploaded)
    else:
        # Document status bar
        if st.session_state.uploaded_files_list:
            st.markdown("""
                <div class="document-status">
                    <span class="status-icon"></span>
                    <span class="status-text">Active Documents: {}</span>
                </div>
            """.format(", ".join(st.session_state.uploaded_files_list[:3])), unsafe_allow_html=True)
        
        # Chat messages container
        chat_container = st.container()
        
        with chat_container:
            messages = st.session_state.chats[current_chat_id]["messages"]
            
            if not messages:
                st.markdown("""
                    <div class="empty-chat">
                        <div class="empty-chat-icon">💬</div>
                        <h3>Start Your Research</h3>
                        <p>Ask any question about your uploaded medical documents</p>
                        <div class="suggested-questions">
                            <p class="suggestions-title">Try asking:</p>
                            <ul>
                                <li>What are the key findings in this research?</li>
                                <li>Explain the treatment protocols mentioned</li>
                                <li>What are the potential side effects discussed?</li>
                                <li>Summarize the clinical trial results</li>
                            </ul>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                for msg in messages:
                    if msg["role"] == "user":
                        st.markdown(f"""
                            <div class="message-container user-message-container">
                                <div class="message user-message">
                                    <div class="message-avatar user-avatar">👤</div>
                                    <div class="message-content">
                                        <div class="message-text">{msg['content']}</div>
                                        <div class="message-time">{msg.get('timestamp', '')}</div>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="message-container assistant-message-container">
                                <div class="message assistant-message">
                                    <div class="message-avatar assistant-avatar">🤖</div>
                                    <div class="message-content">
                                        <div class="message-text">{msg['content']}</div>
                                        <div class="message-time">{msg.get('timestamp', '')}</div>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
        
        # Input section
        st.markdown("<div class='chat-input-section'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([6, 1])
        
        with col1:
            # Create unique key for input field to prevent state issues
            input_key = f"chat_input_{current_chat_id}_{len(messages)}"
            user_input = st.text_input(
                "Ask a question",
                key=input_key,
                placeholder="Type your medical question here...",
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.button("Send", key="send_btn", use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Process input - Fixed to prevent duplicate messages
        if send_button and user_input.strip() and not st.session_state.message_processing:
            # Set processing flag to prevent duplicates
            st.session_state.message_processing = True
            
            # Check if this is a new message (prevent duplicates)
            current_message = user_input.strip()
            
            # Only process if it's a different message
            if current_message != st.session_state.last_processed_message:
                # Add user message
                timestamp = datetime.now().strftime("%H:%M")
                st.session_state.chats[current_chat_id]["messages"].append({
                    "role": "user",
                    "content": current_message,
                    "timestamp": timestamp
                })
                
                # Update chat title if it's the first message
                if len(st.session_state.chats[current_chat_id]["messages"]) == 1:
                    st.session_state.chats[current_chat_id]["title"] = current_message[:30]
                
                # Show thinking animation
                with st.spinner(" Analyzing medical documents..."):
                    try:
                        response = requests.get(f"{API_URL}/chat", params={"q": current_message}, timeout=30)
                        response_data = response.json()
                        assistant_reply = response_data.get("final", "I couldn't process your request. Please try again.")
                    except requests.exceptions.Timeout:
                        assistant_reply = "The request timed out. Please try again."
                    except Exception as e:
                        assistant_reply = f"Error: Unable to connect to the backend service. Please ensure the FastAPI server is running."
                
                # Add assistant response only once
                st.session_state.chats[current_chat_id]["messages"].append({
                    "role": "assistant",
                    "content": assistant_reply,
                    "timestamp": timestamp
                })
                
                # Store the last processed message
                st.session_state.last_processed_message = current_message
            
            # Reset processing flag
            st.session_state.message_processing = False
            
            # Clear and rerun
            time.sleep(0.1)  # Small delay to ensure state is updated
            st.rerun()

# Footer
st.markdown("""
    <div class="footer">
        <p>Powered by Advanced AI • Built for Medical Research • © 2024 MedAssist AI</p>
    </div>
""", unsafe_allow_html=True)