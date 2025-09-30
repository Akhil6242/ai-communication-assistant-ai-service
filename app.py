from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from ai_processor import EmailAIProcessor

app = Flask(__name__)
CORS(app)

# Initialize AI processor
ai_processor = EmailAIProcessor()

@app.route('/api/analyze-email', methods=['POST'])
def analyze_email():
    """Analyze email for sentiment, priority, and extract information"""
    try:
        data = request.get_json()
        email_subject = data.get('subject', '')
        email_body = data.get('body', '')
        
        # Perform AI analysis
        analysis = ai_processor.analyze_email(email_subject, email_body)
        
        return jsonify({
            'sentiment': analysis['sentiment'],
            'priority': analysis['priority'], 
            'category': analysis['category'],
            'extracted_info': analysis['extracted_info'],
            'sentiment_score': analysis['sentiment_score']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-response', methods=['POST'])
def generate_response():
    """Generate AI response for an email"""
    try:
        data = request.get_json()
        email_body = data.get('body', '')
        sentiment = data.get('sentiment', 'neutral')
        category = data.get('category', 'general')
        
        # Generate contextual response
        response = ai_processor.generate_response(email_body, sentiment, category)
        
        return jsonify({
            'ai_response': response,
            'success': True
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'email-ai-service'})

if __name__ == '__main__':
    print("Starting AI Email Service...")
    print("Loading AI models (this may take a moment)...")
    app.run(host='0.0.0.0', port=5000, debug=True)
