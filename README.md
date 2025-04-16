# Goodfire Feature Explorer

A Flask web application that leverages the Goodfire AI API to analyze and display features of LLM (Large Language Model) responses.

## Overview

This application allows users to:
1. Enter questions or statements
2. Receive AI-generated responses using the Goodfire API
3. Explore different categories of features present in the response (philosophy, writing style, tone, scientific concepts)
4. Adjust feature weights to generate new versions of the response

## Project Structure

```
goodfire_webapp/
├── app.py             # Main Flask application
├── static/
│   ├── script.js      # Main JavaScript for the application
│   ├── style.css      # CSS styling for the application
│   └── app.js         # Additional JavaScript functionality
└── templates/
    ├── index.html     # Main application page
    └── error.html     # Error page
```

## Features

- Interactive web interface for exploring AI features
- Feature categories: philosophy, writing style, tone, scientific concepts
- Feature visualization with strength indicators
- Response regeneration with adjusted feature weights
- Error handling and user feedback

## Requirements

See requirements.txt for the complete list of dependencies:
- Flask
- Goodfire API client
- Additional Python libraries

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure your Goodfire API key (instructions for getting a key: [https://goodfire.ai/](https://goodfire.ai/))
4. Run the application:
   ```
   python goodfire_webapp/app.py
   ```
5. Open a browser and navigate to http://localhost:5000

## Technical Details

- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript, Bootstrap 5
- API: Goodfire AI API for LLM feature analysis
- Asynchronous operations for API calls

## Credits

Developed using the Goodfire AI API for feature analysis and generation. 