# Goodfire Feature Explorer

A web application for exploring and visualizing AI-generated text features using the Goodfire API. This application allows users to input questions or statements and see what features are detected in the text.

## Features

- Modern, responsive UI built with Bootstrap
- Integration with Goodfire's API for real feature extraction
- Interactive feature visualization with animated progress bars
- Categorized features (Intent, Sentiment, Entity, Style, Other)
- Toggle feature categories on/off with checkboxes
- Real-time feedback with loading indicators

## Project Structure

```
goodfire_webapp/
├── app.py                 # Flask application with Goodfire API integration
├── static/
│   ├── script.js          # Client-side JavaScript
│   └── style.css          # Custom CSS styles
└── templates/
    └── index.html         # HTML template
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/goodfire-feature-explorer.git
cd goodfire-feature-explorer
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask development server:
```bash
python goodfire_webapp/app.py
```

2. Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

## How to Use

1. Enter a question or statement in the text area
2. Click the "Generate" button
3. View the AI-generated response
4. Explore the detected features, categorized by type
5. Toggle feature categories using the checkboxes

## Customizing Model Selection

The application uses "meta-llama/Llama-3.1-8B-Instruct" as the default model. You can change this by setting the `GOODFIRE_MODEL` environment variable before starting the application.

## License

MIT

## Acknowledgements

- Goodfire for the feature extraction API
- Bootstrap for the responsive UI framework
- Flask for the backend web framework 