from flask import Flask, render_template, request, jsonify, session, send_file
from flask_socketio import SocketIO, emit
import os
import json
import datetime
from datetime import timedelta
import uuid
import eventlet
import io
import base64
import matplotlib.pyplot as plt
from textblob import TextBlob
import pandas as pd
import threading
import time

plt.switch_backend('Agg')

app = Flask(__name__)
app.secret_key = 'intelligent_meeting_secret_key_2024'
app.config['SECRET_KEY'] = 'your_secret_key_here'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

class MeetingDatabase:
    def __init__(self):
        self.meetings = {}
        self.users = {
            'admin': {'password': 'admin123', 'name': 'Administrator', 'role': 'Admin'},
            'user1': {'password': 'user123', 'name': 'John Doe', 'role': 'Manager'},
            'user2': {'password': 'user123', 'name': 'Jane Smith', 'role': 'Team Lead'}
        }
        self.analytics = {}
    
    def add_meeting(self, meeting_data):
        self.meetings[meeting_data['id']] = meeting_data
    
    def get_meeting(self, meeting_id):
        return self.meetings.get(meeting_id)
    
    def update_meeting(self, meeting_id, updates):
        if meeting_id in self.meetings:
            self.meetings[meeting_id].update(updates)
    
    def get_user_meetings(self, username):
        return [meeting for meeting in self.meetings.values() 
                if meeting.get('creator') == username]

db = MeetingDatabase()

class IntelligentMeetingAI:
    def __init__(self):
        self.active_transcriptions = {}
    
    def analyze_sentiment(self, text):
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity,
            'sentiment': 'Positive' if blob.sentiment.polarity > 0.1 else 
                        'Negative' if blob.sentiment.polarity < -0.1 else 'Neutral'
        }
    
    def extract_action_items(self, text):
        action_keywords = ['will', 'should', 'must', 'need to', 'going to', 'plan to', 
                          'action item', 'todo', 'task', 'assign', 'responsible for']
        sentences = text.split('.')
        action_items = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in action_keywords):
                action_item = {
                    'task': sentence.strip(),
                    'assigned_to': self.extract_person(sentence),
                    'deadline': self.extract_deadline(sentence),
                    'priority': 'Medium'
                }
                action_items.append(action_item)
        
        return action_items
    
    def extract_person(self, text):
        people_keywords = ['john', 'jane', 'mike', 'sarah', 'team', 'all', 'developer', 'designer']
        words = text.lower().split()
        for word in words:
            if word in people_keywords:
                return word.title()
        return 'Team'
    
    def extract_deadline(self, text):
        if 'next week' in text.lower():
            return (datetime.datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        elif 'tomorrow' in text.lower():
            return (datetime.datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        elif 'today' in text.lower():
            return datetime.datetime.now().strftime('%Y-%m-%d')
        else:
            return (datetime.datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
    
    def generate_summary(self, transcription):
        key_points = [
            "Project timeline discussion completed",
            "New feature requirements finalized",
            "Team assignments clarified",
            "Next review meeting scheduled"
        ]
        
        return {
            'key_decisions': key_points,
            'main_topics': ['Project Planning', 'Resource Allocation', 'Timeline Review'],
            'overall_sentiment': self.analyze_sentiment(transcription)['sentiment'],
            'meeting_effectiveness': self.calculate_effectiveness(transcription)
        }
    
    def calculate_effectiveness(self, transcription):
        word_count = len(transcription.split())
        sentence_count = len([s for s in transcription.split('.') if len(s.strip()) > 0])
        
        if word_count > 500 and sentence_count > 10:
            return 'High'
        elif word_count > 200 and sentence_count > 5:
            return 'Medium'
        else:
            return 'Low'

ai_processor = IntelligentMeetingAI()

@app.route('/')
def index():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = db.users.get(username)
    if user and user['password'] == password:
        session['username'] = username
        session['user_display_name'] = user['name']
        session['user_role'] = user['role']
        return jsonify({'success': True, 'message': 'Login successful'})
    
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return render_template('index.html')
    
    user_meetings = db.get_user_meetings(session['username'])
    return render_template('dashboard.html', 
                         username=session['username'],
                         user_display_name=session.get('user_display_name', 'User'),
                         user_role=session.get('user_role', 'User'),
                         meetings=user_meetings)

@app.route('/create_meeting', methods=['POST'])
def create_meeting():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    data = request.get_json()
    meeting_id = str(uuid.uuid4())[:8]
    
    meeting_data = {
        'id': meeting_id,
        'title': data.get('title', 'New Meeting'),
        'creator': session['username'],
        'participants': data.get('participants', []),
        'created_at': datetime.datetime.now().isoformat(),
        'status': 'scheduled',
        'transcription': '',
        'summary': {},
        'action_items': [],
        'analytics': {}
    }
    
    db.add_meeting(meeting_data)
    return jsonify({'success': True, 'meeting_id': meeting_id})

@app.route('/meeting/<meeting_id>')
def meeting_detail(meeting_id):
    if 'username' not in session:
        return render_template('index.html')
    
    meeting = db.get_meeting(meeting_id)
    if not meeting:
        return "Meeting not found", 404
    
    return render_template('meeting_detail.html', 
                         meeting=meeting,
                         username=session['username'])

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connection_response', {'data': 'Connected to Intelligent Meeting'})

@socketio.on('start_recording')
def handle_start_recording(data):
    meeting_id = data.get('meeting_id')
    print(f'Starting recording for meeting: {meeting_id}')
    
    def simulate_transcription():
        sample_transcripts = [
            "Okay team, let's start the meeting.",
            "We need to discuss the project timeline.",
            "I think we should aim for completion by next Friday.",
            "John, can you handle the frontend development?",
            "Jane will be responsible for backend integration.",
            "We also need to consider the API documentation.",
            "Let's schedule a follow-up meeting for next week."
        ]
        
        for i, transcript in enumerate(sample_transcripts):
            time.sleep(2)
            
            sentiment = ai_processor.analyze_sentiment(transcript)
            action_items = ai_processor.extract_action_items(transcript)
            
            emit('transcription_update', {
                'text': transcript,
                'speaker': f'Speaker {i % 3 + 1}',
                'timestamp': datetime.datetime.now().strftime('%H:%M:%S'),
                'sentiment': sentiment,
                'new_action_items': action_items
            })
            
            meeting = db.get_meeting(meeting_id)
            if meeting:
                meeting['transcription'] += f"\n{transcript}"
                if action_items:
                    meeting['action_items'].extend(action_items)
    
    thread = threading.Thread(target=simulate_transcription)
    thread.daemon = True
    thread.start()
    
    emit('recording_started', {'meeting_id': meeting_id})

@socketio.on('stop_recording')
def handle_stop_recording(data):
    meeting_id = data.get('meeting_id')
    print(f'Stopping recording for meeting: {meeting_id}')
    
    meeting = db.get_meeting(meeting_id)
    if meeting and meeting['transcription']:
        summary = ai_processor.generate_summary(meeting['transcription'])
        meeting['summary'] = summary
        meeting['status'] = 'completed'
        
        emit('meeting_completed', {
            'summary': summary,
            'total_transcription': meeting['transcription']
        })

@socketio.on('request_analytics')
def handle_analytics_request(data):
    meeting_id = data.get('meeting_id')
    meeting = db.get_meeting(meeting_id)
    
    if meeting and meeting['transcription']:
        fig, ax = plt.subplots(figsize=(8, 4))
        
        categories = ['Discussion', 'Decisions', 'Action Items', 'Questions']
        values = [65, 20, 10, 5]
        
        ax.bar(categories, values, color=['#1a1a1a', '#333333', '#4d4d4d', '#666666'])
        ax.set_ylabel('Percentage (%)')
        ax.set_title('Meeting Content Distribution')
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        img_buffer.seek(0)
        img_data = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        emit('analytics_data', {
            'chart_image': f'data:image/png;base64,{img_data}',
            'effectiveness_score': meeting['summary'].get('meeting_effectiveness', 'Medium'),
            'sentiment_analysis': meeting['summary'].get('overall_sentiment', 'Neutral')
        })

if __name__ == '__main__':
    print("Starting Intelligent Meeting Application...")
    print("Access the application at: http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
