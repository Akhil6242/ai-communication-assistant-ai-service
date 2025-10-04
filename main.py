import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS - Allow your backend and frontend
CORS(app, origins=["*"])  # Configure properly in production

@app.route('/')
def home():
    return jsonify({
        "message": "AI Communication Assistant Service",
        "status": "running",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/generate-response"
        ]
    })

@app.route('/health')
def health():
    """Health check endpoint for Cloud Run"""
    return jsonify({"status": "healthy", "service": "ai-service"}), 200

@app.route('/generate-response', methods=['POST'])
def generate_response():
    """Generate AI response for email content"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        email_content = data.get('email_content', '')
        email_type = data.get('type', 'general')
        
        if not email_content:
            return jsonify({"error": "email_content is required"}), 400
        
        logger.info(f"Processing email of type: {email_type}")
        
        # Simple AI logic (replace with actual AI model)
        response_templates = {
            'complaint': f"Thank you for bringing this to our attention. We apologize for any inconvenience. We'll investigate this matter promptly and get back to you within 24 hours.",
            'inquiry': f"Thank you for your inquiry. Based on your question about '{email_content[:50]}...', I'd be happy to provide more information.",
            'support': f"Thank you for contacting our support team. We've received your request and will assist you shortly.",
            'general': f"Thank you for your email. We appreciate you taking the time to contact us regarding '{email_content[:30]}...'"
        }
        
        generated_text = response_templates.get(email_type, response_templates['general'])
        
        response = {
            "generated_response": generated_text,
            "confidence": 0.85,
            "category": email_type,
            "processing_time": "0.1s"
        }
        
        logger.info("Response generated successfully")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Cloud Run provides PORT environment variable
    port = int(os.environ.get('PORT', 8080))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting AI service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
