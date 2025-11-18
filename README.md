# INTELLIGENT MEETING - Minimalist Edition

AI-Powered Meeting Assistant with clean, minimalist interface.

## Features

- **Auto Transcription** - Real-time speech-to-text conversion
- **Speaker Identification** - Automatic speaker detection and tracking
- **AI Summarization** - Intelligent meeting summary generation
- **Action Items Extraction** - Automatic task identification and assignment
- **Sentiment Analysis** - Real-time emotion and tone detection
- **Meeting Analytics** - Comprehensive effectiveness metrics
- **Clean UI** - Minimalist monochromatic design

## Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   python app.py
   ```

3. **Access**
   Open browser: http://localhost:5000

## Demo Accounts

| Username | Password  | Role          |
|----------|-----------|---------------|
| admin    | admin123  | Administrator |
| user1    | user123   | John Doe      |
| user2    | user123   | Jane Smith    |

## Usage

1. **Login** with demo credentials
2. **Create Meeting** from dashboard
3. **Start Recording** to begin transcription
4. **View Analytics** for insights
5. **Review Summary** after completion

## Technology Stack

- **Backend**: Flask, Socket.IO, Python 3.7+
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI/ML**: TextBlob, NLTK, Pandas
- **Visualization**: Matplotlib
- **Real-time**: WebSocket

## Project Structure

```
intelligent_meeting_minimalist/
├── app.py                      # Main application
├── requirements.txt            # Dependencies
├── templates/
│   ├── index.html             # Login page
│   ├── dashboard.html         # Dashboard
│   └── meeting_detail.html    # Meeting interface
└── README.md                  # Documentation
```

## Configuration

Environment variables:
- `FLASK_ENV`: development/production
- `SECRET_KEY`: Session secret
- `PORT`: Server port (default: 5000)

## License

MIT License - Free for commercial and non-commercial use.
