import os
import time
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

# Set page configuration - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="AI Search Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables (for local development)
_ = load_dotenv(find_dotenv())

# Initialize session state for API keys if not already present
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = os.getenv('OPENAI_API_KEY', '')
if "tavily_api_key" not in st.session_state:
    st.session_state.tavily_api_key = os.getenv('TAVILY_API_KEY', '')
if "api_keys_valid" not in st.session_state:
    st.session_state.api_keys_valid = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thinking" not in st.session_state:
    st.session_state.thinking = False

# Custom CSS for a more professional look
st.markdown("""
<style>
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #1E88E5;
    }
    .sub-header {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 600;
        color: #333;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        display: flex;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .chat-message.user {
        background-color: #E3F2FD;
        border-left: 5px solid #1E88E5;
    }
    .chat-message.assistant {
        background-color: #F5F5F5;
        border-left: 5px solid #4CAF50;
    }
    .chat-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .chat-message .message {
        flex-grow: 1;
    }
    .highlight {
        background-color: #E3F2FD;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .stButton button {
        background-color: #1E88E5;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: #1565C0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .clear-button button {
        background-color: #F5F5F5;
        color: #333;
        border: 1px solid #ddd;
    }
    .clear-button button:hover {
        background-color: #EEEEEE;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .api-form {
        background-color: #F5F5F5;
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        border: 1px solid #ddd;
    }
    .source-link {
        font-size: 0.8rem;
        color: #1E88E5;
        text-decoration: none;
    }
    .source-link:hover {
        text-decoration: underline;
    }
    .thinking-animation {
        display: inline-block;
        position: relative;
        width: 80px;
        height: 20px;
    }
    .thinking-animation div {
        position: absolute;
        top: 8px;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #1E88E5;
        animation-timing-function: cubic-bezier(0, 1, 1, 0);
    }
    .thinking-animation div:nth-child(1) {
        left: 8px;
        animation: thinking1 0.6s infinite;
    }
    .thinking-animation div:nth-child(2) {
        left: 8px;
        animation: thinking2 0.6s infinite;
    }
    .thinking-animation div:nth-child(3) {
        left: 32px;
        animation: thinking2 0.6s infinite;
    }
    .thinking-animation div:nth-child(4) {
        left: 56px;
        animation: thinking3 0.6s infinite;
    }
    @keyframes thinking1 {
        0% {transform: scale(0);}
        100% {transform: scale(1);}
    }
    @keyframes thinking3 {
        0% {transform: scale(1);}
        100% {transform: scale(0);}
    }
    @keyframes thinking2 {
        0% {transform: translate(0, 0);}
        100% {transform: translate(24px, 0);}
    }
    .stTextInput input {
        border-radius: 20px;
        padding: 0.5rem 1rem;
        border: 1px solid #ddd;
    }
    .stTextInput input:focus {
        border-color: #1E88E5;
        box-shadow: 0 0 0 0.2rem rgba(30, 136, 229, 0.25);
    }
    .sidebar-content {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #ddd;
        color: #666;
        font-size: 0.8rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #F5F5F5;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<h1 class="main-header">🔍 AI Search Assistant</h1>', unsafe_allow_html=True)

# Create tabs for different sections
tabs = st.tabs(["🤖 Chat", "ℹ️ About", "🛠️ Settings"])

with tabs[0]:  # Chat Tab
    if st.session_state.api_keys_valid:
        # Chat interface
        st.markdown('<h3 class="sub-header">Ask me anything</h3>', unsafe_allow_html=True)
        
        # Query input with dynamic placeholder
        placeholders = [
            "e.g., What are the latest developments in AI?",
            "e.g., Tell me about recent movies in 2025",
            "e.g., What are the best tourist spots in Japan?",
            "e.g., How does quantum computing work?",
            "e.g., What are the trending technologies in 2025?"
        ]
        import random
        query = st.text_input("", placeholder=random.choice(placeholders), key="query_input")
        
        # Buttons
        col1, col2 = st.columns([1, 5])
        with col1:
            search_button = st.button("🔍 Search", use_container_width=True)
        with col2:
            clear_button = st.button("🗑️ Clear Chat", use_container_width=False, key="clear_button")
            st.markdown('<div class="clear-button"></div>', unsafe_allow_html=True)
        
        # Chat container
        st.markdown('<h3 class="sub-header">Conversation</h3>', unsafe_allow_html=True)
        chat_container = st.container(height=500)
        
        # Process the query when submitted
        if query and search_button:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": query})
            st.session_state.thinking = True
            
            # Force a rerun to show the user message immediately
            st.experimental_rerun()
        
        # Display chat messages
        with chat_container:
            if not st.session_state.messages:
                st.info("👋 Hello! Ask me anything and I'll search the web for answers.")
            
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user">
                        <img src="https://api.dicebear.com/7.x/bottts/svg?seed=user" class="avatar" alt="user">
                        <div class="message">{message["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant">
                        <img src="https://api.dicebear.com/7.x/bottts/svg?seed=assistant" class="avatar" alt="assistant">
                        <div class="message">{message["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Show thinking animation
            if st.session_state.thinking:
                st.markdown(f"""
                <div class="chat-message assistant">
                    <img src="https://api.dicebear.com/7.x/bottts/svg?seed=assistant" class="avatar" alt="assistant">
                    <div class="message">
                        <p>Thinking...</p>
                        <div class="thinking-animation">
                            <div></div><div></div><div></div><div></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                try:
                    # Set API keys from session state
                    os.environ["OPENAI_API_KEY"] = st.session_state.openai_api_key
                    os.environ["TAVILY_API_KEY"] = st.session_state.tavily_api_key
                    
                    # Get the last user message
                    last_user_message = next((msg["content"] for msg in reversed(st.session_state.messages) 
                                             if msg["role"] == "user"), None)
                    
                    if last_user_message:
                        # Get model and max results from session state
                        model_name = st.session_state.get("model_name", "gpt-3.5-turbo-0125")
                        max_results = st.session_state.get("max_results", 3)
                        
                        # Initialize the model and tools
                        chat_model = ChatOpenAI(model=model_name)
                        search = TavilySearchResults(max_results=max_results)
                        tools = [search]
                        
                        # Create the agent
                        agent_executor = create_react_agent(chat_model, tools)
                        
                        # Execute the agent
                        response = agent_executor.invoke({"messages": [HumanMessage(content=last_user_message)]})
                        
                        # Extract the final AI response
                        ai_message = response['messages'][-1].content
                        
                        # Add assistant response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": ai_message})
                    
                except Exception as e:
                    # Add error message to chat history
                    error_message = f"Sorry, I encountered an error: {str(e)}"
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
                
                # Turn off thinking animation
                st.session_state.thinking = False
                
                # Force a rerun to update the chat with the response
                st.experimental_rerun()
        
        # Clear conversation when button is clicked
        if clear_button:
            st.session_state.messages = []
            st.experimental_rerun()
    
    else:
        # Welcome message if API keys are not yet provided
        st.info("👈 Please enter your API keys in the Settings tab to get started")
        
        # Example of what the app can do
        st.markdown('<h3 class="sub-header">What can this AI assistant do?</h3>', unsafe_allow_html=True)
        
        # Feature cards
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; height: 200px;">
                <h4>🌐 Real-time Web Search</h4>
                <p>Get up-to-date information from across the internet on any topic.</p>
                <p>The assistant uses Tavily's powerful search API to find relevant and current information.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-top: 20px; height: 200px;">
                <h4>🧠 Powered by Advanced AI</h4>
                <p>Utilizes OpenAI's powerful language models to understand questions and generate helpful responses.</p>
                <p>Choose between different models based on your needs.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; height: 200px;">
                <h4>💬 Natural Conversation</h4>
                <p>Have a flowing conversation with follow-up questions and contextual responses.</p>
                <p>The chat history is maintained throughout your session.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-top: 20px; height: 200px;">
                <h4>📊 Customizable Results</h4>
                <p>Adjust the number of search results to balance between comprehensive information and response speed.</p>
                <p>Configure the AI model to suit your specific needs.</p>
            </div>
            """, unsafe_allow_html=True)

with tabs[1]:  # About Tab
    st.markdown('<h3 class="sub-header">About AI Search Assistant</h3>', unsafe_allow_html=True)
    
    st.markdown("""
    This application combines the power of large language models with real-time web search capabilities to provide you with up-to-date information on any topic.
    
    ### How It Works
    
    1. **User Input**: You ask a question or request information on any topic
    2. **Web Search**: The app searches the internet using Tavily's search API
    3. **AI Processing**: OpenAI's language model processes the search results
    4. **Response Generation**: The AI generates a comprehensive, informative response
    
    ### Technologies Used
    
    - **Frontend**: Streamlit
    - **AI**: OpenAI GPT models
    - **Search**: Tavily Search API
    - **Framework**: LangChain and LangGraph
    
    ### Privacy & Security
    
    - Your API keys are stored only in your browser's session
    - Keys are never saved to our servers
    - Each user must provide their own API keys
    """)
    
    # Example use cases
    st.markdown('<h3 class="sub-header">Example Use Cases</h3>', unsafe_allow_html=True)
    
    use_cases = [
        {
            "title": "Research Assistant",
            "description": "Get summaries and insights on academic topics, current events, or historical information.",
            "example": "What are the latest developments in quantum computing?"
        },
        {
            "title": "Current Events",
            "description": "Stay updated on news, sports, entertainment, and global happenings.",
            "example": "What major events happened this week in technology?"
        },
        {
            "title": "Learning Tool",
            "description": "Explain complex concepts in an easy-to-understand manner.",
            "example": "Explain machine learning algorithms to a beginner."
        },
        {
            "title": "Travel Planning",
            "description": "Get information about destinations, attractions, and travel tips.",
            "example": "What are the must-visit places in Tokyo?"
        }
    ]
    
    cols = st.columns(2)
    for i, use_case in enumerate(use_cases):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px;">
                <h4>{use_case['title']}</h4>
                <p>{use_case['description']}</p>
                <p><em>Example: "{use_case['example']}"</em></p>
            </div>
            """, unsafe_allow_html=True)

with tabs[2]:  # Settings Tab
    st.markdown('<h3 class="sub-header">API Configuration</h3>', unsafe_allow_html=True)
    
    # API key input section with better UX
    with st.form("api_form", clear_on_submit=False):
        st.markdown("""
        To use this application, you need to provide your own API keys for OpenAI and Tavily.
        These keys are stored only in your browser session and are never saved on our servers.
        """)
        
        # Get API keys from session state or user input
        openai_api_key = st.text_input(
            "OpenAI API Key", 
            value=st.session_state.openai_api_key,
            type="password",
            help="Get your API key from https://platform.openai.com/api-keys"
        )
        
        tavily_api_key = st.text_input(
            "Tavily API Key", 
            value=st.session_state.tavily_api_key,
            type="password",
            help="Get your API key from https://tavily.com/#api"
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            submitted = st.form_submit_button("Save API Keys", use_container_width=True)
        
        if submitted:
            if not openai_api_key or not tavily_api_key:
                st.error("Please provide both API keys")
            else:
                # Save API keys to session state
                st.session_state.openai_api_key = openai_api_key
                st.session_state.tavily_api_key = tavily_api_key
                st.session_state.api_keys_valid = True
                st.success("✅ API keys saved successfully!")
    
    # Only show these settings if API keys are provided
    if st.session_state.api_keys_valid:
        st.markdown('<h3 class="sub-header">Search Settings</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Model selection
            model_options = {
                "gpt-3.5-turbo-0125": "GPT-3.5 Turbo (Faster, Lower Cost)",
                "gpt-4-turbo-preview": "GPT-4 Turbo (More Capable, Higher Cost)"
            }
            
            selected_model = st.selectbox(
                "Select AI Model",
                options=list(model_options.keys()),
                format_func=lambda x: model_options[x],
                index=0,
                help="GPT-4 provides better results but costs more"
            )
            
            # Save to session state
            st.session_state.model_name = selected_model
        
        with col2:
            # Number of search results
            max_results = st.slider(
                "Maximum Search Results", 
                min_value=1, 
                max_value=10, 
                value=st.session_state.get("max_results", 3),
                help="More results provide more context but may slow down the response"
            )
            
            # Save to session state
            st.session_state.max_results = max_results
    
    # Information section
    st.markdown('<h3 class="sub-header">How to Get API Keys</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd;">
            <h4>OpenAI API Key</h4>
            <ol>
                <li>Go to <a href="https://platform.openai.com/signup" target="_blank">OpenAI</a> and create an account</li>
                <li>Navigate to the API section</li>
                <li>Click on "Create new secret key"</li>
                <li>Copy the key and paste it in the form above</li>
            </ol>
            <a href="https://platform.openai.com/api-keys" target="_blank" class="stButton">
                <button style="background-color: #1E88E5; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer;">
                    Get OpenAI API Key
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="padding: 20px; border-radius: 10px; border: 1px solid #ddd;">
            <h4>Tavily API Key</h4>
            <ol>
                <li>Go to <a href="https://tavily.com/#api" target="_blank">Tavily</a> and create an account</li>
                <li>Navigate to the API dashboard</li>
                <li>Generate a new API key</li>
                <li>Copy the key and paste it in the form above</li>
            </ol>
            <a href="https://tavily.com/#api" target="_blank" class="stButton">
                <button style="background-color: #1E88E5; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer;">
                    Get Tavily API Key
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>Built with ❤️ using Streamlit, LangChain and OpenAI | © 2025 AI Search Assistant (Made by Mahfujul Karim) </p>
</div>
""", unsafe_allow_html=True)