# Website Content Summarizer

[Previous sections remain the same...]

## Technical Architecture

### Frontend (UI) Components

The application uses Streamlit to create a responsive web interface with the following components:

1. **Main Layout**:
   - Two-column layout for better space utilization
   - Left column: URL input and summary display
   - Right column: History of previous summaries

2. **UI Elements**:
   - URL input field with validation
   - "Generate Summary" button with loading spinner
   - Summary display box with formatted text
   - Download button for saving summaries
   - History section with expandable entries
   - Sidebar with about information and settings

3. **Styling**:
   - Custom CSS for consistent look and feel
   - Responsive design for different screen sizes
   - Color-coded buttons and sections
   - Loading indicators for better UX

### Backend Architecture

1. **AWS Bedrock Integration**:
   ```python
   bedrock = boto3.client(
       service_name='bedrock-runtime',
       region_name='eu-north-1'
   )
   ```
   - Uses boto3 to interact with AWS Bedrock
   - Handles authentication and API calls
   - Manages model responses and error handling

2. **Content Extraction Pipeline**:
   ```python
   def extract_text_from_url(url):
       # Selenium setup for JavaScript rendering
       # BeautifulSoup for HTML parsing
       # Text cleaning and formatting
   ```
   - Uses Selenium for JavaScript-rendered content
   - BeautifulSoup for HTML parsing
   - Text cleaning and formatting
   - Content length validation

3. **AI Processing**:
   ```python
   def generate_summary(text):
       # Claude 3 API call
       # Response processing
       # Summary formatting
   ```
   - Formats content for Claude 3
   - Handles API responses
   - Processes and formats summaries

4. **State Management**:
   ```python
   if 'history' not in st.session_state:
       st.session_state.history = []
   ```
   - Uses Streamlit's session state
   - Maintains history of summaries
   - Manages rate limiting

5. **Error Handling**:
   - Graceful error handling for API calls
   - User-friendly error messages
   - Rate limit enforcement
   - Content validation

### Data Flow

1. **User Input**:
   ```
   User → URL Input → Validation → Processing
   ```

2. **Content Processing**:
   ```
   URL → Selenium → BeautifulSoup → Cleaned Text
   ```

3. **AI Processing**:
   ```
   Cleaned Text → Claude 3 → Formatted Summary
   ```

4. **Output Handling**:
   ```
   Summary → Display → History → Download Option
   ```

### Security Features

1. **Rate Limiting**:
   ```python
   def check_rate_limit():
       # Enforces request limits
       # Prevents API abuse
   ```

2. **Content Validation**:
   ```python
   def validate_content_length(text):
       # Ensures content within limits
       # Prevents resource exhaustion
   ```

3. **AWS Security**:
   - IAM role-based access
   - Secure credential management
   - API key protection

### Configuration Management

1. **Environment Settings**:
   ```python
   # config.py
   MAX_CONTENT_LENGTH = 100000
   RATE_LIMIT = 10
   ```

2. **AWS Configuration**:
   ```python
   # bedrock-policy.json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "bedrock:InvokeModel"
               ],
               "Resource": [
                   "arn:aws:bedrock:eu-north-1::foundation-model/*"
               ]
           }
       ]
   }
   ```

3. **Streamlit Configuration**:
   ```toml
   # .streamlit/config.toml
   [theme]
   primaryColor = "#4CAF50"
   ```

### Performance Considerations

1. **Caching**:
   - Streamlit's built-in caching
   - Session state management
   - Efficient data handling

2. **Resource Management**:
   - Chrome driver cleanup
   - Memory management
   - Connection pooling

3. **Error Recovery**:
   - Graceful failure handling
   - User feedback
   - State recovery

[Rest of the README remains the same...] 