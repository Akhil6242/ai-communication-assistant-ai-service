from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            email_content = data.get('email_content', '')
            email_type = data.get('type', 'general')
            
            # Simple AI logic - replace with your actual AI model
            response_templates = {
                'complaint': f"Thank you for bringing this to our attention. We apologize for any inconvenience caused by '{email_content[:50]}...'. We'll investigate this matter promptly and get back to you within 24 hours with a resolution.",
                'inquiry': f"Thank you for your inquiry regarding '{email_content[:50]}...'. Based on your question, I'd be happy to provide more detailed information and assist you further.",
                'support': f"Thank you for contacting our support team about '{email_content[:50]}...'. We've received your request and our technical team will assist you shortly.",
                'general': f"Thank you for your email. We appreciate you taking the time to contact us regarding '{email_content[:30]}...'. We'll review your message and respond appropriately."
            }
            
            generated_text = response_templates.get(email_type, response_templates['general'])
            
            # Enhanced response with more AI-like features
            response = {
                "generated_response": generated_text,
                "confidence": 0.85,
                "category": email_type,
                "sentiment": "neutral",
                "processing_time": "0.1s",
                "suggested_actions": ["review", "respond", "archive"],
                "status": "success"
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            # Error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "error": f"Internal server error: {str(e)}",
                "status": "error"
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
    def do_GET(self):
        # Health check endpoint
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        health_response = {
            "status": "healthy",
            "service": "AI Communication Assistant",
            "version": "1.0.0",
            "endpoints": ["/api/generate-response"]
        }
        self.wfile.write(json.dumps(health_response).encode())
