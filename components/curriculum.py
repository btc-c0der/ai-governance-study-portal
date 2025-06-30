"""
📖 Curriculum Manager for AI Governance Study Portal
Handles 12-week program tracking, progress visualization, and content delivery.
"""

import gradio as gr
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

class CurriculumManager:
    def __init__(self):
        self.curriculum_data = self.load_curriculum()
        self.progress_data = self.load_progress()
    
    def load_curriculum(self):
        """Load the 12-week curriculum structure"""
        curriculum_path = Path("components/curriculum.json")
        
        # Create default curriculum if file doesn't exist
        if not curriculum_path.exists():
            return self.create_default_curriculum()
        
        try:
            with open(curriculum_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return self.create_default_curriculum()
    
    def create_default_curriculum(self):
        """Create the comprehensive 12-week AI Governance curriculum"""
        return {
            "program_title": "AI Governance Professional (AIGP) Certification Path",
            "total_weeks": 12,
            "modules": [
                {
                    "week": 1,
                    "title": "🎯 Foundations of AI Governance",
                    "objectives": [
                        "Understand AI governance frameworks",
                        "Learn key terminology and concepts",
                        "Explore regulatory landscape overview"
                    ],
                    "topics": [
                        "What is AI Governance?",
                        "Stakeholder ecosystem",
                        "Risk-based approaches",
                        "Global regulatory comparison"
                    ],
                    "deliverables": ["Concept map", "Stakeholder analysis"],
                    "estimated_hours": 8,
                    "difficulty": "Beginner",
                    "resources": [
                        "EU AI Act White Paper",
                        "NIST AI Risk Management Framework",
                        "ISO/IEC 23053 guidance"
                    ]
                },
                {
                    "week": 2,
                    "title": "⚖️ EU AI Act Deep Dive - Part 1",
                    "objectives": [
                        "Master EU AI Act structure and scope",
                        "Understand risk categorization",
                        "Learn prohibited AI practices"
                    ],
                    "topics": [
                        "EU AI Act overview and timeline",
                        "Risk pyramid (unacceptable, high, limited, minimal)",
                        "Prohibited AI systems (Article 5)",
                        "High-risk AI systems classification"
                    ],
                    "deliverables": ["Risk assessment template", "Compliance checklist"],
                    "estimated_hours": 10,
                    "difficulty": "Intermediate",
                    "resources": [
                        "EU AI Act full text",
                        "Risk management guidelines",
                        "Case studies"
                    ]
                },
                {
                    "week": 3,
                    "title": "🤖 Technical Standards & Implementation",
                    "objectives": [
                        "Learn technical requirements for AI systems",
                        "Understand conformity assessment",
                        "Explore quality management systems"
                    ],
                    "topics": [
                        "Annex IV requirements",
                        "Data governance and quality",
                        "Documentation and record-keeping",
                        "Human oversight requirements"
                    ],
                    "deliverables": ["Technical documentation template", "QMS framework"],
                    "estimated_hours": 12,
                    "difficulty": "Advanced",
                    "resources": [
                        "ISO 27001 standards",
                        "Technical specifications",
                        "Implementation guides"
                    ]
                },
                {
                    "week": 4,
                    "title": "📊 Risk Management & Assessment",
                    "objectives": [
                        "Master AI risk assessment methodologies",
                        "Learn mitigation strategies",
                        "Understand continuous monitoring"
                    ],
                    "topics": [
                        "Risk identification frameworks",
                        "Impact assessment methods",
                        "Mitigation and controls",
                        "Monitoring and review processes"
                    ],
                    "deliverables": ["Risk register", "Monitoring dashboard"],
                    "estimated_hours": 10,
                    "difficulty": "Intermediate",
                    "resources": [
                        "NIST RMF guidelines",
                        "Risk assessment tools",
                        "Industry benchmarks"
                    ]
                },
                {
                    "week": 5,
                    "title": "🏛️ Governance Structures & Oversight",
                    "objectives": [
                        "Design AI governance frameworks",
                        "Establish oversight mechanisms",
                        "Learn board-level reporting"
                    ],
                    "topics": [
                        "Governance committee structures",
                        "Roles and responsibilities",
                        "Escalation procedures",
                        "Board reporting and metrics"
                    ],
                    "deliverables": ["Governance charter", "Reporting template"],
                    "estimated_hours": 8,
                    "difficulty": "Intermediate",
                    "resources": [
                        "Corporate governance guides",
                        "Best practice frameworks",
                        "Case studies"
                    ]
                },
                {
                    "week": 6,
                    "title": "🔒 Data Privacy & AI Ethics",
                    "objectives": [
                        "Understand GDPR-AI intersections",
                        "Learn ethical AI principles",
                        "Explore bias detection and mitigation"
                    ],
                    "topics": [
                        "GDPR Article 22 and automated decision-making",
                        "Ethical AI frameworks",
                        "Bias and fairness in AI",
                        "Transparency and explainability"
                    ],
                    "deliverables": ["Ethics framework", "Bias testing protocol"],
                    "estimated_hours": 10,
                    "difficulty": "Advanced",
                    "resources": [
                        "GDPR compliance guides",
                        "IEEE ethical design standards",
                        "Algorithmic auditing tools"
                    ]
                },
                {
                    "week": 7,
                    "title": "🌍 Global AI Regulations Landscape",
                    "objectives": [
                        "Compare international AI regulations",
                        "Understand cross-border compliance",
                        "Learn harmonization challenges"
                    ],
                    "topics": [
                        "US AI Executive Order",
                        "China AI regulations",
                        "UK AI white paper approach",
                        "International coordination efforts"
                    ],
                    "deliverables": ["Regulatory comparison matrix", "Compliance roadmap"],
                    "estimated_hours": 9,
                    "difficulty": "Intermediate",
                    "resources": [
                        "International regulatory texts",
                        "Comparative analysis reports",
                        "Legal expert insights"
                    ]
                },
                {
                    "week": 8,
                    "title": "🏭 Sector-Specific Applications",
                    "objectives": [
                        "Understand industry-specific requirements",
                        "Learn sector compliance approaches",
                        "Explore use case implementations"
                    ],
                    "topics": [
                        "Healthcare AI regulations",
                        "Financial services compliance",
                        "Automotive and transport",
                        "Public sector AI use"
                    ],
                    "deliverables": ["Sector compliance guide", "Use case analysis"],
                    "estimated_hours": 11,
                    "difficulty": "Advanced",
                    "resources": [
                        "Sector-specific guidelines",
                        "Industry case studies",
                        "Regulatory sandbox examples"
                    ]
                },
                {
                    "week": 9,
                    "title": "📋 Compliance & Audit Processes",
                    "objectives": [
                        "Design compliance monitoring systems",
                        "Learn audit methodologies",
                        "Understand certification processes"
                    ],
                    "topics": [
                        "Compliance program design",
                        "Internal audit frameworks",
                        "External certification requirements",
                        "Continuous compliance monitoring"
                    ],
                    "deliverables": ["Audit program", "Compliance dashboard"],
                    "estimated_hours": 10,
                    "difficulty": "Advanced",
                    "resources": [
                        "Audit standards",
                        "Compliance frameworks",
                        "Certification body guidelines"
                    ]
                },
                {
                    "week": 10,
                    "title": "⚡ Incident Response & Crisis Management",
                    "objectives": [
                        "Develop incident response plans",
                        "Learn crisis communication",
                        "Understand regulatory reporting"
                    ],
                    "topics": [
                        "AI incident classification",
                        "Response team structures",
                        "Stakeholder communication",
                        "Regulatory breach reporting"
                    ],
                    "deliverables": ["Incident response plan", "Communication templates"],
                    "estimated_hours": 8,
                    "difficulty": "Intermediate",
                    "resources": [
                        "Incident response frameworks",
                        "Crisis management guides",
                        "Regulatory reporting requirements"
                    ]
                },
                {
                    "week": 11,
                    "title": "🚀 Emerging Technologies & Future Trends",
                    "objectives": [
                        "Explore cutting-edge AI developments",
                        "Understand regulatory evolution",
                        "Prepare for future challenges"
                    ],
                    "topics": [
                        "Generative AI governance",
                        "Quantum ML implications",
                        "Autonomous systems regulation",
                        "Future regulatory trends"
                    ],
                    "deliverables": ["Trend analysis report", "Future readiness plan"],
                    "estimated_hours": 9,
                    "difficulty": "Advanced",
                    "resources": [
                        "Emerging tech reports",
                        "Regulatory horizon scanning",
                        "Expert predictions"
                    ]
                },
                {
                    "week": 12,
                    "title": "🎓 AIGP Certification Preparation",
                    "objectives": [
                        "Consolidate learning outcomes",
                        "Practice exam questions",
                        "Prepare final project"
                    ],
                    "topics": [
                        "AIGP exam structure and format",
                        "Key concept review",
                        "Practice questions and scenarios",
                        "Final project presentation"
                    ],
                    "deliverables": ["Final project", "Certification application"],
                    "estimated_hours": 15,
                    "difficulty": "Expert",
                    "resources": [
                        "AIGP study guides",
                        "Practice exams",
                        "Certification requirements"
                    ]
                }
            ]
        }
    
    def load_progress(self):
        """Load student progress data"""
        # In a real implementation, this would load from a database
        return {
            "completed_weeks": [],
            "current_week": 1,
            "total_hours_studied": 0,
            "quiz_scores": {},
            "project_submissions": {}
        }
    
    def create_interface(self):
        """Create the Gradio interface for curriculum management"""
        
        gr.Markdown("## 📖 12-Week AI Governance Curriculum")
        
        with gr.Row():
            with gr.Column(scale=2):
                # Progress Overview
                progress_chart = gr.Plot(label="📊 Learning Progress")
                
                # Week selector
                available_weeks = len(self.curriculum_data['modules'])
                week_selector = gr.Dropdown(
                    choices=[(f"Week {i}: {self.curriculum_data['modules'][i-1]['title']}", i) 
                            for i in range(1, min(available_weeks + 1, 13))],
                    label="Select Week",
                    value=1
                )
                
            with gr.Column(scale=3):
                # Week content display
                week_content = gr.HTML(label="Week Content")
                
                # Action buttons
                with gr.Row():
                    mark_complete_btn = gr.Button("✅ Mark Complete", variant="primary")
                    add_notes_btn = gr.Button("📝 Add Notes", variant="secondary")
                    view_resources_btn = gr.Button("📚 Resources", variant="secondary")
        
        # Study notes section
        with gr.Row():
            study_notes = gr.Textbox(
                label="📝 Study Notes",
                lines=5,
                placeholder="Add your study notes here..."
            )
        
        # Interactive functions
        def update_week_content(week_num):
            if week_num and 1 <= week_num <= 12:
                module = self.curriculum_data['modules'][week_num - 1]
                
                html_content = f"""
                <div style="padding: 1rem; background: #f8fafc; border-radius: 10px;">
                    <h3>{module['title']}</h3>
                    <p><strong>Difficulty:</strong> {module['difficulty']} | 
                       <strong>Est. Hours:</strong> {module['estimated_hours']}</p>
                    
                    <h4>🎯 Learning Objectives:</h4>
                    <ul>
                        {''.join([f'<li>{obj}</li>' for obj in module['objectives']])}
                    </ul>
                    
                    <h4>📋 Topics Covered:</h4>
                    <ul>
                        {''.join([f'<li>{topic}</li>' for topic in module['topics']])}
                    </ul>
                    
                    <h4>📄 Deliverables:</h4>
                    <ul>
                        {''.join([f'<li>{deliv}</li>' for deliv in module['deliverables']])}
                    </ul>
                </div>
                """
                return html_content
            return "Select a week to view content"
        
        def create_progress_chart():
            """Create interactive progress visualization"""
            weeks = list(range(1, 13))
            completion_status = [1 if w in self.progress_data['completed_weeks'] else 0 for w in weeks]
            
            fig = go.Figure()
            
            # Add completion bars
            fig.add_trace(go.Bar(
                x=weeks,
                y=completion_status,
                name="Completed",
                marker_color='#10b981'
            ))
            
            fig.update_layout(
                title="📈 Weekly Completion Progress",
                xaxis_title="Week",
                yaxis_title="Completion Status",
                showlegend=False,
                height=300
            )
            
            return fig
        
        # Event handlers
        week_selector.change(
            fn=update_week_content,
            inputs=[week_selector],
            outputs=[week_content]
        )
        
        # Initialize with first week
        week_content.value = update_week_content(1)
        progress_chart.value = create_progress_chart()
        
        return week_selector, week_content, progress_chart 