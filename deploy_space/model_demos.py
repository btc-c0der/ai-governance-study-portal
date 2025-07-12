"""
🤖 Model Demos Component
Interactive ML model demonstrations for AI governance education.
Enhanced with support for OpenAI, Mistral, and DeepSeek APIs.
"""

import gradio as gr
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Tuple, Dict, Optional
import os
import json
import asyncio
import aiohttp
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()  # For local development
# HF Spaces secrets are automatically available as os.environ

class ModelDemos:
    def __init__(self):
        self.is_spaces = os.getenv("SPACE_ID") is not None  # Detect HF Spaces environment
        self.legal_classifier = self.setup_legal_classifier()
        self.sample_documents = self.load_sample_documents()
        self.api_clients = self.setup_api_clients()
        self.rate_limiter = {}  # Simple rate limiting
        
    def setup_api_clients(self) -> Dict[str, Dict]:
        """Setup API clients for different model providers"""
        clients = {
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'model': os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                'base_url': 'https://api.openai.com/v1',
                'enabled': bool(os.getenv('OPENAI_API_KEY'))
            },
            'mistral': {
                'api_key': os.getenv('MISTRAL_API_KEY'),
                'model': os.getenv('MISTRAL_MODEL', 'mistral-large-latest'),
                'base_url': 'https://api.mistral.ai/v1',
                'enabled': bool(os.getenv('MISTRAL_API_KEY'))
            },
            'deepseek': {
                'api_key': os.getenv('DEEPSEEK_API_KEY'),
                'model': os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
                'base_url': 'https://api.deepseek.com/v1',
                'enabled': bool(os.getenv('DEEPSEEK_API_KEY'))
            }
        }
        
        # Log provider status (without exposing keys)
        if self.is_spaces:
            print("🔐 HF Spaces environment detected")
        else:
            print("💻 Local development environment")
            
        for provider, config in clients.items():
            status = "✅ Enabled" if config['enabled'] else "❌ Disabled"
            print(f"🤖 {provider.title()}: {status}")
            
        return clients
    
    def setup_legal_classifier(self):
        """Setup a simple legal document classifier for demonstration"""
        # In production, this would load a pre-trained model
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        classifier = LogisticRegression(random_state=42)
        
        # Create pipeline
        pipeline = Pipeline([
            ('vectorizer', vectorizer),
            ('classifier', classifier)
        ])
        
        # Train on sample data
        sample_texts, sample_labels = self.get_training_data()
        pipeline.fit(sample_texts, sample_labels)
        
        return pipeline
    
    def get_training_data(self):
        """Generate sample training data for the legal classifier"""
        # Sample legal documents and their risk classifications
        texts = [
            "AI system for automated loan approval based on credit scoring algorithms",
            "Chatbot for customer service inquiries and basic support",
            "Facial recognition system for building access control",
            "Recommendation engine for suggesting products to customers",
            "Automated resume screening for job applications",
            "AI-powered medical diagnosis assistance system",
            "Social media content moderation algorithm",
            "Autonomous vehicle navigation system",
            "Email spam detection and filtering system",
            "Predictive maintenance for industrial equipment",
            "Biometric identification for law enforcement",
            "AI tutor for educational content delivery",
            "Emotion recognition for marketing research",
            "Automated trading algorithm for financial markets",
            "Voice assistant for smart home control"
        ]
        
        labels = [
            "High Risk",      # Loan approval
            "Limited Risk",   # Chatbot
            "High Risk",      # Facial recognition
            "Minimal Risk",   # Recommendations
            "High Risk",      # Resume screening
            "High Risk",      # Medical diagnosis
            "Limited Risk",   # Content moderation
            "High Risk",      # Autonomous vehicles
            "Minimal Risk",   # Spam detection
            "Minimal Risk",   # Predictive maintenance
            "High Risk",      # Biometric law enforcement
            "High Risk",      # AI tutor (education)
            "High Risk",      # Emotion recognition
            "Limited Risk",   # Trading (if regulated)
            "Limited Risk"    # Voice assistant
        ]
        
        return texts, labels
    
    def load_sample_documents(self):
        """Load sample documents for testing"""
        return [
            "AI system for processing loan applications using machine learning algorithms to assess creditworthiness",
            "Customer service chatbot that answers frequently asked questions about products and services",
            "Facial recognition system used for employee access control in office buildings",
            "Recommendation algorithm that suggests products based on customer browsing history",
            "Automated system for screening job applications and ranking candidates",
            "AI-powered diagnostic tool that assists doctors in identifying medical conditions",
            "Content moderation system that automatically detects and removes inappropriate social media posts",
            "Autonomous vehicle system that makes real-time navigation and safety decisions",
            "Email filtering system that automatically identifies and blocks spam messages",
            "Predictive maintenance system that forecasts equipment failures in manufacturing"
        ]
    
    def classify_document(self, text: str) -> Tuple[str, Dict[str, float], str]:
        """Classify a document and return prediction with confidence scores"""
        if not text.strip():
            return "No text provided", {}, "Please enter text to classify"
        
        try:
            # Get prediction
            prediction = self.legal_classifier.predict([text])[0]
            
            # Get prediction probabilities
            proba = self.legal_classifier.predict_proba([text])[0]
            classes = self.legal_classifier.classes_
            
            confidence_scores = {classes[i]: float(proba[i]) for i in range(len(classes))}
            
            # Generate explanation
            explanation = self.generate_explanation(text, prediction, confidence_scores)
            
            return prediction, confidence_scores, explanation
            
        except Exception as e:
            return "Error", {}, f"Classification error: {str(e)}"
    
    def generate_explanation(self, text: str, prediction: str, scores: Dict[str, float]) -> str:
        """Generate explanation for the classification"""
        explanation = f"""
        ## 🤖 AI Classification Results
        
        **Predicted Risk Level:** {prediction}
        **Confidence:** {scores.get(prediction, 0):.2%}
        
        ### 📊 Risk Assessment Breakdown:
        """
        
        for risk_level, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            explanation += f"- **{risk_level}:** {score:.2%}\n"
        
        # Add contextual guidance
        if prediction == "High Risk":
            explanation += """
            ### ⚠️ High-Risk AI System - Key Requirements:
            - Conformity assessment before market placement
            - Technical documentation (Annex IV)
            - Risk management system implementation
            - Data governance and quality measures
            - Transparency and human oversight
            - Post-market monitoring
            """
        elif prediction == "Limited Risk":
            explanation += """
            ### 👁️ Limited Risk AI System - Key Requirements:
            - Transparency obligations (Article 52)
            - Clear disclosure of AI interaction
            - User awareness requirements
            """
        else:
            explanation += """
            ### ✅ Minimal Risk AI System:
            - No specific obligations under EU AI Act
            - General safety and fundamental rights considerations
            - Voluntary codes of conduct may apply
            """
        
        return explanation
    
    def create_feature_importance_chart(self, text: str) -> go.Figure:
        """Create feature importance visualization"""
        try:
            # Get feature names and importance scores
            vectorizer = self.legal_classifier.named_steps['vectorizer']
            classifier = self.legal_classifier.named_steps['classifier']
            
            # Transform text to get feature vector
            text_vector = vectorizer.transform([text])
            
            # Get feature names
            feature_names = vectorizer.get_feature_names_out()
            
            # Get coefficients for the predicted class
            prediction = self.legal_classifier.predict([text])[0]
            class_idx = list(self.legal_classifier.classes_).index(prediction)
            
            # Get top features
            feature_scores = classifier.coef_[class_idx] * text_vector.toarray()[0]
            
            # Get top 10 features
            top_indices = np.argsort(np.abs(feature_scores))[-10:]
            top_features = [feature_names[i] for i in top_indices]
            top_scores = [feature_scores[i] for i in top_indices]
            
            # Create bar chart
            fig = go.Figure(data=[
                go.Bar(
                    x=top_scores,
                    y=top_features,
                    orientation='h',
                    marker_color=['red' if score < 0 else 'green' for score in top_scores]
                )
            ])
            
            fig.update_layout(
                title=f"🔍 Feature Importance for '{prediction}' Classification",
                xaxis_title="Impact Score",
                yaxis_title="Features (Words)",
                height=400
            )
            
            return fig
            
        except Exception as e:
            # Return empty figure if error
            fig = go.Figure()
            fig.add_annotation(text=f"Error generating chart: {str(e)}", 
                             showarrow=False, x=0.5, y=0.5)
            return fig
    
    def create_interface(self):
        """Create the Gradio interface for model demonstrations"""
        
        gr.Markdown("## 🤖 AI Model Demonstrations")
        gr.Markdown("Interactive ML model demos for understanding AI governance and explainability.")
        
        # Check provider status
        provider_status = self.get_provider_status()
        available_providers = self.get_available_providers()
        
        if available_providers:
            gr.Markdown(f"✅ **Available AI Providers:** {', '.join([p.title() for p in available_providers])}")
        else:
            gr.Markdown("⚠️ **No AI providers configured.** Add API keys to .env file to enable AI analysis features.")
        
        with gr.Tabs():
            # Legal Document Classifier Tab
            with gr.Tab("⚖️ Legal Document Classifier"):
                gr.Markdown("### EU AI Act Risk Level Classifier")
                gr.Markdown("This demo classifies AI system descriptions according to EU AI Act risk categories.")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        # Input section
                        demo_text = gr.Textbox(
                            label="📝 AI System Description",
                            placeholder="Describe your AI system...",
                            lines=5
                        )
                        
                        # Sample documents
                        sample_dropdown = gr.Dropdown(
                            choices=[(doc[:50] + "...", doc) for doc in self.sample_documents],
                            label="📄 Or choose a sample document",
                            value=None
                        )
                        
                        classify_btn = gr.Button("🔍 Classify Document", variant="primary")
                        
                    with gr.Column(scale=2):
                        # Results section
                        classification_result = gr.Textbox(
                            label="🎯 Classification Result",
                            interactive=False
                        )
                        
                        confidence_chart = gr.Plot(label="📊 Confidence Scores")
                
                # Explanation section
                with gr.Row():
                    explanation_output = gr.Markdown(label="📖 Detailed Explanation")
                
                # Feature importance section
                with gr.Row():
                    feature_importance_chart = gr.Plot(label="🔍 Feature Importance Analysis")
            
            # AI-Powered Governance Analysis Tab
            with gr.Tab("🧠 AI-Powered Analysis"):
                gr.Markdown("### Advanced AI Governance Analysis")
                gr.Markdown("Get detailed analysis from state-of-the-art AI models.")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        # Input section
                        ai_analysis_text = gr.Textbox(
                            label="📝 AI System Description",
                            placeholder="Describe your AI system for analysis...",
                            lines=6
                        )
                        
                        # Provider selection
                        if available_providers:
                            provider_dropdown = gr.Dropdown(
                                choices=available_providers,
                                label="🤖 AI Model Provider",
                                value=available_providers[0] if available_providers else None
                            )
                        else:
                            provider_dropdown = gr.Dropdown(
                                choices=[],
                                label="🤖 AI Model Provider (None Available)",
                                value=None,
                                interactive=False
                            )
                        
                        # Analysis type
                        analysis_type = gr.Dropdown(
                            choices=[
                                ("🏛️ Governance & Compliance", "governance"),
                                ("⚖️ Bias Detection", "bias"),
                                ("🔍 Explainability Analysis", "explainability")
                            ],
                            label="📊 Analysis Type",
                            value="governance"
                        )
                        
                        ai_analyze_btn = gr.Button(
                            "🧠 Analyze with AI", 
                            variant="primary",
                            interactive=bool(available_providers)
                        )
                        
                    with gr.Column(scale=2):
                        # Results section
                        ai_analysis_result = gr.Textbox(
                            label="🤖 AI Analysis Result",
                            lines=15,
                            interactive=False
                        )
                        
                        # Provider status
                        provider_status_md = gr.Markdown(self.create_provider_status_text())
            
            # Bias Detection Tab
            with gr.Tab("🎯 Bias Detection Demo"):
                gr.Markdown("### AI Bias Detection and Mitigation")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### 📊 Synthetic Dataset Analysis")
                        
                        # Dataset parameters
                        bias_type = gr.Dropdown(
                            choices=["Gender Bias", "Age Bias", "Geographic Bias"],
                            label="Bias Type to Simulate",
                            value="Gender Bias"
                        )
                        
                        bias_strength = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.3,
                            label="Bias Strength"
                        )
                        
                        generate_btn = gr.Button("🔄 Generate Biased Dataset", variant="primary")
                        
                    with gr.Column():
                        bias_visualization = gr.Plot(label="📈 Bias Visualization")
                        
                        mitigation_suggestions = gr.Markdown(label="💡 Mitigation Recommendations")
            
            # Explainability Demo Tab
            with gr.Tab("🔍 Explainability Demo"):
                gr.Markdown("### SHAP-style Explainability")
                gr.Markdown("Understanding how AI models make decisions.")
                
                with gr.Row():
                    with gr.Column():
                        explain_text = gr.Textbox(
                            label="📝 Text to Explain",
                            placeholder="Enter text for explanation...",
                            lines=4
                        )
                        
                        explain_btn = gr.Button("🔍 Generate Explanation", variant="primary")
                        
                    with gr.Column():
                        explanation_viz = gr.Plot(label="📊 SHAP-style Explanation")
                        
                        explanation_text = gr.Markdown(label="📖 Explanation Summary")
        
        # Event handlers
        def on_classify(text, sample_selection):
            if sample_selection:
                text = sample_selection
            
            if not text.strip():
                return "No text provided", go.Figure(), "Please enter text to classify", go.Figure()
            
            # Classify document
            prediction, scores, explanation = self.classify_document(text)
            
            # Create confidence chart
            confidence_fig = go.Figure(data=[
                go.Bar(
                    x=list(scores.keys()),
                    y=list(scores.values()),
                    marker_color=['red', 'orange', 'green']
                )
            ])
            confidence_fig.update_layout(
                title="🎯 Classification Confidence",
                yaxis_title="Probability",
                xaxis_title="Risk Level"
            )
            
            # Create feature importance chart
            feature_fig = self.create_feature_importance_chart(text)
            
            return prediction, confidence_fig, explanation, feature_fig
        
        def on_ai_analyze(text, provider, analysis_type):
            if not text.strip():
                return "Please enter text to analyze"
            
            if not provider:
                return "Please select an AI provider"
            
            return self.analyze_with_ai(text, provider, analysis_type)
        
        def on_sample_select(sample):
            return sample if sample else ""
        
        def generate_bias_demo(bias_type, strength):
            """Generate bias visualization"""
            # Create synthetic biased data
            np.random.seed(42)
            
            if bias_type == "Gender Bias":
                categories = ['Male', 'Female']
                # Simulate biased hiring data
                male_success = 0.7 + strength * 0.2
                female_success = 0.7 - strength * 0.2
                
                data = {
                    'Category': categories,
                    'Success_Rate': [male_success, female_success],
                    'Sample_Size': [1000, 1000]
                }
            else:
                # Similar logic for other bias types
                categories = ['Group A', 'Group B']
                data = {
                    'Category': categories,
                    'Success_Rate': [0.7 + strength * 0.2, 0.7 - strength * 0.2],
                    'Sample_Size': [1000, 1000]
                }
            
            fig = go.Figure(data=[
                go.Bar(
                    x=data['Category'],
                    y=data['Success_Rate'],
                    marker_color=['blue', 'red']
                )
            ])
            
            fig.update_layout(
                title=f"📊 {bias_type} Simulation (Strength: {strength:.1f})",
                yaxis_title="Success Rate",
                xaxis_title="Category"
            )
            
            # Generate mitigation suggestions
            suggestions = f"""
            ## 💡 Bias Mitigation Recommendations
            
            **Detected Bias Level:** {strength:.1%}
            
            ### 🛠️ Mitigation Strategies:
            1. **Data Augmentation:** Increase representation of underrepresented groups
            2. **Algorithmic Debiasing:** Apply fairness constraints during training
            3. **Post-processing:** Adjust model outputs to ensure fairness
            4. **Continuous Monitoring:** Implement ongoing bias detection
            
            ### 📊 Fairness Metrics to Track:
            - Demographic parity
            - Equal opportunity
            - Equalized odds
            - Individual fairness
            """
            
            return fig, suggestions
        
        # Wire up event handlers
        classify_btn.click(
            fn=on_classify,
            inputs=[demo_text, sample_dropdown],
            outputs=[classification_result, confidence_chart, explanation_output, feature_importance_chart]
        )
        
        # AI Analysis handler
        if available_providers:
            ai_analyze_btn.click(
                fn=on_ai_analyze,
                inputs=[ai_analysis_text, provider_dropdown, analysis_type],
                outputs=[ai_analysis_result]
            )
        
        sample_dropdown.change(
            fn=on_sample_select,
            inputs=[sample_dropdown],
            outputs=[demo_text]
        )
        
        generate_btn.click(
            fn=generate_bias_demo,
            inputs=[bias_type, bias_strength],
            outputs=[bias_visualization, mitigation_suggestions]
        )
        
        return demo_text, classification_result, explanation_output
    
    def check_rate_limit(self, provider: str) -> bool:
        """Simple rate limiting check"""
        current_time = time.time()
        
        # Get rate limit and handle comments in env var
        rate_limit_str = os.getenv('DEMO_RATE_LIMIT', '10')
        try:
            # Split on # to remove comments
            rate_limit = int(rate_limit_str.split('#')[0].strip())
        except ValueError:
            rate_limit = 10  # Default fallback
        
        if provider not in self.rate_limiter:
            self.rate_limiter[provider] = []
        
        # Clean old requests (older than 1 minute)
        self.rate_limiter[provider] = [
            req_time for req_time in self.rate_limiter[provider]
            if current_time - req_time < 60
        ]
        
        if len(self.rate_limiter[provider]) >= rate_limit:
            return False
        
        self.rate_limiter[provider].append(current_time)
        return True
    
    async def call_ai_model(self, provider: str, prompt: str, system_prompt: str = None) -> str:
        """Make API call to AI model provider"""
        if not self.api_clients[provider]['enabled']:
            return f"❌ {provider.title()} API key not configured"
        
        if not self.check_rate_limit(provider):
            return f"⚠️ Rate limit exceeded for {provider.title()}. Please try again in a moment."
        
        try:
            client_config = self.api_clients[provider]
            
            headers = {
                'Authorization': f'Bearer {client_config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Prepare request data
            data = {
                "model": client_config["model"],
                "messages": messages,
                "max_tokens": int(os.getenv('MAX_TOKENS', '2000').split('#')[0].strip()),
                "temperature": float(os.getenv('TEMPERATURE', '0.7').split('#')[0].strip())
            }
            
            # Make API call
            async with aiohttp.ClientSession() as session:
                timeout_seconds = int(os.getenv('API_TIMEOUT', '30').split('#')[0].strip())
                async with session.post(
                    f"{client_config['base_url']}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=timeout_seconds)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        error_text = await response.text()
                        return f"❌ API Error ({response.status}): {error_text}"
        
        except asyncio.TimeoutError:
            return f"⏱️ Request timeout for {provider.title()} API"
        except Exception as e:
            return f"❌ Error calling {provider.title()} API: {str(e)}"
    
    def analyze_with_ai(self, text: str, provider: str, analysis_type: str) -> str:
        """Analyze text with AI model"""
        if not os.getenv('ENABLE_AI_DEMOS', 'true').lower() == 'true':
            return "❌ AI demos are disabled in configuration"
        
        if analysis_type == "governance":
            system_prompt = """You are an AI governance expert. Analyze the provided AI system description and provide:
1. EU AI Act risk classification (Minimal, Limited, High, or Prohibited)
2. Key compliance requirements
3. Potential governance challenges
4. Mitigation recommendations

Be specific and reference relevant EU AI Act articles where applicable."""
            
            prompt = f"Please analyze this AI system description for governance implications:\n\n{text}"
            
        elif analysis_type == "bias":
            system_prompt = """You are an AI bias detection expert. Analyze the provided text for potential bias issues and provide:
1. Identified bias types (if any)
2. Bias severity assessment
3. Affected groups or demographics
4. Mitigation strategies
5. Fairness metrics to monitor

Focus on practical, actionable insights."""
            
            prompt = f"Please analyze this text for potential bias issues:\n\n{text}"
            
        elif analysis_type == "explainability":
            system_prompt = """You are an AI explainability expert. Analyze the provided AI system and provide:
1. Explainability requirements based on use case
2. Recommended explanation techniques
3. Stakeholder-specific explanation needs
4. Technical implementation suggestions

Focus on practical explainability solutions."""
            
            prompt = f"Please analyze this AI system for explainability requirements:\n\n{text}"
            
        else:
            return "❌ Unknown analysis type"
        
        # Run async function in sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.call_ai_model(provider, prompt, system_prompt))
    
    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers"""
        return [provider for provider, config in self.api_clients.items() if config['enabled']]
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all providers"""
        return {provider: config['enabled'] for provider, config in self.api_clients.items()}
    
    def create_provider_status_text(self) -> str:
        """Create provider status text for display"""
        status = self.get_provider_status()
        text = "### 🔌 Provider Status\n\n"
        
        for provider, enabled in status.items():
            icon = "✅" if enabled else "❌"
            model = self.api_clients[provider]['model']
            text += f"{icon} **{provider.title()}**: {model if enabled else 'Not configured'}\n"
        
        if not any(status.values()):
            if self.is_spaces:
                text += "\n⚠️ **Hugging Face Spaces Setup:**\n"
                text += "1. Go to your Space **Settings** tab\n"
                text += "2. Add **Repository secrets**:\n"
                text += "   - `OPENAI_API_KEY`: Your OpenAI key\n"
                text += "   - `MISTRAL_API_KEY`: Your Mistral key\n"
                text += "   - `DEEPSEEK_API_KEY`: Your DeepSeek key\n"
                text += "3. **Restart** the Space\n"
                text += "\n🔐 **API keys are stored securely** as HF Spaces secrets\n"
            else:
                text += "\n⚠️ **Local Development Setup:**\n"
                text += "1. Copy `.env.example` to `.env`\n"
                text += "2. Add your API keys to `.env`\n"
                text += "3. Restart the application\n"
        
        environment = "🔐 Hugging Face Spaces" if self.is_spaces else "💻 Local Development"
        text += f"\n**Environment**: {environment}\n"
        
        return text