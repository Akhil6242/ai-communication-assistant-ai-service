from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import re
import json
from datetime import datetime

class EmailAIProcessor:
    def __init__(self):
        print("Initializing AI models...")
        
        # Load sentiment analysis model
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            return_all_scores=True
        )
        
        # Priority keywords (can be enhanced with ML model later)
        self.urgent_keywords = [
            'urgent', 'critical', 'immediate', 'asap', 'emergency', 
            'blocked', 'down', 'cannot access', 'not working', 
            'broken', 'failed', 'error', 'issue', 'problem'
        ]
        
        self.critical_keywords = [
            'critical', 'emergency', 'down', 'outage', 'severe',
            'major issue', 'completely broken', 'not working at all'
        ]
        
        # Knowledge base for response generation
        self.knowledge_base = self._load_knowledge_base()
        
        print("AI models loaded successfully!")
    
    def analyze_email(self, subject, body):
        """Comprehensive email analysis"""
        
        # Combine subject and body for analysis
        full_text = f"{subject} {body}"
        
        # Sentiment analysis
        sentiment_result = self.sentiment_analyzer(full_text)[0]
        sentiment_scores = {item['label']: item['score'] for item in sentiment_result}
        
        # Determine primary sentiment
        primary_sentiment = max(sentiment_scores, key=sentiment_scores.get)
        sentiment_mapping = {
            'LABEL_0': 'negative',  # Negative
            'LABEL_1': 'neutral',   # Neutral  
            'LABEL_2': 'positive'   # Positive
        }
        final_sentiment = sentiment_mapping.get(primary_sentiment, 'neutral')
        
        # Priority detection
        priority = self._detect_priority(subject, body)
        
        # Category classification
        category = self._classify_category(subject, body)
        
        # Information extraction
        extracted_info = self._extract_information(body)
        
        return {
            'sentiment': final_sentiment,
            'sentiment_score': round(sentiment_scores[primary_sentiment], 3),
            'priority': priority,
            'category': category,
            'extracted_info': extracted_info
        }
    
    def _detect_priority(self, subject, body):
        """Detect email priority based on keywords and context"""
        text = f"{subject} {body}".lower()
        
        # Check for critical keywords
        critical_found = any(keyword in text for keyword in self.critical_keywords)
        if critical_found:
            return 'Critical'
        
        # Check for urgent keywords
        urgent_found = any(keyword in text for keyword in self.urgent_keywords)
        if urgent_found:
            return 'Urgent'
        
        return 'Normal'
    
    def _classify_category(self, subject, body):
        """Classify email into categories"""
        text = f"{subject} {body}".lower()
        
        # Simple keyword-based classification
        if any(word in text for word in ['login', 'password', 'account', 'access', 'verify']):
            return 'Account Access'
        elif any(word in text for word in ['billing', 'charge', 'payment', 'refund', 'invoice']):
            return 'Billing'
        elif any(word in text for word in ['api', 'integration', 'technical', 'code', 'development']):
            return 'Technical Support'
        elif any(word in text for word in ['pricing', 'plan', 'subscription', 'upgrade']):
            return 'Pricing'
        else:
            return 'General Support'
    
    def _extract_information(self, body):
        """Extract key information from email body"""
        extracted = {}
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, body)
        if emails:
            extracted['contact_emails'] = emails
        
        # Extract phone numbers (simple pattern)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, body)
        if phones:
            extracted['phone_numbers'] = phones
        
        # Extract common customer requests
        if 'reset password' in body.lower():
            extracted['request_type'] = 'password_reset'
        elif 'refund' in body.lower():
            extracted['request_type'] = 'refund_request'
        elif 'cancel' in body.lower():
            extracted['request_type'] = 'cancellation'
        
        return extracted
    
    def generate_response(self, email_body, sentiment, category):
        """Generate contextual AI response"""
        
        # Get relevant knowledge base content
        relevant_kb = self._get_relevant_knowledge(email_body, category)
        
        # Create context-aware prompt
        prompt = self._create_response_prompt(email_body, sentiment, category, relevant_kb)
        
        # For hackathon, we'll use template-based responses
        # In production, you'd use OpenAI API or similar
        response = self._generate_template_response(email_body, sentiment, category, relevant_kb)
        
        return response
    
    def _load_knowledge_base(self):
        """Load knowledge base for RAG"""
        return {
            'account_access': """
            For account access issues:
            1. Try resetting your password using the 'Forgot Password' link
            2. Clear your browser cache and cookies
            3. Try accessing from an incognito/private window
            4. If the issue persists, we can manually reset your account
            Contact support at support@company.com for immediate assistance.
            """,
            
            'billing': """
            For billing inquiries:
            1. You can view all charges in your account dashboard
            2. Refunds are processed within 5-7 business days
            3. For billing disputes, please provide transaction ID
            4. You can update payment methods in your account settings
            Our billing team is available at billing@company.com
            """,
            
            'technical_support': """
            For technical issues:
            1. Check our API documentation at docs.company.com
            2. Ensure you're using the latest API version
            3. Verify your API keys are correctly configured
            4. Check our status page for any ongoing issues
            Technical support: tech@company.com
            """,
            
            'general': """
            Thank you for contacting our support team. 
            We're here to help you with any questions or concerns.
            You can also check our FAQ at help.company.com
            """
        }
    
    def _get_relevant_knowledge(self, email_body, category):
        """Get relevant knowledge base content"""
        kb_key = category.lower().replace(' ', '_')
        return self.knowledge_base.get(kb_key, self.knowledge_base['general'])
    
    def _create_response_prompt(self, email_body, sentiment, category, knowledge):
        """Create prompt for response generation"""
        return f"""
        Customer Email: {email_body}
        Customer Sentiment: {sentiment}
        Issue Category: {category}
        Knowledge Base: {knowledge}
        
        Generate a professional, empathetic response.
        """
    
    def _generate_template_response(self, email_body, sentiment, category, knowledge):
        """Generate response using templates (hackathon version)"""
        
        # Greeting based on sentiment
        if sentiment == 'negative':
            greeting = "Thank you for reaching out, and I sincerely apologize for any inconvenience you've experienced."
        elif sentiment == 'positive':
            greeting = "Thank you for your message! We're happy to help."
        else:
            greeting = "Thank you for contacting our support team."
        
        # Category-specific response
        if 'account' in category.lower():
            main_response = """I understand you're having trouble with account access. Here are some immediate steps you can try:

1. Use the 'Forgot Password' link on our login page
2. Clear your browser cache and try again
3. Try accessing your account from an incognito window

If these steps don't resolve the issue, I'll be happy to manually reset your account access."""
        
        elif 'billing' in category.lower():
            main_response = """I'll help you resolve this billing concern right away. Our billing team will investigate this matter and ensure any errors are corrected promptly.

For immediate assistance with billing issues, you can also access your billing history in your account dashboard."""
        
        elif 'technical' in category.lower():
            main_response = """I'll connect you with our technical support team who specialize in API and integration issues. They'll provide you with detailed guidance to resolve this technical matter.

In the meantime, you might find our documentation helpful at docs.company.com"""
        
        else:
            main_response = """I've received your inquiry and will ensure you get the assistance you need. Our team will review your request and provide a detailed response shortly."""
        
        # Closing
        closing = """Please don't hesitate to reach out if you have any additional questions. We're committed to ensuring you have the best possible experience with our service.

Best regards,
The Support Team"""
        
        return f"{greeting}\n\n{main_response}\n\n{closing}"
