"""
🧠 AI Tutor Component
Intelligent tutoring system for AI governance and AIGP exam preparation.
"""

import gradio as gr
import json
from datetime import datetime
from typing import List, Dict, Tuple
import random

class AITutor:
    def __init__(self):
        self.knowledge_base = self.load_knowledge_base()
        self.conversation_history = []
        self.quiz_bank = self.load_quiz_questions()
    
    def load_knowledge_base(self):
        """Load AI governance knowledge base"""
        return {
            "eu_ai_act": {
                "overview": "The EU AI Act is the world's first comprehensive AI regulation, establishing a risk-based approach to AI governance.",
                "key_concepts": [
                    "Risk-based approach with 4 categories",
                    "Prohibited AI practices",
                    "High-risk AI system requirements",
                    "Transparency obligations",
                    "Conformity assessment procedures"
                ],
                "timeline": {
                    "2024-08-01": "Regulation enters into force",
                    "2025-02-02": "Prohibited AI practices ban begins",
                    "2026-08-02": "Full application for high-risk systems"
                }
            },
            "aigp_certification": {
                "overview": "AIGP (Artificial Intelligence Governance Professional) certification demonstrates expertise in AI governance and compliance.",
                "domains": [
                    "AI Governance Fundamentals",
                    "Risk Management",
                    "Regulatory Compliance",
                    "Ethics and Bias Mitigation",
                    "Technical Implementation"
                ],
                "exam_format": {
                    "questions": 100,
                    "duration": "2 hours",
                    "passing_score": "70%",
                    "question_types": ["Multiple choice", "Scenario-based"]
                }
            },
            "risk_management": {
                "frameworks": [
                    "NIST AI Risk Management Framework",
                    "ISO/IEC 23053",
                    "EU AI Act requirements",
                    "Industry-specific guidelines"
                ],
                "key_processes": [
                    "Risk identification",
                    "Risk assessment",
                    "Risk mitigation",
                    "Continuous monitoring"
                ]
            }
        }
    
    def load_quiz_questions(self):
        """Load sample AIGP quiz questions"""
        return [
            {
                "question": "Which of the following AI practices is explicitly prohibited under the EU AI Act?",
                "options": [
                    "Chatbots that disclose they are AI systems",
                    "AI systems that exploit vulnerabilities of specific groups",
                    "High-risk AI systems without conformity assessment",
                    "AI systems that require human oversight"
                ],
                "correct": 1,
                "explanation": "Article 5 of the EU AI Act prohibits AI systems that exploit vulnerabilities of specific groups due to age, disability, or socioeconomic circumstances."
            },
            {
                "question": "What is the main purpose of Annex IV in the EU AI Act?",
                "options": [
                    "Lists prohibited AI practices",
                    "Defines AI system categories",
                    "Specifies technical documentation requirements",
                    "Outlines penalty structures"
                ],
                "correct": 2,
                "explanation": "Annex IV details the technical documentation requirements that providers of high-risk AI systems must prepare and maintain."
            },
            {
                "question": "Which risk management principle is most important for high-risk AI systems?",
                "options": [
                    "Cost minimization",
                    "Continuous iterative process",
                    "Maximum automation",
                    "Regulatory avoidance"
                ],
                "correct": 1,
                "explanation": "Article 9 emphasizes that risk management must be a continuous, iterative process throughout the AI system lifecycle."
            }
        ]
    
    def generate_response(self, user_message: str, history: List[Tuple[str, str]]) -> str:
        """Generate tutor response based on user message and conversation history"""
        
        # Store conversation
        self.conversation_history.append(("user", user_message))
        
        # Simple rule-based response generation
        response = self.process_query(user_message.lower())
        
        self.conversation_history.append(("assistant", response))
        
        return response
    
    def process_query(self, query: str) -> str:
        """Process user query and generate appropriate response"""
        
        # EU AI Act queries
        if any(term in query for term in ["eu ai act", "ai act", "regulation"]):
            if "prohibited" in query or "banned" in query:
                return """
                ## 🚫 Prohibited AI Practices (Article 5)
                
                The EU AI Act prohibits AI systems that:
                
                1. **Subliminal techniques** - Deploy techniques beyond consciousness to alter behavior
                2. **Exploit vulnerabilities** - Target specific groups based on age, disability, or socioeconomic status
                3. **Social scoring** - General social scoring by public authorities
                4. **Real-time biometric identification** - In public spaces by law enforcement (with limited exceptions)
                
                💡 **Key Point:** These prohibitions are absolute - such systems cannot be placed on the market or used in the EU.
                """
            
            elif "high risk" in query or "high-risk" in query:
                return """
                ## ⚠️ High-Risk AI Systems
                
                ### Classification Criteria:
                - Used as safety components in regulated products, OR
                - Standalone systems in Annex III areas with significant risk
                
                ### Key Requirements:
                1. **Risk management system** (Article 9)
                2. **Data governance** (Article 10)
                3. **Technical documentation** (Annex IV)
                4. **Transparency** (Article 13)
                5. **Human oversight** (Article 14)
                6. **Conformity assessment** before market placement
                
                ### Annex III Areas:
                - Critical infrastructures
                - Education and training
                - Employment and HR
                - Essential services access
                - Law enforcement
                - Migration and border control
                - Justice and democratic processes
                """
            
            else:
                return """
                ## ⚖️ EU AI Act Overview
                
                The EU AI Act establishes a **risk-based approach** to AI regulation:
                
                ### 🔴 **Unacceptable Risk** - Prohibited
                - Subliminal techniques
                - Exploitation of vulnerabilities
                - Social scoring (public authorities)
                - Real-time biometric ID (with exceptions)
                
                ### 🟠 **High Risk** - Strict Requirements
                - Safety components in regulated products
                - Standalone systems in sensitive areas
                - Requires conformity assessment
                
                ### 🟡 **Limited Risk** - Transparency
                - Human interaction disclosure
                - Emotion recognition transparency
                - Deepfake labeling
                
                ### 🟢 **Minimal Risk** - No Restrictions
                - Voluntary codes of conduct
                - General safety considerations
                
                Would you like me to elaborate on any specific risk category?
                """
        
        # AIGP certification queries
        elif any(term in query for term in ["aigp", "certification", "exam"]):
            if "exam" in query or "test" in query:
                return """
                ## 🎓 AIGP Certification Exam
                
                ### Exam Format:
                - **100 multiple-choice questions**
                - **2 hours duration**
                - **70% passing score**
                - **Scenario-based questions**
                
                ### Knowledge Domains:
                1. **AI Governance Fundamentals** (25%)
                2. **Risk Management** (20%)
                3. **Regulatory Compliance** (25%)
                4. **Ethics and Bias** (15%)
                5. **Technical Implementation** (15%)
                
                ### Study Tips:
                - Focus on EU AI Act articles and requirements
                - Understand risk categorization thoroughly
                - Practice scenario-based questions
                - Review global AI governance frameworks
                
                Would you like me to quiz you on specific topics?
                """
            
            else:
                return """
                ## 🧠 AIGP Certification Overview
                
                The **Artificial Intelligence Governance Professional (AIGP)** certification demonstrates expertise in:
                
                ### Core Competencies:
                - AI governance frameworks and principles
                - Regulatory compliance (EU AI Act, GDPR, etc.)
                - Risk management methodologies
                - Ethics and bias mitigation
                - Technical implementation strategies
                
                ### Career Benefits:
                - Recognized expertise in AI governance
                - Competitive advantage in AI/ML roles
                - Networking with governance professionals
                - Continuous learning opportunities
                
                ### Preparation Resources:
                - Official study guides
                - Practice exams
                - Industry case studies
                - Regulatory updates
                
                Ready to start your preparation journey?
                """
        
        # Risk management queries
        elif any(term in query for term in ["risk", "management", "assessment"]):
            return """
            ## 📊 AI Risk Management
            
            ### Risk Management Framework (Article 9):
            
            #### 🔍 **Risk Identification**
            - Known and foreseeable risks
            - Intended use and reasonably foreseeable misuse
            - Impact on health, safety, fundamental rights
            
            #### 📈 **Risk Assessment**
            - Probability and severity analysis
            - Risk estimation methodologies
            - Consideration of user groups
            
            #### 🛡️ **Risk Mitigation**
            - Design and development measures
            - Adequate testing and validation
            - Information and training for users
            
            #### 🔄 **Continuous Process**
            - Regular review and updates
            - Post-market monitoring
            - Incident response procedures
            
            ### Key Principles:
            - Proportionate to risk level
            - Documented and systematic
            - Integrated into development lifecycle
            - Stakeholder involvement
            """
        
        # Bias and ethics queries
        elif any(term in query for term in ["bias", "ethics", "fairness"]):
            return """
            ## 🎯 AI Ethics and Bias Mitigation
            
            ### Data Governance (Article 10):
            - **Representative datasets** - Reflect intended use
            - **Error detection** - Identify and correct data issues
            - **Bias monitoring** - Continuous assessment
            - **Statistical properties** - Appropriate for task
            
            ### Bias Types to Address:
            1. **Historical bias** - Reflected in training data
            2. **Representation bias** - Underrepresented groups
            3. **Evaluation bias** - Unfair performance metrics
            4. **Aggregation bias** - Inappropriate data combining
            
            ### Mitigation Strategies:
            - Diverse and inclusive datasets
            - Algorithmic fairness techniques
            - Regular bias auditing
            - Stakeholder engagement
            - Continuous monitoring
            
            ### Fairness Metrics:
            - Demographic parity
            - Equal opportunity
            - Equalized odds
            - Individual fairness
            """
        
        # Technical implementation queries
        elif any(term in query for term in ["technical", "implementation", "documentation"]):
            return """
            ## 🔧 Technical Implementation Requirements
            
            ### Annex IV Technical Documentation:
            
            #### 📋 **System Description**
            - General description and intended use
            - Person responsible for development
            - Date and version identification
            
            #### 🏗️ **System Elements**
            - System architecture and design
            - Algorithms and model information
            - Data requirements and characteristics
            
            #### 🛡️ **Risk Management**
            - Risk management system documentation
            - Risk assessment and mitigation measures
            - Testing and validation procedures
            
            #### 📊 **Data Governance**
            - Data governance measures
            - Training, validation, testing datasets
            - Data quality and bias assessment
            
            #### 👥 **Human Oversight**
            - Human oversight measures
            - User interface design
            - User training requirements
            
            ### Quality Management System:
            - Strategy and governance
            - Resource management
            - Process documentation
            - Continuous improvement
            """
        
        # Quiz request
        elif any(term in query for term in ["quiz", "question", "test me", "practice"]):
            return self.generate_quiz_question()
        
        # General help
        else:
            return """
            ## 👋 Welcome to AI Governance Tutor!
            
            I'm here to help you master AI governance and prepare for the AIGP certification. 
            
            ### What I can help with:
            - **EU AI Act** - Articles, requirements, compliance
            - **AIGP Certification** - Exam prep, study guidance
            - **Risk Management** - Frameworks, assessment, mitigation
            - **Ethics & Bias** - Detection, mitigation strategies
            - **Technical Implementation** - Documentation, systems
            
            ### Try asking me:
            - "Explain high-risk AI systems"
            - "What's prohibited under the EU AI Act?"
            - "How do I prepare for the AIGP exam?"
            - "Quiz me on AI governance"
            - "What are the technical documentation requirements?"
            
            What would you like to learn about today?
            """
    
    def generate_quiz_question(self) -> str:
        """Generate a random quiz question"""
        question = random.choice(self.quiz_bank)
        
        quiz_html = f"""
        ## 🧪 AIGP Practice Question
        
        **Question:** {question['question']}
        
        **Options:**
        A) {question['options'][0]}
        B) {question['options'][1]}
        C) {question['options'][2]}
        D) {question['options'][3]}
        
        ---
        
        **Answer:** {chr(65 + question['correct'])} - {question['options'][question['correct']]}
        
        **Explanation:** {question['explanation']}
        
        ---
        
        💡 **Study Tip:** Focus on understanding the reasoning behind each answer rather than memorizing facts.
        
        Ready for another question? Just ask!
        """
        
        return quiz_html
    
    def create_interface(self):
        """Create the Gradio interface for AI tutoring"""
        
        gr.Markdown("## 🧠 AI Governance Tutor")
        gr.Markdown("Your intelligent study companion for AI governance and AIGP certification preparation.")
        
        with gr.Row():
            with gr.Column(scale=3):
                # Chat interface
                chatbot = gr.Chatbot(
                    label="💬 Chat with AI Tutor",
                    height=500,
                    show_copy_button=True
                )
                
                with gr.Row():
                    msg_input = gr.Textbox(
                        label="Your Question",
                        placeholder="Ask me anything about AI governance...",
                        scale=4
                    )
                    send_btn = gr.Button("📤 Send", variant="primary", scale=1)
                    clear_btn = gr.Button("🗑️ Clear", variant="secondary", scale=1)
                
                # Quick action buttons
                with gr.Row():
                    quiz_btn = gr.Button("🧪 Quiz Me", size="sm")
                    eu_act_btn = gr.Button("⚖️ EU AI Act", size="sm")
                    aigp_btn = gr.Button("🎓 AIGP Exam", size="sm")
                    risk_btn = gr.Button("📊 Risk Mgmt", size="sm")
            
            with gr.Column(scale=1):
                # Study resources and tips
                gr.Markdown("### 📚 Quick References")
                
                study_tips = gr.Markdown("""
                #### 💡 Study Tips:
                - Focus on EU AI Act structure
                - Understand risk categorization
                - Practice scenario questions
                - Review case studies
                - Join study groups
                
                #### 🎯 Key Topics:
                - Article 5 (Prohibited practices)
                - Article 6 (High-risk classification)
                - Article 9 (Risk management)
                - Article 10 (Data governance)
                - Annex IV (Documentation)
                
                #### 📖 Resources:
                - EU AI Act full text
                - AIGP study guides
                - Practice exams
                - Industry case studies
                """)
                
                # Progress tracking
                gr.Markdown("### 📈 Study Progress")
                progress_display = gr.HTML("""
                <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); 
                            color: white; padding: 1.5rem; border-radius: 12px;
                            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                    <h4 style="color: #fbbf24; margin-top: 0; font-size: 1.3rem;">🎯 Your Progress</h4>
                    <p style="color: #f3f4f6; margin: 0.5rem 0;">
                        Questions asked: <strong style="color: #fbbf24;">0</strong>
                    </p>
                    <p style="color: #f3f4f6; margin: 0.5rem 0;">
                        Topics covered: <strong style="color: #fbbf24;">0</strong>
                    </p>
                    <p style="color: #f3f4f6; margin: 0.5rem 0;">
                        Quiz questions: <strong style="color: #fbbf24;">0</strong>
                    </p>
                </div>
                """)
        
        # Event handlers
        def respond(message, history):
            if not message.strip():
                return history, ""
            
            response = self.generate_response(message, history)
            history.append((message, response))
            return history, ""
        
        def quick_quiz():
            return self.generate_quiz_question()
        
        def quick_eu_act():
            return "Tell me about the EU AI Act"
        
        def quick_aigp():
            return "How do I prepare for the AIGP certification exam?"
        
        def quick_risk():
            return "Explain AI risk management frameworks"
        
        # Wire up events
        msg_input.submit(respond, [msg_input, chatbot], [chatbot, msg_input])
        send_btn.click(respond, [msg_input, chatbot], [chatbot, msg_input])
        clear_btn.click(lambda: ([], ""), outputs=[chatbot, msg_input])
        
        # Quick buttons
        quiz_btn.click(lambda: quick_quiz(), outputs=[msg_input])
        eu_act_btn.click(lambda: quick_eu_act(), outputs=[msg_input])
        aigp_btn.click(lambda: quick_aigp(), outputs=[msg_input])
        risk_btn.click(lambda: quick_risk(), outputs=[msg_input])
        
        return chatbot, msg_input 