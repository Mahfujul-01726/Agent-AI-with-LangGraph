# AI Search Assistant

A web-based AI assistant that can search the internet to answer questions using LangChain, OpenAI, and Tavily Search.

## Features

- Interactive web interface built with Streamlit
- Powered by OpenAI's language models
- Real-time web search capabilities using Tavily Search
- Conversation history tracking
- Customizable search parameters
- Deployment-ready with in-app API key management

## How to run locally

1. Create and activate a conda environment:
   ```
   conda create -n llmapp python=3.11 -y
   conda activate llmapp
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. (Optional) Set up your API keys in a `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```
   Note: You can also enter API keys directly in the app interface.

4. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

5. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

## Deployment Options

### Deploy to Streamlit Cloud

1. Fork this repository to your GitHub account
2. Sign up for [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and connect it to your GitHub repository
4. Deploy the app (no environment variables needed as users will input their API keys)

### Deploy to Heroku

1. Create a Heroku account and install the Heroku CLI
2. Create a new Heroku app:
   ```
   heroku create your-app-name
   ```
3. Add a `Procfile` with the following content:
   ```
   web: streamlit run app.py --server.port=$PORT
   ```
4. Deploy to Heroku:
   ```
   git push heroku main
   ```

## Usage

1. Enter your OpenAI and Tavily API keys in the sidebar
2. Configure search settings (model and number of results)
3. Enter your question in the text input field
4. Click the "Search" button
5. View the AI's response with information sourced from the web
6. Continue the conversation with follow-up questions

## Requirements

- Python 3.11+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Tavily API key ([Get one here](https://tavily.com/#api))