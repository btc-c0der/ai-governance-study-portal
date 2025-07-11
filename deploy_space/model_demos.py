"""
🤖 Model Demos Component
Interactive ML model demonstrations for AI governance education.
"""

import gradio as gr
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Tuple, Dict

class ModelDemos:
    def __init__(self):
        self.legal_classifier = self.setup_legal_classifier()
        self.sample_documents = self.load_sample_documents()
    
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