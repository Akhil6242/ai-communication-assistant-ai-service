from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import os
from waitress import serve


app = Flask(__name__)
CORS(app)

class SimpleEmailProcessor:
    def __init__(self):
        # Simple keyword-based processing for hackathon
        self.urgent_keywords = [
            'urgent', 'critical', 'immediate', 'asap', 'emergency', 
            'blocked', 'down', 'cannot access', 'not working', 'broken'
        ]
        
        self.negative_words = [
            'problem', 'issue', 'error', 'failed', 'broken', 'not working',
            'frustrated', 'angry', 'disappointed', 'urgent', 'critical'
        ]
        
        self.positive_words = [
            'thank', 'great', 'excellent', 'good', 'happy', 'satisfied',
            'love', 'perfect', 'amazing', 'wonderful'
        ]

    def analyze_email(self, subject, body):
        full_text = f"{subject} {body}".lower()
        
        # Simple sentiment analysis
        negative_count = sum(1 for word in self.negative_words if word in full_text)
        positive_count = sum(1 for word in self.positive_words if word in full_text)
        
        if negative_count > positive_count:
            sentiment = 'negative'
        elif positive_count > negative_count:
            sentiment = 'positive'
        else:
            sentiment = 'neutral'
        
        # Priority detection
        priority = 'Critical' if any(keyword in full_text for keyword in ['critical', 'emergency', 'down']) else \
                  'Urgent' if any(keyword in full_text for keyword in self.urgent_keywords) else 'Normal'
        
        # Simple category classification
        if any(word in full_text for word in ['login', 'password', 'account', 'access']):
            category = 'Account Access'
        elif any(word in full_text for word in ['billing', 'charge', 'payment', 'refund']):
            category = 'Billing'
        elif any(word in full_text for word in ['api', 'technical', 'integration']):
            category = 'Technical Support'
        else:
            category = 'General Support'
            
        return {
            'sentiment': sentiment,
            'priority': priority,
            'category': category,
            'extracted_info': self._extract_basic_info(body)
        }
    
    def _extract_basic_info(self, body):
        extracted = {}
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, body)
        if emails:
            extracted['contact_emails'] = emails
        
        # Extract phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, body)
        if phones:
            extracted['phone_numbers'] = phones
            
        return extracted
    
    def generate_response(self, email_body, sentiment, category):
        # Template-based response generation
        if sentiment == 'negative':
            greeting = "Thank you for reaching out, and I sincerely apologize for any inconvenience you've experienced."
        elif sentiment == 'positive':
            greeting = "Thank you for your message! We're happy to help."
        else:
            greeting = "Thank you for contacting our support team."
        
        if 'account' in category.lower():
            main_response = """I understand you're having trouble with account access. Here are some steps that can help:

1. Try using the 'Forgot Password' link on our login page
2. Clear your browser cache and try again
3. Try accessing from an incognito window

If these steps don't work, I'll personally ensure your account access is restored."""
        
        elif 'billing' in category.lower():
            main_response = """I'll help resolve this billing concern immediately. Our billing team will investigate and correct any errors promptly.

You can also check your billing history in your account dashboard."""
        
        elif 'technical' in category.lower():
            main_response = """I'll connect you with our technical team who specialize in API and integration issues. 

In the meantime, our documentation at docs.company.com might be helpful."""
        
        else:
            main_response = """I've received your inquiry and will ensure you get the assistance you need. Our team will provide a detailed response shortly."""
        
        closing = """Please don't hesitate to reach out with any additional questions. We're committed to your success!

Best regards,
The Support Team"""
        
        return f"{greeting}\n\n{main_response}\n\n{closing}"

# Initialize processor
processor = SimpleEmailProcessor()

@app.route('/api/analyze-email', methods=['POST'])
def analyze_email():
    try:
        data = request.get_json()
        subject = data.get('subject', '')
        body = data.get('body', '')
        
        analysis = processor.analyze_email(subject, body)
        
        return jsonify({
            'sentiment': analysis['sentiment'],
            'priority': analysis['priority'],
            'category': analysis['category'],
            'extracted_info': analysis['extracted_info'],
            'success': True
        })
    
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/generate-response', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()
        email_body = data.get('body', '')
        sentiment = data.get('sentiment', 'neutral')
        category = data.get('category', 'general')
        
        response = processor.generate_response(email_body, sentiment, category)
        
        return jsonify({
            'ai_response': response,
            'success': True
        })
    
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'simple-email-ai-service'})

if __name__ == '__main__':
    print("🚀 Starting Simple AI Email Service...")
    print("✅ Service will be available at http://localhost:5000")
    print("✅ Health check: http://localhost:5000/health")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)