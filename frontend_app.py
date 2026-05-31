import streamlit as st
import requests
import json
from datetime import datetime
import time
import os
from typing import Optional

# Set page config
st.set_page_config(
    page_title="AgniLex AI",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for beautiful UI (default dark theme)
def load_custom_css():
    st.markdown("""
    <style>
        * {
            margin: 0;
            padding: 0;
        }
        
        body {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .main {
            background: #0f1419;
            color: #e0e0e0;
        }
        
        .stApp {
            background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: rgba(20, 25, 40, 0.95);
            backdrop-filter: blur(10px);
        }
        
        /* Chat bubbles */
        .chat-bubble {
            padding: 12px 16px;
            border-radius: 12px;
            margin: 8px 0;
            word-wrap: break-word;
            animation: fadeIn 0.3s ease-in;
        }
        
        .user-bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
            max-width: 70%;
            text-align: right;
        }
        
        .assistant-bubble {
            background: rgba(100, 120, 160, 0.2);
            color: #e0e0e0;
            border: 1px solid rgba(100, 150, 200, 0.3);
            max-width: 85%;
        }
        
        .chat-bubble small {
            color: rgba(255, 255, 255, 0.6);
            font-size: 11px;
            display: block;
        }
        
        .assistant-bubble small {
            color: rgba(224, 224, 224, 0.5);
        }
        
        /* Cards */
        .card {
            background: rgba(30, 40, 60, 0.8);
            border: 1px solid rgba(100, 150, 200, 0.2);
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            background: rgba(40, 50, 80, 0.9);
            border-color: rgba(150, 200, 255, 0.4);
            transform: translateY(-2px);
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {
            background: rgba(30, 40, 60, 0.8) !important;
            border: 1px solid rgba(100, 150, 200, 0.3) !important;
            color: #e0e0e0 !important;
            border-radius: 8px !important;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #fff;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        /* Animations */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .typing-animation {
            display: inline-block;
        }
        
        .typing-animation::after {
            content: '';
            animation: typing 1.5s infinite;
        }
        
        @keyframes typing {
            0%, 20% { content: ''; }
            40% { content: '.'; }
            60% { content: '..'; }
            80%, 100% { content: '...'; }
        }
        
        /* Footer */
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(20, 25, 40, 0.95);
            border-top: 1px solid rgba(100, 150, 200, 0.2);
            padding: 12px 24px;
            text-align: center;
            font-size: 14px;
            color: #e0e0e0;
            z-index: 999;
        }
        
        .footer a {
            color: #667eea;
            text-decoration: none;
        }
        
        .footer a:hover {
            color: #764ba2;
            text-decoration: underline;
        }
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

# API configuration
API_BASE_URL = "http://localhost:8000/api"

# Session state
def init_session_state():
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'
    if 'current_conversation_id' not in st.session_state:
        st.session_state.current_conversation_id = None
    if 'messages_cache' not in st.session_state:
        st.session_state.messages_cache = {}

init_session_state()

# API Helper Functions
def make_request(method: str, endpoint: str, **kwargs) -> dict:
    """Make API request with error handling"""
    headers = kwargs.pop('headers', {})
    if st.session_state.access_token:
        headers['Authorization'] = f'Bearer {st.session_state.access_token}'
    
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == 'GET':
            response = requests.get(url, headers=headers, **kwargs)
        elif method == 'POST':
            response = requests.post(url, headers=headers, **kwargs)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, **kwargs)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, **kwargs)
        else:
            return {'error': 'Invalid method'}
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            return {'error': response.text}
    except Exception as e:
        return {'error': str(e)}

# Footer
def render_footer():
    st.markdown("""
    <div class="footer">
        Made by <a href="https://sourishdeyportfolio.vercel.app/" target="_blank">Sourish  Dey</a>
    </div>
    """, unsafe_allow_html=True)

# Pages
def login_page():
    """Login page"""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown("## 🔥 AgniLex AI")
        st.markdown("---")
        
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            if st.button("Login", use_container_width=True):
                if username and password:
                    response = make_request(
                        'POST',
                        '/auth/login',
                        json={'username': username, 'password': password}
                    )
                    
                    if 'error' not in response:
                        st.session_state.access_token = response['access_token']
                        st.session_state.user_info = response['user']
                        
                        if response['user']['role'] == 'admin':
                            st.session_state.current_page = 'admin_dashboard'
                        else:
                            st.session_state.current_page = 'chat'
                        
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(response['error'])
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            if st.button("Don't have an account? Sign up", use_container_width=True):
                st.session_state.current_page = 'signup'
                st.rerun()

def signup_page():
    """Signup page"""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown("## 📝 Create Account")
        st.markdown("---")
        
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Create a password (min 8 chars)")
            confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
            
            if st.button("Sign Up", use_container_width=True):
                if not all([username, email, password, confirm]):
                    st.error("All fields are required")
                elif password != confirm:
                    st.error("Passwords don't match")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    response = make_request(
                        'POST',
                        '/auth/signup',
                        json={
                            'username': username,
                            'email': email,
                            'password': password
                        }
                    )
                    
                    if 'error' not in response:
                        st.success("Account created! Please login.")
                        st.session_state.current_page = 'login'
                        st.rerun()
                    else:
                        st.error(response['error'])
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            if st.button("Already have an account? Login", use_container_width=True):
                st.session_state.current_page = 'login'
                st.rerun()

def chat_page():
    """Main chat interface"""
    st.title("🔥 AgniLex AI")
    
    # Search conversations
    search_query = st.sidebar.text_input("🔍 Search conversations", value="", placeholder="Search...")
    
    # Sidebar for conversations
    with st.sidebar:
        st.header("Conversations")
        
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.current_conversation_id = None
            st.rerun()
        
        # Get conversations
        convs = make_request('GET', '/conversations')
        if 'error' not in convs:
            # Filter conversations by search query
            filtered_convs = [c for c in convs if search_query.lower() in c['title'].lower()] if search_query else convs
            
            if not filtered_convs:
                st.caption("No conversations found")
            
            for conv in filtered_convs:
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(f"📝 {conv['title'][:20]}", key=f"conv_{conv['id']}", use_container_width=True):
                        st.session_state.current_conversation_id = conv['id']
                        st.rerun()
                with col2:
                    if st.button("✏️", key=f"rename_{conv['id']}"):
                        st.session_state.rename_conv_id = conv['id']
                        st.session_state.rename_conv_title = conv['title']
                        st.rerun()
        
        st.divider()
        
        # Rename conversation modal
        if 'rename_conv_id' in st.session_state and st.session_state.rename_conv_id:
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("**Rename Chat**")
                new_title = st.text_input("New title", value=st.session_state.get('rename_conv_title', ''))
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    if st.button("Save", use_container_width=True):
                        resp = make_request(
                            'PUT',
                            f"/conversations/{st.session_state.rename_conv_id}",
                            json={"title": new_title[:200]}
                        )
                        if 'error' not in resp:
                            st.success("Renamed!")
                            del st.session_state.rename_conv_id
                            del st.session_state.rename_conv_title
                            st.rerun()
                        else:
                            st.error(resp['error'])
                with col_b:
                    if st.button("Cancel", use_container_width=True):
                        del st.session_state.rename_conv_id
                        del st.session_state.rename_conv_title
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        
        st.divider()
        
        # Quick prompts
        st.markdown("### Quick Prompts")
        quick_prompts = [
            "How do I reset my password?",
            "What is your return policy?",
            "Contact support",
            "Help with my order"
        ]
        for prompt in quick_prompts:
            if st.button(f"💬 {prompt[:18]}...", key=f"quick_{prompt[:8].replace(' ', '_')}", use_container_width=True):
                st.session_state.quick_prompt = prompt
                st.rerun()
        
        st.divider()
        
        # Delete chat (end-to-end)
        if st.session_state.current_conversation_id:
            st.subheader("🗑️ Delete Chat")
            st.caption("This deletes the selected conversation permanently.")
            confirm_text = st.text_input("Type DELETE to confirm", value="")
            delete_btn = st.button("Delete selected chat", use_container_width=True)
            if delete_btn:
                if confirm_text.strip() == "DELETE":
                    del_resp = make_request(
                        "DELETE",
                        f"/conversations/{st.session_state.current_conversation_id}"
                    )
                    if "error" not in del_resp:
                        st.success("Chat deleted")
                        st.session_state.current_conversation_id = None
                        st.session_state.messages_cache = {}
                        st.rerun()
                    else:
                        st.error(del_resp["error"])
                else:
                    st.error("Confirmation failed. Type DELETE to confirm.")
        
        st.divider()
        
        # Additional options
        if st.button("📄 Knowledge Base", use_container_width=True):
            st.session_state.current_page = 'documents'
            st.rerun()
        
        if st.button("📊 Analytics", use_container_width=True):
            st.session_state.current_page = 'analytics'
            st.rerun()
        
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.current_page = 'settings'
            st.rerun()
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.access_token = None
            st.session_state.user_info = None
            st.session_state.current_page = 'login'
            st.rerun()
    
    # Main chat area
    col1, col2 = st.columns([1, 3])
    
    with col2:
        # Chat history
        if st.session_state.current_conversation_id:
            conv_data = make_request('GET', f'/conversations/{st.session_state.current_conversation_id}')
            if 'error' not in conv_data:
                st.markdown(f"## {conv_data['title']}")
                
                # Sentiment indicator
                if conv_data['messages']:
                    last_msg = conv_data['messages'][-1]
                    if last_msg['sender'] == 'assistant':
                        sentiment_resp = make_request('GET', '/analytics')
                        if 'error' not in sentiment_resp:
                            sentiment = sentiment_resp.get('sentiment', 'neutral')
                            st.caption(f"Current sentiment: {sentiment.upper()}")
                
                # Export button
                if st.button("📥 Export Chat"):
                    chat_text = "\n".join([f"{msg['sender'].upper()}: {msg['content']}" for msg in conv_data['messages']])
                    st.session_state.export_chat_data = chat_text
                    st.session_state.export_chat_name = f"chat_{conv_data['id']}.txt"
                
                if 'export_chat_data' in st.session_state:
                    st.download_button(
                        label="Download as TXT",
                        data=st.session_state.export_chat_data,
                        file_name=st.session_state.export_chat_name,
                        mime="text/plain"
                    )
                
                st.divider()
                
                # Display messages with timestamps
                for msg in conv_data['messages']:
                    timestamp = msg.get('timestamp', '')[:16].replace('T', ' ')
                    if msg['sender'] == 'user':
                        st.markdown(f'<div class="chat-bubble user-bubble">{msg["content"]}<br><small>{timestamp}</small></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-bubble assistant-bubble">{msg["content"]}<br><small>{timestamp}</small></div>', unsafe_allow_html=True)
        
        # Input area
        st.divider()
        
        # Check if we need to clear input (after message sent)
        clear_input = st.session_state.pop('clear_message_input', False) if 'clear_message_input' in st.session_state else False
        
        # Use quick prompt if set
        default_value = ""
        if 'quick_prompt' in st.session_state:
            default_value = st.session_state.pop('quick_prompt')
        
        message = st.text_area("Your message:", value=default_value, height=100)
        
        if message:
            st.caption(f"Characters: {len(message)}")
        
        col_a, col_b, col_c = st.columns([3, 1, 1])
        
        with col_b:
            if st.button("Send", use_container_width=True):
                if message:
                    with st.spinner("AI is thinking..."):
                        response = make_request(
                            'POST',
                            '/chat',
                            json={
                                'message': message,
                                'conversation_id': st.session_state.current_conversation_id
                            }
                        )
                        
                        if 'error' not in response:
                            st.session_state.current_conversation_id = response['conversation_id']
                            st.session_state.clear_message_input = True  # Flag to clear on next run
                            st.success("Message sent!")
                            st.rerun()
                        else:
                            st.error(response['error'])
    
    render_footer()

def documents_page():
    """Document upload and management"""
    st.title("📄 Knowledge Base")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Upload Documents")
        
        uploaded_file = st.file_uploader(
            "Upload PDF, DOCX, or TXT files",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=False
        )
        
        if uploaded_file:
            if st.button("Upload & Process", use_container_width=True):
                with st.spinner("Processing document..."):
                    files = {'file': (uploaded_file.name, uploaded_file.getbuffer())}
                    
                    headers = {'Authorization': f'Bearer {st.session_state.access_token}'}
                    response = requests.post(
                        f"{API_BASE_URL}/upload",
                        files=files,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"✅ {data['filename']} processed successfully!")
                        st.info(f"Created {data['chunks_created']} text chunks for search")
                    else:
                        st.error("Upload failed")
    
    with col2:
        st.write("")
    
    st.divider()
    
    # List documents
    st.header("Your Documents")
    
    docs = make_request('GET', '/documents')
    if 'error' not in docs:
        if docs:
            cols = st.columns([3, 1, 1, 1])
            with cols[0]:
                st.write("**Filename**")
            with cols[1]:
                st.write("**Type**")
            with cols[2]:
                st.write("**Status**")
            with cols[3]:
                st.write("**Action**")
            
            st.divider()
            
            for doc in docs:
                cols = st.columns([3, 1, 1, 1])
                with cols[0]:
                    st.write(doc['filename'])
                with cols[1]:
                    st.write(doc['file_type'].upper())
                with cols[2]:
                    if doc['status'] == 'completed':
                        st.success(doc['status'])
                    else:
                        st.info(doc['status'])
                with cols[3]:
                    if st.button("🗑️", key=f"delete_{doc['id']}"):
                        make_request('DELETE', f'/documents/{doc["id"]}')
                        st.success("Deleted!")
                        st.rerun()
        else:
            st.info("No documents yet. Upload one to get started!")
    
    st.divider()
    
    if st.button("⬅️ Back to Chat"):
        st.session_state.current_page = 'chat'
        st.rerun()
    
    render_footer()

def analytics_page():
    """Analytics dashboard"""
    st.title("📊 Analytics Dashboard")
    
    analytics = make_request('GET', '/analytics')
    
    if 'error' not in analytics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Queries", analytics['total_queries'], "📨")
        with col2:
            st.metric("Conversations", analytics['total_conversations'], "💬")
        with col3:
            st.metric("Documents", analytics['total_documents'], "📄")
        with col4:
            st.metric("Sentiment", analytics['sentiment'].upper(), "😊")
        
        st.divider()
        
        st.subheader("Detailed Analytics")
        st.write(f"**Average Response Latency:** {analytics['average_latency']:.2f}ms")
        st.write(f"**Account Status:** {'Active' if analytics['active'] else 'Inactive'}")
    
    st.divider()
    
    if st.button("⬅️ Back to Chat"):
        st.session_state.current_page = 'chat'
        st.rerun()
    
    render_footer()

def settings_page():
    """User settings and password change"""
    st.title("⚙️ Settings")
    
    # User info
    st.header("Account Information")
    if st.session_state.user_info:
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Username:** {st.session_state.user_info['username']}")
        with col2:
            st.write(f"**Email:** {st.session_state.user_info['email']}")
    
    st.divider()
    
    # Change password
    st.header("Change Password")
    
    with st.form("change_password_form"):
        current_pwd = st.text_input("Current Password", type="password")
        new_pwd = st.text_input("New Password", type="password")
        confirm_pwd = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("Change Password", use_container_width=True)
        
        if submitted:
            if not all([current_pwd, new_pwd, confirm_pwd]):
                st.error("All fields are required")
            elif len(new_pwd) < 8:
                st.error("New password must be at least 8 characters")
            elif new_pwd != confirm_pwd:
                st.error("Passwords don't match")
            else:
                response = make_request(
                    'POST',
                    '/auth/change-password',
                    json={
                        'current_password': current_pwd,
                        'new_password': new_pwd,
                        'confirm_password': confirm_pwd
                    }
                )
                
                if 'error' not in response:
                    st.success("Password changed successfully!")
                else:
                    st.error(response['error'])
    
    st.divider()
    
    if st.button("⬅️ Back to Chat"):
        st.session_state.current_page = 'chat'
        st.rerun()
    
    render_footer()

def admin_dashboard():
    """Admin dashboard"""
    st.title("👨‍💼 Admin Dashboard")
    
    # Check if user is admin
    if not st.session_state.user_info or st.session_state.user_info['role'] != 'admin':
        st.error("Admin access required")
        if st.button("Login as Admin"):
            st.session_state.current_page = 'login'
            st.rerun()
        return
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Statistics", "👥 Users", "💬 Conversations", "📝 Workflows"])
    
    with tab1:
        st.header("Platform Statistics")
        stats = make_request('GET', '/admin/statistics')
        
        if 'error' not in stats:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Users", stats['total_users'], "👥")
            with col2:
                st.metric("Active Users", stats['active_users'], "✅")
            with col3:
                st.metric("Conversations", stats['total_conversations'], "💬")
            with col4:
                st.metric("Documents", stats['total_documents'], "📄")
            with col5:
                st.metric("Messages", stats['total_messages'], "📨")
    
    with tab2:
        st.header("User Management")
        users = make_request('GET', '/admin/users')
        
        if 'error' not in users:
            st.dataframe(
                [
                    {
                        'ID': u['id'],
                        'Username': u['username'],
                        'Email': u['email'],
                        'Role': u['role'],
                        'Active': u['is_active'],
                        'Created': u['created_at'][:10]
                    }
                    for u in users
                ],
                use_container_width=True
            )
            
            st.divider()
            st.subheader("Delete User")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                user_id = st.selectbox("Select user to delete", [u['id'] for u in users])
            with col2:
                if st.button("Delete User"):
                    if st.session_state.user_info['id'] != user_id:
                        make_request('DELETE', f'/admin/users/{user_id}')
                        st.success("User deleted")
                        st.rerun()
                    else:
                        st.error("Cannot delete yourself")
    
    with tab3:
        st.header("All Conversations")
        convs = make_request('GET', '/admin/conversations')
        
        if 'error' not in convs:
            st.dataframe(
                [
                    {
                        'ID': c['id'],
                        'User ID': c['user_id'],
                        'Title': c['title'],
                        'Messages': c['message_count'],
                        'Created': c['created_at'][:10]
                    }
                    for c in convs
                ],
                use_container_width=True
            )
    
    with tab4:
        st.header("Workflow Logs")
        logs = make_request('GET', '/admin/workflows')
        
        if 'error' not in logs:
            st.dataframe(
                [
                    {
                        'Workflow': log['workflow_type'],
                        'Status': log['status'],
                        'User': log['user_id'],
                        'Timestamp': log['timestamp'][:10]
                    }
                    for log in logs
                ],
                use_container_width=True
            )
    
    st.divider()
    
    if st.button("🚪 Logout"):
        st.session_state.access_token = None
        st.session_state.user_info = None
        st.session_state.current_page = 'login'
        st.rerun()
    
    render_footer()

# Main app logic
def main():
    if not st.session_state.access_token:
        if st.session_state.current_page == 'signup':
            signup_page()
        else:
            login_page()
    else:
        if st.session_state.current_page == 'admin_dashboard':
            admin_dashboard()
        elif st.session_state.current_page == 'documents':
            documents_page()
        elif st.session_state.current_page == 'analytics':
            analytics_page()
        elif st.session_state.current_page == 'settings':
            settings_page()
        else:
            chat_page()

if __name__ == "__main__":
    main()