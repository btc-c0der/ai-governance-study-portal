"""
⚖️ EU AI Act Explorer Component
Interactive exploration of EU AI Act articles, annexes, and compliance requirements.
"""

import gradio as gr
import json
import pandas as pd
from pathlib import Path
import re
from typing import List, Dict, Any

class AIActExplorer:
    def __init__(self):
        self.ai_act_data = self.load_ai_act_data()
        self.search_index = self.build_search_index()
    
    def load_ai_act_data(self):
        """Load structured EU AI Act data"""
        data_path = Path("components/ai_act_articles.json")
        
        if not data_path.exists():
            return self.create_default_ai_act_data()
        
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return self.create_default_ai_act_data()
    
    def create_default_ai_act_data(self):
        """Create comprehensive EU AI Act article structure"""
        return {
            "title": "Regulation (EU) 2024/1689 - EU AI Act",
            "effective_date": "2024-08-01",
            "full_application_date": "2026-08-02",
            "articles": [
                {
                    "number": "Article 1",
                    "title": "Subject matter and scope",
                    "category": "General Provisions",
                    "content": "This Regulation lays down harmonised rules for the placing on the market, the putting into service and the use of artificial intelligence systems in the Union.",
                    "key_points": [
                        "Establishes harmonized AI rules across EU",
                        "Covers AI systems placed on market or put into service",
                        "Defines territorial and material scope"
                    ],
                    "compliance_impact": "Foundation - defines what AI systems are covered",
                    "relevant_stakeholders": ["AI developers", "Deployers", "Importers", "Distributors"]
                },
                {
                    "number": "Article 3",
                    "title": "Definitions",
                    "category": "General Provisions", 
                    "content": "For the purposes of this Regulation, the following definitions apply: 'artificial intelligence system' means a machine-based system...",
                    "key_points": [
                        "Defines 'AI system' with broad, technology-neutral approach",
                        "Includes key terms: provider, deployer, user, etc.",
                        "Establishes legal terminology for compliance"
                    ],
                    "compliance_impact": "Critical - determines if your system falls under regulation",
                    "relevant_stakeholders": ["All AI stakeholders", "Legal teams", "Compliance officers"]
                },
                {
                    "number": "Article 5",
                    "title": "Prohibited artificial intelligence practices",
                    "category": "Prohibited Practices",
                    "content": "The following artificial intelligence practices shall be prohibited: (a) the placing on the market, the putting into service or the use of an AI system that deploys subliminal techniques...",
                    "key_points": [
                        "Subliminal techniques beyond consciousness",
                        "Exploitation of vulnerabilities (age, disability, etc.)",
                        "Social scoring by public authorities",
                        "Real-time biometric identification in public spaces (with exceptions)"
                    ],
                    "compliance_impact": "Absolute prohibition - violating systems must be withdrawn",
                    "relevant_stakeholders": ["All AI providers", "Public authorities", "Law enforcement"]
                },
                {
                    "number": "Article 6",
                    "title": "Classification rules for high-risk AI systems",
                    "category": "High-Risk AI Systems",
                    "content": "AI systems shall be considered high-risk AI systems where both of the following conditions are fulfilled: (a) the AI system is intended to be used as a safety component...",
                    "key_points": [
                        "Two-step classification process",
                        "Safety component of regulated products",
                        "Standalone systems in Annex III areas",
                        "Significant risk of harm to health, safety, fundamental rights"
                    ],
                    "compliance_impact": "Determines if extensive obligations apply",
                    "relevant_stakeholders": ["AI providers", "Risk managers", "Product teams"]
                },
                {
                    "number": "Article 9",
                    "title": "Risk management system",
                    "category": "High-Risk AI Systems",
                    "content": "Providers of high-risk AI systems shall establish, implement, document and maintain a risk management system.",
                    "key_points": [
                        "Continuous iterative process",
                        "Risk identification and analysis",
                        "Risk estimation and evaluation",
                        "Risk mitigation measures"
                    ],
                    "compliance_impact": "Core requirement - must be established before deployment",
                    "relevant_stakeholders": ["Risk managers", "AI providers", "Quality teams"]
                },
                {
                    "number": "Article 10",
                    "title": "Data and data governance",
                    "category": "High-Risk AI Systems",
                    "content": "High-risk AI systems which make use of techniques involving the training of models with data shall be developed on the basis of training, validation and testing data sets that meet the quality criteria...",
                    "key_points": [
                        "Data quality requirements",
                        "Representative, error-free, complete datasets",
                        "Appropriate statistical properties",
                        "Bias detection and mitigation"
                    ],
                    "compliance_impact": "Fundamental - affects model development process",
                    "relevant_stakeholders": ["Data scientists", "ML engineers", "Data governance teams"]
                },
                {
                    "number": "Article 13",
                    "title": "Transparency and provision of information to deployers",
                    "category": "High-Risk AI Systems",
                    "content": "High-risk AI systems shall be designed and developed in such a way as to ensure that their operation is sufficiently transparent to enable deployers to interpret the system's output and use it appropriately.",
                    "key_points": [
                        "Interpretability for deployers",
                        "Clear and comprehensive instructions",
                        "Information about system capabilities and limitations",
                        "Expected level of accuracy"
                    ],
                    "compliance_impact": "Essential for deployment - affects user interface design",
                    "relevant_stakeholders": ["UX designers", "Technical writers", "Product managers"]
                },
                {
                    "number": "Article 14",
                    "title": "Human oversight",
                    "category": "High-Risk AI Systems", 
                    "content": "High-risk AI systems shall be designed and developed in such a way, including with appropriate human-machine interface tools, that they can be effectively overseen by natural persons during the period in which the AI system is in use.",
                    "key_points": [
                        "Meaningful human oversight during operation",
                        "Human-machine interface requirements",
                        "Ability to interrupt or override system",
                        "Understanding of system capabilities and limitations"
                    ],
                    "compliance_impact": "Operational requirement - affects system design and deployment",
                    "relevant_stakeholders": ["System operators", "UX designers", "Operations teams"]
                },
                {
                    "number": "Article 16",
                    "title": "Obligations of providers of high-risk AI systems",
                    "category": "High-Risk AI Systems",
                    "content": "Before placing a high-risk AI system on the market or putting it into service, providers shall: (a) ensure that the system has been subject to the relevant conformity assessment procedure...",
                    "key_points": [
                        "Conformity assessment before market placement",
                        "Quality management system establishment",
                        "Technical documentation preparation",
                        "CE marking and declaration of conformity"
                    ],
                    "compliance_impact": "Pre-market obligations - affects go-to-market timeline",
                    "relevant_stakeholders": ["Compliance teams", "Legal teams", "Product managers"]
                },
                {
                    "number": "Article 52",
                    "title": "Transparency obligations for certain AI systems",
                    "category": "Limited Risk AI Systems",
                    "content": "Providers shall ensure that AI systems intended to interact with natural persons are designed and developed in such a way that natural persons are informed that they are interacting with an AI system...",
                    "key_points": [
                        "Clear disclosure of AI interaction",
                        "Emotion recognition and biometric categorisation transparency",
                        "Deep fake and AI-generated content labeling",
                        "Clear and distinguishable information"
                    ],
                    "compliance_impact": "User interface requirement - affects customer-facing systems",
                    "relevant_stakeholders": ["Product teams", "UX designers", "Marketing teams"]
                }
            ],
            "annexes": {
                "annex_i": {
                    "title": "Artificial intelligence techniques and approaches",
                    "description": "Lists AI techniques covered by the regulation",
                    "items": [
                        "Machine learning approaches",
                        "Logic- and knowledge-based approaches", 
                        "Statistical approaches"
                    ]
                },
                "annex_iii": {
                    "title": "High-risk AI systems",
                    "description": "Areas where AI systems are considered high-risk",
                    "categories": [
                        "Critical infrastructures",
                        "Education and vocational training",
                        "Employment and workers management",
                        "Access to essential services",
                        "Law enforcement",
                        "Migration, asylum and border control",
                        "Administration of justice and democratic processes"
                    ]
                },
                "annex_iv": {
                    "title": "Technical documentation",
                    "description": "Required technical documentation for high-risk AI systems",
                    "sections": [
                        "General description of the AI system",
                        "Detailed description of system elements",
                        "Risk management system",
                        "Data governance measures"
                    ]
                }
            }
        }
    
    def build_search_index(self):
        """Build searchable index of articles and content"""
        index = []
        for article in self.ai_act_data['articles']:
            index.append({
                'id': article['number'],
                'title': article['title'],
                'category': article['category'],
                'content': article['content'],
                'key_points': ' '.join(article['key_points']),
                'searchable_text': f"{article['title']} {article['content']} {' '.join(article['key_points'])}"
            })
        return index
    
    def search_articles(self, query: str, category_filter: str = "All") -> List[Dict[str, Any]]:
        """Search articles based on query and filters"""
        if not query.strip():
            articles = self.ai_act_data['articles']
        else:
            # Simple text matching - in production, use more sophisticated search
            query_lower = query.lower()
            articles = []
            for article in self.ai_act_data['articles']:
                searchable = f"{article['title']} {article['content']} {' '.join(article['key_points'])}".lower()
                if query_lower in searchable:
                    articles.append(article)
        
        # Apply category filter
        if category_filter != "All":
            articles = [a for a in articles if a['category'] == category_filter]
        
        return articles
    
    def create_interface(self):
        """Create the Gradio interface for AI Act exploration"""
        
        gr.Markdown("## ⚖️ EU AI Act Interactive Explorer")
        gr.Markdown("Search and explore EU AI Act articles, requirements, and compliance guidance.")
        
        with gr.Row():
            with gr.Column(scale=1):
                # Search and filter controls
                search_query = gr.Textbox(
                    label="🔍 Search Articles",
                    placeholder="e.g., high-risk, biometric, transparency..."
                )
                
                category_filter = gr.Dropdown(
                    choices=["All", "General Provisions", "Prohibited Practices", 
                            "High-Risk AI Systems", "Limited Risk AI Systems"],
                    label="📂 Filter by Category",
                    value="All"
                )
                
                search_btn = gr.Button("🔍 Search", variant="primary")
                
                # Quick access buttons
                gr.Markdown("### ⚡ Quick Access")
                prohibited_btn = gr.Button("🚫 Prohibited Practices", size="sm")
                high_risk_btn = gr.Button("⚠️ High-Risk Requirements", size="sm")
                transparency_btn = gr.Button("👁️ Transparency Rules", size="sm")
                
            with gr.Column(scale=2):
                # Results display
                search_results = gr.HTML(label="Search Results")
                
                # Article detail view
                article_detail = gr.HTML(label="Article Details")
        
        with gr.Row():
            # Compliance wizard
            with gr.Column():
                gr.Markdown("### 🧭 Compliance Quick Check")
                system_description = gr.Textbox(
                    label="Describe your AI system",
                    placeholder="e.g., Chatbot for customer service, ML model for loan approval..."
                )
                check_compliance_btn = gr.Button("✅ Check Compliance Requirements", variant="secondary")
                compliance_result = gr.HTML(label="Compliance Assessment")
        
        # Search functionality
        def perform_search(query, category):
            articles = self.search_articles(query, category)
            
            if not articles:
                return "<p>No articles found matching your search criteria.</p>"
            
            html_results = "<div style='max-height: 400px; overflow-y: auto;'>"
            for article in articles:
                html_results += f"""
                <div style='border: 1px solid #e5e7eb; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; cursor: pointer;'
                     onclick='selectArticle("{article["number"]}")'>
                    <h4 style='color: #1f2937; margin: 0 0 0.5rem 0;'>{article['number']}: {article['title']}</h4>
                    <p style='color: #6b7280; font-size: 0.9rem; margin: 0 0 0.5rem 0;'>Category: {article['category']}</p>
                    <p style='margin: 0; font-size: 0.9rem;'>{article['content'][:200]}...</p>
                </div>
                """
            html_results += "</div>"
            
            return html_results
        
        def show_article_details(article_number):
            """Display detailed article information"""
            article = next((a for a in self.ai_act_data['articles'] if a['number'] == article_number), None)
            
            if not article:
                return "Article not found"
            
            html_detail = f"""
            <div style='background: #f8fafc; padding: 1.5rem; border-radius: 10px;'>
                <h3 style='color: #1f2937; margin-top: 0;'>{article['number']}: {article['title']}</h3>
                <p><strong>Category:</strong> {article['category']}</p>
                
                <h4>📖 Full Text:</h4>
                <p style='font-style: italic; background: white; padding: 1rem; border-radius: 5px;'>
                    {article['content']}
                </p>
                
                <h4>🎯 Key Points:</h4>
                <ul>
                    {''.join([f'<li>{point}</li>' for point in article['key_points']])}
                </ul>
                
                <h4>⚖️ Compliance Impact:</h4>
                <p style='background: #fef3c7; padding: 0.75rem; border-radius: 5px; color: #92400e;'>
                    {article['compliance_impact']}
                </p>
                
                <h4>👥 Relevant Stakeholders:</h4>
                <p>{', '.join(article['relevant_stakeholders'])}</p>
            </div>
            """
            
            return html_detail
        
        def quick_access_prohibited():
            return perform_search("prohibited", "Prohibited Practices")
        
        def quick_access_high_risk():
            return perform_search("high-risk", "High-Risk AI Systems")
        
        def quick_access_transparency():
            return perform_search("transparency", "Limited Risk AI Systems")
        
        def assess_compliance(system_desc):
            """Simple compliance assessment based on system description"""
            if not system_desc.strip():
                return "Please describe your AI system for assessment."
            
            desc_lower = system_desc.lower()
            assessment = "<div style='background: #f0f9ff; padding: 1rem; border-radius: 8px;'>"
            assessment += f"<h4>🤖 System: {system_desc}</h4>"
            
            # Simple rule-based assessment
            risk_level = "Minimal Risk"
            requirements = []
            
            if any(term in desc_lower for term in ['biometric', 'facial recognition', 'emotion', 'scoring']):
                risk_level = "High Risk or Prohibited"
                requirements.extend([
                    "Conformity assessment required",
                    "Technical documentation (Annex IV)",
                    "Risk management system",
                    "Data governance measures",
                    "Human oversight requirements"
                ])
            elif any(term in desc_lower for term in ['chatbot', 'customer service', 'interaction']):
                risk_level = "Limited Risk"
                requirements.append("Transparency disclosure required (Article 52)")
            
            assessment += f"<p><strong>Preliminary Risk Assessment:</strong> {risk_level}</p>"
            
            if requirements:
                assessment += "<h5>📋 Key Requirements:</h5><ul>"
                for req in requirements:
                    assessment += f"<li>{req}</li>"
                assessment += "</ul>"
            
            assessment += "<p><em>⚠️ This is a preliminary assessment. Consult legal experts for definitive compliance guidance.</em></p>"
            assessment += "</div>"
            
            return assessment
        
        # Wire up event handlers
        search_btn.click(
            fn=perform_search,
            inputs=[search_query, category_filter],
            outputs=[search_results]
        )
        
        prohibited_btn.click(
            fn=quick_access_prohibited,
            outputs=[search_results]
        )
        
        high_risk_btn.click(
            fn=quick_access_high_risk,
            outputs=[search_results]
        )
        
        transparency_btn.click(
            fn=quick_access_transparency,
            outputs=[search_results]
        )
        
        check_compliance_btn.click(
            fn=assess_compliance,
            inputs=[system_description],
            outputs=[compliance_result]
        )
        
        # Initialize with overview
        search_results.value = perform_search("", "All")
        
        return search_query, search_results, article_detail 