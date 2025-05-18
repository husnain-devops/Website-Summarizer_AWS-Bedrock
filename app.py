import boto3
import streamlit as st
from bs4 import BeautifulSoup
import requests
import json
from config import MAX_CONTENT_LENGTH, RATE_LIMIT
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from database import init_db, get_user_credits, update_user_credits
from pages.signin import show_signin_page
from pages.signup import show_signup_page

# Page configuration
st.set_page_config(
    page_title="Website Summarizer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: auto;
        min-width: 100px;
    }
    .stDownloadButton>button {
        width: 100%;
        background-color: #008CBA;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
    }
    .summary-box {
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ddd;
        background-color: #f9f9f9;
    }
    .url-input {
        margin-bottom: 1rem;
    }
    .header-container {
        text-align: center;
        padding: 1rem;
        margin-bottom: 2rem;
    }
    .stForm {
        max-width: 400px;
        margin: 0 auto;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize AWS clients
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='eu-north-1'
)

# Initialize the database
init_db()

# Session state initialization
if 'history' not in st.session_state:
    st.session_state.history = []

# Add authentication state to session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'show_signup' not in st.session_state:
    st.session_state['show_signup'] = False

# Function to extract text from website
def extract_text_from_url(url):
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')  # Updated headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # For macOS, we need to specify the binary location
        chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        
        # Initialize the Chrome driver with specific options for macOS
        driver = webdriver.Chrome(
            options=chrome_options
        )
        
        # Get the page
        driver.get(url)
        time.sleep(5)  # Wait for JavaScript to render
        
        # Get the page source
        html_content = driver.page_source
        
        # Close the driver
        driver.quit()
        
        # Parse HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        if not validate_content_length(text):
            st.warning(f"Content length exceeds maximum limit of {MAX_CONTENT_LENGTH} characters. Text will be truncated.")
            text = text[:MAX_CONTENT_LENGTH]
        
        return text
    except Exception as e:
        st.error(f"Error extracting text from URL: {str(e)}")
        return None

# Function to generate summary using Claude
def generate_summary(text):
    try:
        # Prepare messages for Claude 3
        messages = [
            {
                "role": "user",
                "content": f"Please provide a concise summary of the following text. Focus on the main points and key information. Structure the summary with bullet points for key takeaways and a brief paragraph for overall context:\n\n{text}"
            }
        ]

        # Call Bedrock API with Claude model using Messages API
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.5,
            "top_k": 250,
            "top_p": 1
        })

        response = bedrock.invoke_model(
            modelId="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        # Extract the assistant's message from the response
        summary = response_body['content'][0]['text']
        
        return summary.strip()
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

def check_rate_limit():
    current_time = time.time()
    if 'last_request_time' not in st.session_state:
        st.session_state.last_request_time = current_time
        return True
    
    time_diff = current_time - st.session_state.last_request_time
    if time_diff < (60 / RATE_LIMIT):
        st.warning(f"Please wait {int((60 / RATE_LIMIT) - time_diff)} seconds before making another request.")
        return False
    
    st.session_state.last_request_time = current_time
    return True

def validate_content_length(text):
    return len(text) <= MAX_CONTENT_LENGTH

def save_to_history(url, summary):
    st.session_state.history.append({
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'url': url,
        'summary': summary
    })

# Sidebar
with st.sidebar:
    st.title("📚 About")
    st.write("""
    This tool helps you summarize website content quickly and efficiently.
    Simply paste a URL and get a concise summary of the main points.
    """)
    
    st.subheader("📋 Features")
    st.write("""
    - Website text extraction
    - AI-powered summarization
    - Download summaries
    - History tracking
    """)
    
    st.subheader("⚙️ Settings")
    st.write(f"Max content length: {MAX_CONTENT_LENGTH} characters")
    st.write(f"Rate limit: {RATE_LIMIT} requests/minute")

# Main UI
def show_auth_buttons():
    col1, col2 = st.columns([6,1])
    with col2:
        if not st.session_state['authenticated']:
            if st.button("Sign In"):
                st.session_state['show_signup'] = False
                st.experimental_rerun()
            if st.button("Sign Up"):
                st.session_state['show_signup'] = True
                st.experimental_rerun()
        else:
            if st.button("Sign Out"):
                st.session_state['authenticated'] = False
                st.session_state['username'] = None
                st.session_state['user_id'] = None
                st.experimental_rerun()

def main():
    # Show auth buttons in top right
    show_auth_buttons()
    
    if not st.session_state['authenticated']:
        if st.session_state['show_signup']:
            show_signup_page()
        else:
            show_signin_page()
        return

    # Show credits in sidebar
    with st.sidebar:
        credits = get_user_credits(st.session_state['username'])
        st.metric("Credits Remaining", credits)
        
        if credits <= 0:
            st.error("You have no credits remaining!")
            return

    # Header
    st.markdown("<div class='header-container'>", unsafe_allow_html=True)
    st.title("🌐 Website Content Summarizer")
    st.write("Enter a URL to get an AI-powered summary of the website content")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Create two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # URL input
        url = st.text_input("🔗 Enter website URL:", key="url-input")
        
        if st.button("🚀 Generate Summary"):
            if url:
                if check_rate_limit():
                    with st.spinner("🔍 Extracting content..."):
                        text = extract_text_from_url(url)
                        
                    if text:
                        with st.spinner("🤖 Generating summary..."):
                            summary = generate_summary(text)
                            
                        if summary:
                            # Save to history
                            save_to_history(url, summary)
                            
                            st.markdown("### 📝 Summary")
                            st.markdown("<div class='summary-box'>", unsafe_allow_html=True)
                            st.write(summary)
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                            # Download button
                            st.download_button(
                                label="💾 Download Summary",
                                data=summary,
                                file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain"
                            )
                            
                            # Update credits after successful summary generation
                            update_user_credits(st.session_state['username'], 1)  # Deduct 1 credit per summary
            else:
                st.warning("⚠️ Please enter a URL")
    
    with col2:
        # History section
        st.markdown("### 📜 Recent Summaries")
        if st.session_state.history:
            for item in reversed(st.session_state.history[-5:]):  # Show last 5 summaries
                with st.expander(f"Summary from {item['timestamp']}"):
                    st.write(f"URL: {item['url']}")
                    st.write("Summary:")
                    st.write(item['summary'])
        else:
            st.info("No summaries generated yet")

if __name__ == "__main__":
    main() 