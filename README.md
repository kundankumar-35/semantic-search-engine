# Semantic Search Engine

## Overview
The Semantic Search Engine is designed to provide advanced search capabilities by understanding the context and meaning of queries. This project leverages natural language processing (NLP) techniques to deliver relevant and accurate search results.

## Features
- Contextual understanding of search queries
- Support for complex queries with multiple keywords
- Easy setup and integration with existing applications
- User-friendly API endpoints
- Comprehensive logging and analytics

## Tech Stack
- **Backend**: Python, Flask
- **NLP Library**: spaCy, NLTK
- **Database**: PostgreSQL
- **Frontend**: React
- **Deployment**: Docker, Kubernetes

## Project Structure
```
semantic-search-engine/
├── backend/
│   ├── app.py      # Main application file
│   ├── models/     # Database models
│   ├── routes/     # API routes
│   └── utils/      # Utility functions
├── frontend/
│   ├── src/
│   │   ├── App.js   # Main React component
│   │   ├── components/ # Custom components
│   │   └── styles/     # CSS styles
├── docker-compose.yml  # Docker configuration
└── README.md           # Project documentation
```

## Installation Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/kundankumar-35/semantic-search-engine.git
   cd semantic-search-engine
   ```
2. **Set up the backend**:
   - Navigate to the backend directory and create a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
   - Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up the database**:
   - Configure your PostgreSQL database credentials in the `config.py` file.
   - Run the migrations:
   ```bash
   python -m flask db upgrade
   ```
4. **Run the application**:
   ```bash
   python app.py
   ```
5. **Set up the frontend**:
   - Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
   - Install the required packages:
   ```bash
   npm install
   ```
   - Start the frontend application:
   ```bash
   npm start
   ```

## API Endpoints
- **GET /api/search**: Perform a search query.
  - **Query Param**: `q` (string) - The search keyword(s).

- **POST /api/feedback**: Submit feedback about a search result.
  - **Body**:
    ```json
    {
      "resultId": "123",
      "feedback": "useful"
    }
    ```

## Frontend Details
The frontend is built using React and interacts with the backend through RESTful API calls. Components are organized for easy navigation and maintainability. The state is managed using React hooks.

## How it Works
1. When a user submits a search query, the request is sent to the `/api/search` endpoint.
2. The backend processes the query using NLP techniques to extract meaning and context.
3. Relevant results are fetched from the database and returned to the frontend.
4. The frontend displays the results, allowing users to provide feedback on their relevance.
5. Feedback is collected and analyzed to continuously improve the search engine's accuracy.