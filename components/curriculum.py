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
import sqlite3
from components.auth_manager import AuthManager
from typing import Optional

class CurriculumManager:
    def __init__(self, auth_manager: Optional[AuthManager] = None):
        self.curriculum_data = self.load_curriculum()
        self.progress_data = self.load_progress()
        self.aigp_resources = self.load_aigp_resources()
        self.auth_manager = auth_manager or AuthManager()
        self.notes_db_path = "data/curriculum_notes.db"
        self.init_notes_database()
    
    def init_notes_database(self):
        """Initialize the notes database (authentication handled by AuthManager)"""
        # Ensure data directory exists
        Path(self.notes_db_path).parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.notes_db_path)
        cursor = conn.cursor()
        
        # Notes table only - authentication handled by AuthManager
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS curriculum_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                week_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_user_notes(self, week_number=None):
        """Get notes for current user"""
        if not self.auth_manager.is_logged_in():
            return []
        
        user_id = self.auth_manager.current_user['user_id']
        conn = sqlite3.connect(self.notes_db_path)
        cursor = conn.cursor()
        
        if week_number is not None:
            cursor.execute("""
                SELECT id, title, content, week_number, created_at, updated_at
                FROM curriculum_notes 
                WHERE user_id = ? AND week_number = ?
                ORDER BY updated_at DESC
            """, (user_id, week_number))
        else:
            cursor.execute("""
                SELECT id, title, content, week_number, created_at, updated_at
                FROM curriculum_notes 
                WHERE user_id = ?
                ORDER BY week_number, updated_at DESC
            """, (user_id,))
        
        notes = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": note[0],
                "title": note[1],
                "content": note[2],
                "week_number": note[3],
                "created_at": note[4],
                "updated_at": note[5]
            }
            for note in notes
        ]
    
    def create_note(self, week_number, title, content):
        """Create a new note"""
        if not self.auth_manager.is_logged_in():
            return False, "User not authenticated"
        
        user_id = self.auth_manager.current_user['user_id']
        conn = sqlite3.connect(self.notes_db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO curriculum_notes (user_id, week_number, title, content)
                VALUES (?, ?, ?, ?)
            """, (user_id, week_number, title, content))
            
            conn.commit()
            note_id = cursor.lastrowid
            conn.close()
            
            return True, f"Note created successfully"
        
        except Exception as e:
            conn.close()
            return False, f"Error creating note: {str(e)}"
    
    def update_note(self, note_id, title, content):
        """Update an existing note"""
        if not self.auth_manager.is_logged_in():
            return False, "User not authenticated"
        
        user_id = self.auth_manager.current_user['user_id']
        conn = sqlite3.connect(self.notes_db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE curriculum_notes 
                SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            """, (title, content, note_id, user_id))
            
            conn.commit()
            
            if cursor.rowcount > 0:
                conn.close()
                return True, "Note updated successfully"
            else:
                conn.close()
                return False, "Note not found or access denied"
        
        except Exception as e:
            conn.close()
            return False, f"Error updating note: {str(e)}"
    
    def delete_note(self, note_id):
        """Delete a note"""
        if not self.auth_manager.is_logged_in():
            return False, "User not authenticated"
        
        user_id = self.auth_manager.current_user['user_id']
        conn = sqlite3.connect(self.notes_db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM curriculum_notes 
                WHERE id = ? AND user_id = ?
            """, (note_id, user_id))
            
            conn.commit()
            
            if cursor.rowcount > 0:
                conn.close()
                return True, "Note deleted successfully"
            else:
                conn.close()
                return False, "Note not found or access denied"
        
        except Exception as e:
            conn.close()
            return False, f"Error deleting note: {str(e)}"
    
    def get_notes_html(self, week_number):
        """Generate HTML display for user notes"""
        notes = self.get_user_notes(week_number)
        
        if not notes:
            return f"""
            <div style="background: #1a1a1a; border-radius: 12px; padding: 2rem; color: #ffffff; text-align: center;">
                <h3 style="color: #60a5fa; margin: 0 0 1rem 0;">📝 No Notes Yet for Week {week_number}</h3>
                <p style="color: #d1d5db; margin: 0;">Create your first note using the form above!</p>
            </div>
            """
        
        notes_html = f"""
        <div style="background: #1a1a1a; border-radius: 12px; padding: 2rem; color: #ffffff;">
            <h3 style="color: #60a5fa; margin: 0 0 1.5rem 0;">📝 Your Notes for Week {week_number}</h3>
        """
        
        for note in notes:
            created_date = note['created_at'].split(' ')[0] if note['created_at'] else 'Unknown'
            updated_date = note['updated_at'].split(' ')[0] if note['updated_at'] else 'Unknown'
            
            # Truncate content for preview
            content_preview = note['content'][:200] + "..." if len(note['content']) > 200 else note['content']
            
            # Escape strings for JavaScript (cannot use backslashes in f-strings)
            escaped_title = note['title'].replace("'", "\\'")
            escaped_content = note['content'].replace("'", "\\'").replace(chr(10), "\\n")
            
            notes_html += f"""
            <div style="border: 2px solid #3b82f6; border-radius: 8px; padding: 1.5rem; margin: 1rem 0; background: #2a2a2a;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h4 style="color: #fbbf24; margin: 0; font-size: 1.2rem;">{note['title']}</h4>
                    <div style="display: flex; gap: 0.5rem;">
                        <button onclick="editNote({note['id']}, '{escaped_title}', '{escaped_content}')" 
                                style="background: #3b82f6; color: white; border: none; padding: 0.3rem 0.6rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem;">
                            ✏️ Edit
                        </button>
                        <button onclick="deleteNote({note['id']}, {week_number})" 
                                style="background: #dc2626; color: white; border: none; padding: 0.3rem 0.6rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem;">
                            🗑️ Delete
                        </button>
                    </div>
                </div>
                
                <p style="color: #e5e7eb; margin: 0 0 1rem 0; line-height: 1.5; white-space: pre-wrap;">{content_preview}</p>
                
                <div style="color: #94a3b8; font-size: 0.85rem; border-top: 1px solid #475569; padding-top: 0.5rem;">
                    <span style="margin-right: 1rem;">📅 Created: {created_date}</span>
                    {f'<span>🔄 Updated: {updated_date}</span>' if updated_date != created_date else ''}
                </div>
            </div>
            """
        
        notes_html += """
        </div>
        
        <script>
        function editNote(noteId, title, content) {
            // This would trigger the edit functionality
            // In a real implementation, you'd use Gradio's JavaScript API
            console.log('Edit note:', noteId, title, content);
        }
        
        function deleteNote(noteId, weekNum) {
            if (confirm('Are you sure you want to delete this note?')) {
                // This would trigger the delete functionality
                console.log('Delete note:', noteId, 'for week:', weekNum);
            }
        }
        </script>
        """
        
        return notes_html
    
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
    
    def load_aigp_resources(self):
        """Load comprehensive IAPP AIGP certification resources from JSON file"""
        try:
            with open("data/aigp_resources.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: AIGP resources JSON file not found. Using empty resources.")
            return {}
        except json.JSONDecodeError:
            print("Warning: Invalid JSON in AIGP resources file. Using empty resources.")
            return {}
        except Exception as e:
            print(f"Warning: Error loading AIGP resources: {e}. Using empty resources.")
            return {}
    
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
                        "Compare international AI regulations - Develop a comprehensive understanding of how different jurisdictions approach AI regulation, including detailed analysis of regulatory frameworks in major economies and their implications for global AI deployment.",
                        "Understand cross-border compliance - Master the complexities of operating AI systems across multiple jurisdictions, including data transfer requirements, local certification needs, and harmonization strategies.",
                        "Learn harmonization challenges - Explore the practical challenges of reconciling different regulatory requirements, including conflicts between jurisdictions and strategies for building globally compliant AI systems."
                    ],
                    "topics": [
                        "US AI Executive Order - Deep dive into the Biden Administration's Executive Order on AI, including key requirements, affected sectors, and implementation timelines.",
                        "China AI regulations - Comprehensive analysis of China's AI governance framework, including the AI governance measures, ethical principles, and sector-specific requirements.",
                        "UK AI white paper approach - Detailed examination of the UK's pro-innovation regulatory framework, including the five principles for AI regulation and sector-specific guidance.",
                        "International coordination efforts - Study of international initiatives for AI governance coordination, including OECD principles, UNESCO recommendations, and G7 AI guidelines."
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
                        "Understand industry-specific requirements - Master the unique AI governance requirements across different sectors, including regulatory obligations, industry standards, and sector-specific risk considerations.",
                        "Learn sector compliance approaches - Develop expertise in implementing AI governance frameworks tailored to different industries, including compliance strategies, documentation requirements, and stakeholder management.",
                        "Explore use case implementations - Analyze real-world examples of AI governance implementation across various sectors, including success stories, challenges faced, and lessons learned."
                    ],
                    "topics": [
                        "Healthcare AI regulations - Comprehensive coverage of AI governance in healthcare, including patient data protection, medical device regulations, and clinical validation requirements.",
                        "Financial services compliance - Detailed examination of AI governance in finance, including model risk management, algorithmic trading regulations, and customer protection requirements.",
                        "Automotive and transport - Analysis of AI governance in autonomous vehicles and intelligent transport systems, including safety standards, liability frameworks, and testing requirements.",
                        "Public sector AI use - Study of AI governance in government applications, including procurement guidelines, transparency requirements, and public accountability measures."
                    ],
                    "deliverables": ["Sector compliance guide", "Use case analysis"],
                    "estimated_hours": 11,
                    "difficulty": "Advanced"
                },
                {
                    "week": 9,
                    "title": "📋 Compliance & Audit Processes",
                    "objectives": [
                        "Design compliance monitoring systems - Learn to create comprehensive monitoring frameworks that track AI system compliance across multiple dimensions, including technical, ethical, and regulatory requirements.",
                        "Learn audit methodologies - Master various approaches to auditing AI systems, including technical audits, ethical assessments, and regulatory compliance reviews.",
                        "Understand certification processes - Develop expertise in AI system certification requirements, including documentation preparation, testing procedures, and ongoing compliance maintenance."
                    ],
                    "topics": [
                        "Compliance program design - Detailed guidance on creating effective AI compliance programs, including policy development, control frameworks, and monitoring mechanisms.",
                        "Internal audit frameworks - Comprehensive coverage of internal audit methodologies for AI systems, including risk-based approaches, testing procedures, and reporting templates.",
                        "External certification requirements - Analysis of various certification schemes for AI systems, including conformity assessment procedures, testing requirements, and documentation needs.",
                        "Continuous compliance monitoring - Study of tools and techniques for ongoing compliance monitoring, including automated checks, periodic reviews, and reporting systems."
                    ],
                    "deliverables": ["Audit program", "Compliance dashboard"],
                    "estimated_hours": 10,
                    "difficulty": "Advanced"
                },
                {
                    "week": 10,
                    "title": "⚡ Incident Response & Crisis Management",
                    "objectives": [
                        "Develop incident response plans - Master the creation of comprehensive incident response plans specifically tailored for AI systems, including detection mechanisms, escalation procedures, and recovery processes.",
                        "Learn crisis communication - Develop expertise in communicating AI-related incidents to various stakeholders, including regulatory bodies, affected users, and the general public.",
                        "Understand regulatory reporting - Learn the requirements and procedures for reporting AI incidents to regulatory authorities, including timing requirements, documentation needs, and follow-up procedures."
                    ],
                    "topics": [
                        "AI incident classification - Detailed framework for categorizing AI incidents based on severity, impact, and regulatory implications, including response prioritization criteria.",
                        "Response team structures - Comprehensive guidance on building and organizing AI incident response teams, including roles, responsibilities, and required expertise.",
                        "Stakeholder communication - Detailed strategies for managing communications during AI incidents, including templates, channels, and timing considerations.",
                        "Regulatory breach reporting - Analysis of reporting requirements across different jurisdictions, including mandatory notifications, documentation requirements, and timeline obligations."
                    ],
                    "deliverables": ["Incident response plan", "Communication templates"],
                    "estimated_hours": 8,
                    "difficulty": "Intermediate"
                },
                {
                    "week": 11,
                    "title": "🚀 Emerging Technologies & Future Trends",
                    "objectives": [
                        "Explore cutting-edge AI developments - Deep dive into emerging AI technologies and their governance implications, including large language models, autonomous systems, and edge AI applications.",
                        "Understand regulatory evolution - Analysis of how AI regulations are evolving to address new technological capabilities, including proposed frameworks and industry standards.",
                        "Prepare for future challenges - Develop strategies for anticipating and addressing future AI governance challenges, including ethical considerations and societal impacts."
                    ],
                    "topics": [
                        "Generative AI governance - Comprehensive examination of governance frameworks for generative AI systems, including content moderation, copyright implications, and safety measures.",
                        "Quantum ML implications - Analysis of how quantum computing will impact AI governance, including security considerations, algorithmic accountability, and regulatory preparedness.",
                        "Autonomous systems regulation - Study of regulatory approaches to autonomous systems, including safety standards, liability frameworks, and ethical guidelines.",
                        "Future regulatory trends - Exploration of emerging regulatory trends and their implications for AI governance, including international coordination efforts and industry standards."
                    ],
                    "deliverables": ["Trend analysis report", "Future readiness plan"],
                    "estimated_hours": 9,
                    "difficulty": "Advanced"
                },
                {
                    "week": 12,
                    "title": "🎓 AIGP Certification Preparation",
                    "objectives": [
                        "Consolidate learning outcomes - Comprehensive review of key concepts and frameworks covered throughout the course, with emphasis on practical application and integration.",
                        "Practice exam questions - Extensive practice with certification exam-style questions, including scenario-based problems and technical assessments.",
                        "Prepare final project - Development of a comprehensive AI governance implementation project that demonstrates mastery of course concepts and practical application skills."
                    ],
                    "topics": [
                        "AIGP exam structure and format - Detailed breakdown of the certification exam format, including question types, scoring criteria, and time management strategies.",
                        "Key concept review - Systematic review of critical concepts from all previous modules, with emphasis on their practical application in AI governance.",
                        "Practice questions and scenarios - Extensive practice with real-world scenarios and example questions that mirror the certification exam format.",
                        "Final project presentation - Guidance on preparing and presenting the final certification project, including documentation requirements and evaluation criteria."
                    ],
                    "deliverables": ["Final project", "Certification application"],
                    "estimated_hours": 15,
                    "difficulty": "Expert"
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
        
        # Resources display area (initially hidden)
        with gr.Row():
            resources_display = gr.HTML(visible=False, label="AIGP Resources")
        
        # Authentication and Notes Management Area (initially hidden)
        with gr.Row():
            auth_notes_area = gr.Column(visible=False)
            with auth_notes_area:
                # Authentication form
                auth_section = gr.Column(visible=True)
                with auth_section:
                    gr.Markdown("## 🔐 Authentication Required")
                    gr.Markdown("Please login or register to access the notes feature")
                    
                    with gr.Tabs():
                        with gr.Tab("Login"):
                            with gr.Column():
                                login_email = gr.Textbox(
                                    label="📧 Email",
                                    placeholder="Enter your email address..."
                                )
                                login_password = gr.Textbox(
                                    label="🔑 Password",
                                    type="password",
                                    placeholder="Enter your password..."
                                )
                                login_btn = gr.Button("🔐 Login", variant="primary")
                                login_message = gr.Markdown(visible=False)
                        
                        with gr.Tab("Register"):
                            with gr.Column():
                                reg_email = gr.Textbox(
                                    label="📧 Email",
                                    placeholder="Enter your email address..."
                                )
                                reg_password = gr.Textbox(
                                    label="🔑 Password",
                                    type="password",
                                    placeholder="Create a secure password..."
                                )
                                reg_confirm = gr.Textbox(
                                    label="🔑 Confirm Password",
                                    type="password",
                                    placeholder="Confirm your password..."
                                )
                                register_btn = gr.Button("📝 Register", variant="secondary")
                                register_message = gr.Markdown(visible=False)
                
                # Notes management interface (initially hidden)
                notes_section = gr.Column(visible=False)
                with notes_section:
                    gr.Markdown("## 📝 Study Notes Manager")
                    
                    with gr.Row():
                        with gr.Column(scale=2):
                            # Current user info
                            user_info = gr.HTML()
                            logout_btn = gr.Button("🚪 Logout", variant="secondary")
                        
                        with gr.Column(scale=3):
                            # Week selector for notes
                            notes_week_selector = gr.Dropdown(
                                choices=[(f"Week {i}", i) for i in range(1, 13)],
                                label="Select Week for Notes",
                                value=1
                            )
                    
                    # Create new note section
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### ➕ Create New Note")
                            note_title = gr.Textbox(
                                label="📑 Note Title",
                                placeholder="Enter a descriptive title for your note..."
                            )
                            note_content = gr.Textbox(
                                label="📝 Note Content",
                                lines=8,
                                placeholder="Write your detailed study notes here..."
                            )
                            
                            with gr.Row():
                                save_note_btn = gr.Button("💾 Save Note", variant="primary")
                                clear_note_btn = gr.Button("🗑️ Clear", variant="secondary")
                    
                    # Existing notes display
                    with gr.Row():
                        existing_notes = gr.HTML(label="Your Notes")
                    
                    # Hidden components for note editing
                    edit_note_id = gr.State(value=None)
                    edit_mode = gr.State(value=False)
        
        # Interactive functions
        def update_week_content(week_num):
            if week_num and 1 <= week_num <= 12:
                module = self.curriculum_data['modules'][week_num - 1]
                
                # Special expanded content for Weeks 1-6
                expanded_content = ""
                if week_num == 1:
                    expanded_content = """
                    <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(30, 64, 175, 0.1); border-radius: 10px;">
                        <h4 style="color: #fbbf24; margin: 0 0 1rem 0; font-size: 1.2rem;">
                            📚 Expanded Topic Content:
                        </h4>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">1. What is AI Governance?</h5>
                            <ul style="margin: 0; padding-left: 1.5rem;">
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Definition and scope of AI governance</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Key principles and objectives</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Relationship to corporate governance</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Importance in modern organizations</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Governance vs. compliance distinction</li>
                            </ul>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">2. Stakeholder Ecosystem</h5>
                            <div style="display: flex; gap: 2rem;">
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0 0 0.3rem 0;">Internal Stakeholders:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Board of Directors</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Executive leadership</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">AI development teams</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Risk and compliance teams</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">End users</li>
                                    </ul>
                                </div>
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0 0 0.3rem 0;">External Stakeholders:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Regulators</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Customers</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Business partners</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Industry groups</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Public interest groups</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">3. Risk-based Approaches</h5>
                            <ul style="margin: 0; padding-left: 1.5rem;">
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk assessment methodologies</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk categorization frameworks:
                                    <ul style="margin: 0.2rem 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6;">EU AI Act risk pyramid</li>
                                        <li style="color: #f3f4f6;">NIST AI RMF approach</li>
                                        <li style="color: #f3f4f6;">ISO/IEC 23053 guidelines</li>
                                    </ul>
                                </li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk mitigation strategies</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Continuous monitoring requirements</li>
                            </ul>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">4. Global Regulatory Comparison</h5>
                            <ul style="margin: 0; padding-left: 1.5rem;">
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Major regulatory frameworks:
                                    <ul style="margin: 0.2rem 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6;">EU AI Act (Regulation 2024/1689)</li>
                                        <li style="color: #f3f4f6;">US AI Executive Order 14110</li>
                                        <li style="color: #f3f4f6;">China's AI regulations</li>
                                        <li style="color: #f3f4f6;">UK's pro-innovation approach</li>
                                    </ul>
                                </li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Regional variations:
                                    <ul style="margin: 0.2rem 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6;">Singapore Model AI Governance</li>
                                        <li style="color: #f3f4f6;">Canada's AIDA</li>
                                        <li style="color: #f3f4f6;">Japan's Guidelines</li>
                                        <li style="color: #f3f4f6;">Australia's Ethics Framework</li>
                                    </ul>
                                </li>
                            </ul>
                        </div>
                        
                        <div style="margin-bottom: 1rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">📚 Key Resources</h5>
                            <div style="display: flex; gap: 2rem;">
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0 0 0.3rem 0;">Official Standards:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">ISO/IEC 23053:2022 (AI Risk Management)</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">ISO/IEC 23894:2023 (Risk Management Processes)</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">IEEE 2858 (AI System Transparency)</li>
                                    </ul>
                                </div>
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0 0 0.3rem 0;">Government Documents:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">EU AI Act Official Text</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">US NIST AI Risk Management Framework</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">UK AI White Paper</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                    """
                elif week_num == 2:
                    expanded_content = """
                    <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(30, 64, 175, 0.1); border-radius: 10px;">
                        <h4 style="color: #fbbf24; margin: 0 0 1rem 0; font-size: 1.2rem;">
                            📚 Expanded Topic Content:
                        </h4>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">1. EU AI Act Overview and Timeline</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                The EU AI Act represents the world's first comprehensive legal framework for artificial intelligence. Adopted in 2024, it establishes a unified regulatory approach across all EU member states. The Act follows a risk-based approach, categorizing AI systems based on their potential impact on fundamental rights and safety. Implementation will occur in phases over 24 months, giving organizations time to adapt their AI systems and processes to the new requirements.
                            </p>
                            <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Key milestones and deadlines</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Scope of application (territorial and material)</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Core definitions and concepts</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Implementation phases</li>
                            </ul>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">2. Risk Pyramid Structure</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                The Act introduces a four-tier risk classification system that determines the obligations and requirements for AI systems. This pyramid approach ensures proportionate regulation, with stricter requirements for higher-risk applications. Understanding this classification is crucial for organizations to determine their compliance obligations and necessary controls.
                            </p>
                            <div style="display: flex; gap: 2rem;">
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0.5rem 0;">Unacceptable Risk:</h6>
                                    <p style="color: #f3f4f6; margin: 0.3rem 0; font-size: 0.9rem;">
                                        AI systems that pose unacceptable risks to fundamental rights are completely prohibited. These include social scoring systems, manipulative AI, and most real-time biometric identification systems in public spaces.
                                    </p>
                                </div>
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0.5rem 0;">High Risk:</h6>
                                    <p style="color: #f3f4f6; margin: 0.3rem 0; font-size: 0.9rem;">
                                        Systems used in critical infrastructure, education, employment, essential services, and law enforcement require strict oversight, documentation, and human supervision.
                                    </p>
                                </div>
                            </div>
                            <div style="display: flex; gap: 2rem; margin-top: 1rem;">
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0.5rem 0;">Limited Risk:</h6>
                                    <p style="color: #f3f4f6; margin: 0.3rem 0; font-size: 0.9rem;">
                                        Systems like chatbots and emotion recognition require transparency measures, ensuring users know they're interacting with AI and can make informed decisions.
                                    </p>
                                </div>
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0.5rem 0;">Minimal Risk:</h6>
                                    <p style="color: #f3f4f6; margin: 0.3rem 0; font-size: 0.9rem;">
                                        Basic AI applications like spam filters and AI-enabled video games have minimal requirements, though voluntary codes of conduct are encouraged.
                                    </p>
                                </div>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">3. Prohibited AI Systems (Article 5)</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Article 5 of the EU AI Act explicitly prohibits AI systems that pose unacceptable risks to society and fundamental rights. These prohibitions reflect the EU's commitment to ethical AI development and human-centric artificial intelligence.
                            </p>
                            <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                    <strong>Subliminal Manipulation:</strong> Systems designed to manipulate human behavior in ways that cause physical or psychological harm
                                </li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                    <strong>Vulnerability Exploitation:</strong> AI that exploits age, disability, or social/economic situations to materially distort behavior
                                </li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                    <strong>Social Scoring:</strong> Government social scoring systems that lead to detrimental treatment of individuals
                                </li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                    <strong>Real-time Biometric ID:</strong> Limited exceptions for law enforcement in specific circumstances
                                </li>
                            </ul>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">4. High-risk AI Systems Classification</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                High-risk AI systems are subject to extensive requirements due to their significant impact on safety and fundamental rights. The classification process involves both standalone high-risk AI systems and those integrated into products covered by existing EU safety legislation.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Classification Criteria:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Intended purpose of the AI system</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Sector of deployment</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Potential impact on fundamental rights</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Level of autonomy in decision-making</li>
                                </ul>
                            </div>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Requirements:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk assessment and management system</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Data governance and quality measures</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Technical documentation and record-keeping</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Human oversight mechanisms</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Accuracy, robustness, and cybersecurity</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">📚 Essential Resources</h5>
                            <div style="display: flex; gap: 2rem;">
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0 0 0.3rem 0;">Primary Sources:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">EU AI Act Full Text (2024/1689)</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">European Commission Guidelines</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">ENISA Technical Guidance</li>
                                    </ul>
                                </div>
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0 0 0.3rem 0;">Implementation Tools:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Risk Assessment Templates</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Compliance Checklists</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Documentation Guidelines</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                    """
                elif week_num == 3:
                    expanded_content = """
                    <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(30, 64, 175, 0.1); border-radius: 10px;">
                        <h4 style="color: #fbbf24; margin: 0 0 1rem 0; font-size: 1.2rem;">
                            📚 Expanded Topic Content:
                        </h4>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">1. High-Risk AI Requirements Deep Dive</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                The EU AI Act establishes comprehensive requirements for high-risk AI systems to ensure their safety, transparency, and accountability. These requirements form the backbone of the regulatory framework and demand careful attention from organizations developing or deploying high-risk AI systems.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Requirements Breakdown:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                        <strong>Risk Management System:</strong> A systematic approach to identifying, assessing, and mitigating risks throughout the AI system's lifecycle
                                    </li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                        <strong>Data Quality:</strong> Rigorous standards for training, validation, and testing datasets to ensure representativeness and minimize biases
                                    </li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                        <strong>Technical Documentation:</strong> Comprehensive documentation covering system architecture, development processes, and validation methods
                                    </li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                        <strong>Record Keeping:</strong> Automated logging of system operations to ensure traceability and accountability
                                    </li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">2. Transparency and Information Requirements</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Transparency is a cornerstone of the EU AI Act, requiring clear communication about AI systems' capabilities, limitations, and intended use. This ensures users can make informed decisions and understand when they are interacting with AI systems.
                            </p>
                            <div style="display: flex; gap: 2rem;">
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0.5rem 0;">User Information:</h6>
                                    <p style="color: #f3f4f6; margin: 0.3rem 0; font-size: 0.9rem;">
                                        Organizations must provide clear information about AI system capabilities, limitations, and intended purpose. This includes performance characteristics, expected outputs, and potential risks.
                                    </p>
                                </div>
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0.5rem 0;">Documentation Requirements:</h6>
                                    <p style="color: #f3f4f6; margin: 0.3rem 0; font-size: 0.9rem;">
                                        Detailed technical documentation must be maintained, including system architecture, development methodologies, and validation procedures. This ensures accountability and facilitates compliance assessments.
                                    </p>
                                </div>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">3. Human Oversight Measures</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Human oversight is mandatory for high-risk AI systems to ensure meaningful human control and intervention capability. This requirement balances automation benefits with human judgment and accountability.
                            </p>
                            <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                    <strong>Oversight Mechanisms:</strong> Implementation of technical tools and procedures that enable human monitoring and intervention in AI system operations
                                </li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                    <strong>Training Requirements:</strong> Comprehensive training programs for human overseers to understand system capabilities and limitations
                                </li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                    <strong>Intervention Protocols:</strong> Clear procedures for when and how human operators should intervene in AI system decisions
                                </li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                    <strong>Documentation of Oversight:</strong> Detailed records of human oversight activities and interventions for accountability
                                </li>
                            </ul>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">4. Accuracy and Cybersecurity Requirements</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                High-risk AI systems must maintain appropriate levels of accuracy and cybersecurity throughout their lifecycle. This ensures reliable performance and protection against unauthorized manipulation.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Accuracy Measures:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Performance metrics and thresholds</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Regular accuracy assessments</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Error handling procedures</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Continuous monitoring systems</li>
                                </ul>
                            </div>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Cybersecurity Requirements:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Resilience against attacks</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Data protection measures</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Access control systems</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Incident response plans</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">📚 Implementation Resources</h5>
                            <div style="display: flex; gap: 2rem;">
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0 0 0.3rem 0;">Technical Guidelines:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Risk Assessment Frameworks</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Documentation Templates</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Oversight Protocols</li>
                                    </ul>
                                </div>
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0 0 0.3rem 0;">Best Practices:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Industry Standards</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Case Studies</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Implementation Examples</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                    """
                elif week_num == 4:
                    expanded_content = """
                    <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(30, 64, 175, 0.1); border-radius: 10px;">
                        <h4 style="color: #fbbf24; margin: 0 0 1rem 0; font-size: 1.2rem;">
                            📚 Expanded Topic Content:
                        </h4>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">1. Risk Identification Frameworks</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Understanding risk identification frameworks is crucial for effective risk management. Organizations must identify potential risks associated with their AI systems and develop strategies to mitigate them.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Frameworks:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">ISO 27001:2013</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">NIST SP 800-30:2016</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">ISO/IEC 27005:2018</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">2. Impact Assessment Methods</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Impact assessment methods help organizations understand the potential consequences of AI system failures and develop strategies to mitigate them.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Methods:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Scenario Analysis</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Failure Mode and Effects Analysis (FMEA)</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Hazard and Operability Studies (HAZOP)</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk-Based Inspection (RBI)</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">3. Mitigation and Controls</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Developing and implementing effective mitigation strategies is essential for maintaining compliant AI systems. These strategies should address both technical and operational risks.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Strategies:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                        <strong>Technical Controls:</strong> Implementation of security measures, monitoring systems, and fail-safes
                                    </li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                        <strong>Operational Controls:</strong> Procedures, policies, and guidelines for system operation
                                    </li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                        <strong>Management Controls:</strong> Oversight mechanisms and decision-making frameworks
                                    </li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                        <strong>Documentation Controls:</strong> Record-keeping and evidence maintenance procedures
                                    </li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">4. Continuous Monitoring</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Ongoing monitoring ensures that AI systems maintain compliance and safety throughout their operational lifecycle. This includes regular assessments and updates to risk management strategies.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Monitoring Activities:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Performance tracking</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk indicator monitoring</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Incident detection</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Trend analysis</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    """
                elif week_num == 5:
                    expanded_content = """
                    <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(30, 64, 175, 0.1); border-radius: 10px;">
                        <h4 style="color: #fbbf24; margin: 0 0 1rem 0; font-size: 1.2rem;">
                            📚 Expanded Topic Content:
                        </h4>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">1. Documentation Best Practices</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Effective documentation is crucial for demonstrating compliance with the EU AI Act. Organizations must maintain comprehensive, clear, and accessible documentation that covers all aspects of their AI systems' development, deployment, and operation.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Documentation Areas:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">System architecture and design decisions</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Data governance and quality measures</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk assessment and mitigation strategies</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Testing and validation procedures</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">2. Compliance Record-Keeping</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Organizations must maintain detailed records of their compliance efforts, including all assessments, tests, and modifications made to ensure conformity with the EU AI Act requirements.
                            </p>
                            <div style="display: flex; gap: 2rem;">
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0.5rem 0;">Required Records:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Conformity assessments</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk management measures</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Post-market monitoring data</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Incident reports and resolutions</li>
                                    </ul>
                                </div>
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0.5rem 0;">Storage Requirements:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Secure and accessible storage</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Version control systems</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Retention period compliance</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Access control measures</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">3. Compliance Monitoring Tools</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Implementing effective compliance monitoring tools helps organizations track, measure, and maintain their adherence to EU AI Act requirements throughout their AI systems' lifecycle.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Essential Tools:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Automated compliance checkers</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk assessment platforms</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Documentation management systems</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Audit trail generators</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">4. Audit Preparation</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Organizations must be prepared for potential audits by maintaining organized, comprehensive documentation and establishing clear procedures for demonstrating compliance.
                            </p>
                            <div style="display: flex; gap: 2rem;">
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0.5rem 0;">Audit Readiness:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Documentation organization</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Staff training and preparation</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Process documentation</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Evidence collection procedures</li>
                                    </ul>
                                </div>
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0.5rem 0;">Common Audit Areas:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk management systems</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Data governance practices</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Human oversight measures</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Technical documentation</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                    """
                elif week_num == 6:
                    expanded_content = """
                    <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(30, 64, 175, 0.1); border-radius: 10px;">
                        <h4 style="color: #fbbf24; margin: 0 0 1rem 0; font-size: 1.2rem;">
                            📚 Expanded Topic Content:
                        </h4>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">1. Risk Assessment Methodologies</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Effective risk assessment is fundamental to AI governance under the EU AI Act. Organizations must implement systematic approaches to identify, evaluate, and mitigate risks associated with their AI systems.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Components:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk identification techniques</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Impact assessment methods</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Probability evaluation tools</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk prioritization frameworks</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">2. Risk Management Frameworks</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Organizations need robust frameworks to manage identified risks throughout the AI system lifecycle. These frameworks should align with EU AI Act requirements and industry best practices.
                            </p>
                            <div style="display: flex; gap: 2rem;">
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0.5rem 0;">Framework Elements:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk governance structure</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Control implementation</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Monitoring mechanisms</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Review procedures</li>
                                    </ul>
                                </div>
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0.5rem 0;">Implementation Steps:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Framework selection</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Customization process</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Staff training</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Effectiveness evaluation</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">3. Risk Mitigation Strategies</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Developing and implementing effective risk mitigation strategies is essential for maintaining compliant AI systems. These strategies should address both technical and operational risks.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Mitigation Approaches:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                        <strong>Technical Controls:</strong> Implementation of security measures, monitoring systems, and fail-safes
                                    </li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                        <strong>Operational Controls:</strong> Procedures, policies, and guidelines for system operation
                                    </li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                        <strong>Management Controls:</strong> Oversight mechanisms and decision-making frameworks
                                    </li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">
                                        <strong>Documentation Controls:</strong> Record-keeping and evidence maintenance procedures
                                    </li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">4. Continuous Risk Monitoring</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Ongoing risk monitoring ensures that AI systems maintain compliance and safety throughout their operational lifecycle. This includes regular assessments and updates to risk management strategies.
                            </p>
                            <div style="display: flex; gap: 2rem;">
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0.5rem 0;">Monitoring Activities:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Performance tracking</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk indicator monitoring</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Incident detection</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Trend analysis</li>
                                    </ul>
                                </div>
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0.5rem 0;">Response Procedures:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Incident response plans</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Escalation procedures</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Corrective actions</li>
                                        <li style="color: #f3f4f6; margin: 0.3rem 0;">Stakeholder communication</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">📚 Risk Management Tools</h5>
                            <div style="display: flex; gap: 2rem;">
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0 0 0.3rem 0;">Assessment Tools:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Risk assessment matrices</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Impact evaluation tools</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Probability calculators</li>
                                    </ul>
                                </div>
                                <div style="flex: 1;">
                                    <h6 style="color: #fbbf24; margin: 0 0 0.3rem 0;">Management Resources:</h6>
                                    <ul style="margin: 0; padding-left: 1.5rem;">
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Control frameworks</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Monitoring templates</li>
                                        <li style="color: #f3f4f6; margin: 0.2rem 0;">Response playbooks</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                    """
                elif week_num == 7:
                    expanded_content = """
                    <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(30, 64, 175, 0.1); border-radius: 10px;">
                        <h4 style="color: #fbbf24; margin: 0 0 1rem 0; font-size: 1.2rem;">
                            📚 Expanded Topic Content:
                        </h4>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">1. US AI Executive Order 14110</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                The US AI Executive Order 14110 sets out a comprehensive approach to AI governance, emphasizing transparency, accountability, and international cooperation.
                            </p>
                            <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Key principles and requirements</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Guidelines for AI system development and deployment</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">International collaboration and standards</li>
                            </ul>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">2. China's AI Regulations</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                China's AI regulations are designed to promote ethical AI development, protect personal data, and ensure national security.
                            </p>
                            <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Key regulations and guidelines</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Data privacy and security measures</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">AI ethics and governance frameworks</li>
                            </ul>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">3. UK AI White Paper Approach</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                The UK AI white paper approach emphasizes the importance of AI governance frameworks, international cooperation, and ethical considerations.
                            </p>
                            <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Key principles and requirements</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">Guidelines for AI system development and deployment</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">International collaboration and standards</li>
                            </ul>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">4. International Coordination Efforts</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                International coordination efforts are crucial for addressing cross-border AI governance challenges.
                            </p>
                            <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">UNAI's AI Governance Principles</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">OECD's AI Governance Guidelines</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">EU-US AI Dialogue</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">EU-China AI Cooperation</li>
                                <li style="color: #f3f4f6; margin: 0.3rem 0;">EU-UK AI Cooperation</li>
                            </ul>
                        </div>
                    </div>
                    """
                elif week_num == 8:
                    expanded_content = """
                    <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(30, 64, 175, 0.1); border-radius: 10px;">
                        <h4 style="color: #fbbf24; margin: 0 0 1rem 0; font-size: 1.2rem;">
                            📚 Expanded Topic Content:
                        </h4>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">1. Governance Operating Models</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Designing effective governance operating models is crucial for aligning AI governance with organizational objectives and regulatory requirements.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Elements:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Roles and responsibilities</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">RACI matrices</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Change management strategies</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Training and awareness programs</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">2. Role Definitions and RACI Matrices</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Understanding role definitions and RACI matrices is essential for effective governance and decision-making.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Components:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Roles and responsibilities</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">RACI matrices</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Change management strategies</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Training and awareness programs</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">3. Change Management Strategies</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Implementing effective change management strategies is crucial for managing AI governance transitions and ensuring stakeholder buy-in.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Strategies:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Stakeholder engagement</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Communication strategies</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk assessment and mitigation</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Resource allocation and prioritization</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">4. Training and Awareness Programs</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Developing comprehensive training and awareness programs is essential for empowering stakeholders to understand and support AI governance initiatives.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Components:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI ethics training</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Regulatory compliance training</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Stakeholder communication training</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk management training</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    """
                elif week_num == 9:
                    expanded_content = """
                    <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(30, 64, 175, 0.1); border-radius: 10px;">
                        <h4 style="color: #fbbf24; margin: 0 0 1rem 0; font-size: 1.2rem;">
                            📚 Expanded Topic Content:
                        </h4>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">1. Audit Planning and Execution</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Effective audit planning and execution is crucial for ensuring that AI governance initiatives are effectively implemented and compliant with regulatory requirements.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Elements:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Scope of audit</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk assessment</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Audit methodology</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Stakeholder engagement</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">2. Compliance Monitoring Systems</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Implementing effective compliance monitoring systems is crucial for maintaining compliance with regulatory requirements and identifying areas for improvement.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Components:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Key performance indicators (KPIs)</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Risk assessment frameworks</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Monitoring tools and techniques</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Data collection and analysis methods</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">3. Key Performance Indicators</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Establishing clear key performance indicators (KPIs) is essential for measuring the success of AI governance initiatives and identifying areas for improvement.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key KPIs:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI system safety and security</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Regulatory compliance</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Stakeholder satisfaction</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI system impact on society</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">4. Regulatory Reporting Requirements</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Understanding regulatory reporting requirements is crucial for ensuring that AI governance initiatives are effectively communicated and reported to stakeholders.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Areas:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI system safety and security</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Regulatory compliance</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Stakeholder satisfaction</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI system impact on society</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    """
                elif week_num == 10:
                    expanded_content = """
                    <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(30, 64, 175, 0.1); border-radius: 10px;">
                        <h4 style="color: #fbbf24; margin: 0 0 1rem 0; font-size: 1.2rem;">
                            📚 Expanded Topic Content:
                        </h4>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">1. AI Incident Classification</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Understanding AI incident classification is crucial for developing effective incident response plans and crisis communication strategies.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Categories:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Safety-related incidents</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Security-related incidents</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Privacy-related incidents</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Ethical violations</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">2. Response Team Structures</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Establishing effective response team structures is crucial for managing AI incidents effectively and minimizing their impact on stakeholders.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Elements:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Roles and responsibilities</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Communication channels</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Stakeholder engagement</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Incident response protocols</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">3. Crisis Communication Strategies</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Developing effective crisis communication strategies is crucial for managing stakeholder expectations and minimizing the impact of AI incidents.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Elements:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Stakeholder identification</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Communication channels</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Message development</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Communication frequency and format</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">4. Regulatory Breach Reporting</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Understanding regulatory breach reporting requirements is crucial for ensuring that AI incidents are reported promptly and appropriately to regulatory authorities.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Areas:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Incident reporting procedures</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Breach notification requirements</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Stakeholder notification protocols</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Public reporting requirements</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    """
                elif week_num == 11:
                    expanded_content = """
                    <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(30, 64, 175, 0.1); border-radius: 10px;">
                        <h4 style="color: #fbbf24; margin: 0 0 1rem 0; font-size: 1.2rem;">
                            📚 Expanded Topic Content:
                        </h4>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">1. Generative AI Governance</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Generative AI governance involves establishing clear guidelines and ethical standards for the development and deployment of generative AI systems.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Elements:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI ethics frameworks</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI risk assessment methodologies</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI system transparency</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI system accountability</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">2. Quantum Machine Learning Implications</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Quantum machine learning has the potential to revolutionize AI, but it also presents new challenges for AI governance.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Considerations:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Quantum computing's impact on AI</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Quantum machine learning algorithms</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Quantum machine learning applications</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Quantum machine learning ethics</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">3. Autonomous Systems Regulation</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Autonomous systems regulation involves establishing clear guidelines and ethical standards for the development and deployment of autonomous systems.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Elements:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Autonomy assessment methodologies</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Safety and security requirements</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Human oversight mechanisms</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Regulatory compliance</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">4. Future Regulatory Trends</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Emerging trends in AI governance, such as AI ethics frameworks, international cooperation, and regulatory harmonization, are shaping the future of AI regulation.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Trends:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI ethics frameworks</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">International cooperation</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Regulatory harmonization</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Cross-border AI regulation</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    """
                elif week_num == 12:
                    expanded_content = """
                    <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(30, 64, 175, 0.1); border-radius: 10px;">
                        <h4 style="color: #fbbf24; margin: 0 0 1rem 0; font-size: 1.2rem;">
                            📚 Expanded Topic Content:
                        </h4>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">1. AIGP Exam Structure and Format</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Understanding the AIGP exam structure and format is crucial for preparing effectively for the certification exam.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Components:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Exam structure</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Exam format</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Exam content</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Exam preparation strategies</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">2. Key Concept Review</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Reviewing key concepts from the AI governance curriculum is essential for consolidating learning outcomes and preparing for the exam.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Concepts:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI governance frameworks</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI risk management frameworks</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI system transparency</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI system accountability</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">3. Practice Questions and Scenarios</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Practicing with sample questions and scenarios is essential for developing problem-solving skills and preparing for the exam.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Areas:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI governance frameworks</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI risk management frameworks</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI system transparency</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">AI system accountability</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div style="margin-bottom: 1.5rem;">
                            <h5 style="color: #fbbf24; margin: 0 0 0.5rem 0; font-size: 1.1rem;">4. Final Project Presentation</h5>
                            <p style="color: #f3f4f6; margin: 0.5rem 0; line-height: 1.6;">
                                Preparing a final project presentation is essential for demonstrating your understanding of AI governance concepts and applying them to a real-world scenario.
                            </p>
                            <div style="background: rgba(30, 64, 175, 0.05); padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                                <h6 style="color: #fbbf24; margin: 0 0 0.5rem 0;">Key Elements:</h6>
                                <ul style="margin: 0; padding-left: 1.5rem;">
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Project proposal</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Project development</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Project presentation</li>
                                    <li style="color: #f3f4f6; margin: 0.3rem 0;">Project evaluation</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    """
                
                html_content = f"""
                <div style="padding: 1.5rem; background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); 
                            color: white; border-radius: 15px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                    <h3 style="color: #fbbf24; margin-top: 0; font-size: 1.4rem; font-weight: bold;">
                        {module['title']}
                    </h3>
                    <p style="color: #e5e7eb; margin: 1rem 0; font-size: 1.1rem;">
                        <strong style="color: #fbbf24;">Difficulty:</strong> 
                        <span style="background: rgba(251, 191, 36, 0.2); padding: 0.2rem 0.5rem; border-radius: 5px;">
                            {module['difficulty']}
                        </span> | 
                        <strong style="color: #fbbf24;">Est. Hours:</strong> 
                        <span style="background: rgba(251, 191, 36, 0.2); padding: 0.2rem 0.5rem; border-radius: 5px;">
                            {module['estimated_hours']}h
                        </span>
                    </p>
                    
                    <h4 style="color: #fbbf24; margin: 1.5rem 0 0.5rem 0; font-size: 1.2rem;">
                        🎯 Learning Objectives:
                    </h4>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        {''.join([f'<li style="color: #f3f4f6; margin: 0.3rem 0; line-height: 1.4;">{obj}</li>' for obj in module['objectives']])}
                    </ul>
                    
                    <h4 style="color: #fbbf24; margin: 1.5rem 0 0.5rem 0; font-size: 1.2rem;">
                        📋 Topics Covered:
                    </h4>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        {''.join([f'<li style="color: #f3f4f6; margin: 0.3rem 0; line-height: 1.4;">{topic}</li>' for topic in module['topics']])}
                    </ul>
                    
                    <h4 style="color: #fbbf24; margin: 1.5rem 0 0.5rem 0; font-size: 1.2rem;">
                        📄 Deliverables:
                    </h4>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        {''.join([f'<li style="color: #f3f4f6; margin: 0.3rem 0; line-height: 1.4; font-weight: 500;">{deliv}</li>' for deliv in module['deliverables']])}
                    </ul>
                </div>
                {expanded_content}
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
        
        def show_aigp_resources():
            """Display comprehensive AIGP certification resources with expand/collapse functionality"""
            
            # JavaScript functions for toggle functionality
            js_functions = """
            <script>
                function toggleCategory(categoryId) {
                    const content = document.getElementById(categoryId);
                    const toggleBtn = document.getElementById('toggle-' + categoryId);
                    
                    if (content.style.display === 'none' || content.style.display === '') {
                        content.style.display = 'block';
                        toggleBtn.innerHTML = '🔽';
                    } else {
                        content.style.display = 'none';
                        toggleBtn.innerHTML = '▶️';
                    }
                }
                
                function expandAll() {
                    const allContents = document.querySelectorAll('[id$="-content"]');
                    const allButtons = document.querySelectorAll('[id^="toggle-"]');
                    
                    allContents.forEach(content => {
                        content.style.display = 'block';
                    });
                    
                    allButtons.forEach(btn => {
                        btn.innerHTML = '🔽';
                    });
                }
                
                function collapseAll() {
                    const allContents = document.querySelectorAll('[id$="-content"]');
                    const allButtons = document.querySelectorAll('[id^="toggle-"]');
                    
                    allContents.forEach(content => {
                        content.style.display = 'none';
                    });
                    
                    allButtons.forEach(btn => {
                        btn.innerHTML = '▶️';
                    });
                }
                
                function hideResources() {
                    const resourcesContainer = document.getElementById('resources-container');
                    resourcesContainer.style.display = 'none';
                }
            </script>
            """
            
            resources_html = js_functions + """
            <div id="resources-container" style="background: #1a1a1a; border-radius: 12px; padding: 2rem; color: #ffffff; margin: 1rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h2 style="color: #3b82f6; margin: 0; font-size: 1.8rem;">
                        🎓 IAPP AIGP Certification Resources
                    </h2>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <button onclick="expandAll()" style="background: #059669; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 0.9rem;">
                            📤 Expand All
                        </button>
                        <button onclick="collapseAll()" style="background: #dc2626; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 0.9rem;">
                            📥 Collapse All
                        </button>
                        <button onclick="hideResources()" style="background: #6b7280; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 0.9rem;">
                            👁️ Hide Resources
                        </button>
                    </div>
                </div>
                <p style="color: #d1d5db; text-align: center; margin: 1rem 0; font-size: 1.1rem;">
                    Comprehensive collection of resources for AI Governance Professional certification preparation
                </p>
            """
            
            for category_key, category_data in self.aigp_resources.items():
                category_id = f"{category_key}-content"
                toggle_id = f"toggle-{category_key}-content"
                
                resources_html += f"""
                <div style="margin: 2rem 0; border: 2px solid #3b82f6; border-radius: 8px; background: #2a2a2a;">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 1.5rem; cursor: pointer;" onclick="toggleCategory('{category_id}')">
                        <div>
                            <h3 style="color: #60a5fa; margin: 0; font-size: 1.4rem;">
                                {category_data['title']}
                            </h3>
                            <p style="color: #d1d5db; margin: 0.5rem 0 0 0; font-style: italic;">
                                {category_data['description']}
                            </p>
                        </div>
                        <span id="{toggle_id}" style="font-size: 1.5rem; color: #60a5fa;">🔽</span>
                    </div>
                    <div id="{category_id}" style="display: block; padding: 0 1.5rem 1.5rem 1.5rem;">
                """
                
                for resource in category_data['resources']:
                    type_color = {
                        'Official': '#10b981',
                        'Study Material': '#3b82f6', 
                        'Training': '#8b5cf6',
                        'Resource Center': '#f59e0b',
                        'News': '#ef4444',
                        'Conference': '#8b5cf6',
                        'Regulation': '#dc2626',
                        'Proposed Directive': '#7c3aed',
                        'Framework': '#059669',
                        'Policy': '#7c3aed',
                        'Executive Order': '#be123c',
                        'Blueprint': '#0891b2',
                        'Proposed Legislation': '#0891b2',
                        'Directive': '#7c3aed',
                        'Voluntary Framework': '#059669',
                        'Guidelines': '#166534',
                        'Ethics Framework': '#15803d',
                        'National Strategy': '#1e40af',
                        'International Agreement': '#0369a1',
                        'Standard': '#166534',
                        'Design Framework': '#15803d',
                        'International Principles': '#0369a1',
                        'Policy Hub': '#1e40af',
                        'International Partnership': '#0369a1',
                        'Global Standard': '#166534',
                        'International Treaty': '#7c2d12',
                        'Industry Initiative': '#0369a1',
                        'Declaration': '#7c3aed',
                        'Principles': '#4338ca',
                        'Global Initiative': '#0369a1',
                        'International Code': '#7c2d12',
                        'Database': '#7c2d12',
                        'Standards Coordination': '#166534',
                        'Technical Standards': '#15803d',
                        'Research Institute': '#7c3aed',
                        'Research Center': '#6366f1',
                        'Research Program': '#8b5cf6',
                        'Think Tank': '#1e40af',
                        'Policy Institute': '#3730a3',
                        'Policy Research': '#4338ca',
                        'Annual Report': '#b91c1c',
                        'Industry Report': '#dc2626',
                        'Ethics Institute': '#059669',
                        'Educational Program': '#0d9488',
                        'Online Education': '#0891b2',
                        'Online Course': '#3b82f6',
                        'Template': '#ea580c',
                        'Tool': '#db2777',
                        'Framework Tool': '#2563eb',
                        'Assessment Tool': '#c2410c',
                        'Documentation Tool': '#7c3aed',
                        'Official Guide': '#059669',
                        'Practice Material': '#0891b2',
                        'Reference': '#4338ca',
                        'Webinar': '#be185d',
                        'Community': '#16a34a'
                    }.get(resource['type'], '#6b7280')
                    
                    resources_html += f"""
                    <div style="border-left: 4px solid {type_color}; padding: 1rem; margin: 1rem 0; background: #1a1a1a; border-radius: 4px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <h4 style="color: #e5e7eb; margin: 0; font-size: 1.1rem;">
                                <a href="{resource['url']}" target="_blank" style="color: #60a5fa; text-decoration: none;">
                                    {resource['name']} ↗
                                </a>
                            </h4>
                            <span style="background: {type_color}; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: bold;">
                                {resource['type']}
                            </span>
                        </div>
                        <p style="color: #d1d5db; margin: 0; font-size: 0.95rem; line-height: 1.4;">
                            {resource['description']}
                        </p>
                    </div>
                    """
                
                resources_html += "</div></div>"
            
            resources_html += """
                <div style="margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, #065f46 0%, #059669 100%); border-radius: 8px; text-align: center;">
                    <h3 style="color: #ffffff; margin: 0 0 1rem 0; font-size: 1.3rem;">🎯 Quick Start Guide</h3>
                    <p style="color: #d1fae5; margin: 0.5rem 0; font-size: 1rem;">
                        1. Start with <strong>IAPP AIGP Certification Homepage</strong> for official requirements<br/>
                        2. Review <strong>EU AI Act Official Text</strong> for core content<br/>
                        3. Use <strong>NIST AI Risk Management Framework</strong> for practical understanding<br/>
                        4. Practice with <strong>AIGP Practice Questions</strong> before the exam
                    </p>
                </div>
            </div>
            """
            
            return resources_html, gr.update(visible=True)
        
        # Authentication and Notes Functions
        def show_auth_interface():
            """Show authentication interface when Add Notes is clicked"""
            return gr.update(visible=True)
        
        def handle_login(email, password):
            """Handle user login"""
            if not email or not password:
                return gr.update(value="⚠️ Please enter both email and password", visible=True), gr.update(visible=True), gr.update(visible=False)
            
            success, result = self.auth_manager.authenticate_user(email, password)
            
            if success:
                user_html = f"""
                <div style="background: #065f46; border-radius: 8px; padding: 1rem; color: white;">
                    <h4 style="color: #10b981; margin: 0;">👤 Logged in as:</h4>
                    <p style="margin: 0.5rem 0 0 0; font-weight: 600;">{email}</p>
                </div>
                """
                # Switch to notes interface
                return (
                    gr.update(value="✅ Login successful", visible=True),
                    gr.update(visible=False),  # Hide auth section
                    gr.update(visible=True),   # Show notes section
                    user_html,  # Update user info
                    1,  # Default week selection
                    "",  # Clear note title
                    "",  # Clear note content
                    self.get_notes_html(1)  # Load notes for week 1
                )
            else:
                return gr.update(value=f"❌ {result}", visible=True), gr.update(visible=True), gr.update(visible=False)
        
        def handle_registration(email, password, confirm_password):
            """Handle user registration"""
            if not email or not password or not confirm_password:
                return gr.update(value="⚠️ Please fill in all fields", visible=True)
            
            if password != confirm_password:
                return gr.update(value="❌ Passwords do not match", visible=True)
            
            if len(password) < 6:
                return gr.update(value="❌ Password must be at least 6 characters", visible=True)
            
            success, message = self.auth_manager.create_user(email, password)
            
            if success:
                return gr.update(value=f"✅ User registered successfully. Please login now.", visible=True)
            else:
                return gr.update(value=f"❌ {message}", visible=True)
        
        def handle_logout():
            """Handle user logout"""
            self.auth_manager.logout()
            return (
                gr.update(visible=True),   # Show auth section
                gr.update(visible=False),  # Hide notes section
                "",  # Clear user info
                "",  # Clear login email
                "",  # Clear login password
                gr.update(value="👋 Logged out successfully", visible=True)
            )
        
        def save_note(week_num, title, content, edit_id, is_edit_mode):
            """Save or update a note"""
            if not title or not content:
                return "⚠️ Please enter both title and content", "", "", False, None, self.get_notes_html(week_num)
            
            if is_edit_mode and edit_id:
                # Update existing note
                success, message = self.update_note(edit_id, title, content)
                if success:
                    return f"✅ Note updated successfully", "", "", False, None, self.get_notes_html(week_num)
                else:
                    return f"❌ {message}", title, content, is_edit_mode, edit_id, self.get_notes_html(week_num)
            else:
                # Create new note
                success, message = self.create_note(week_num, title, content)
                if success:
                    return f"✅ Note saved successfully", "", "", False, None, self.get_notes_html(week_num)
                else:
                    return f"❌ {message}", title, content, is_edit_mode, edit_id, self.get_notes_html(week_num)
        
        def clear_note_form():
            """Clear the note form"""
            return "", "", False, None
        
        def load_notes_for_week(week_num):
            """Load notes when week selection changes"""
            return self.get_notes_html(week_num)
        
        def edit_note_action(note_id, title, content):
            """Prepare form for editing a note"""
            return title, content, True, note_id
        
        def delete_note_action(note_id, week_num):
            """Delete a note"""
            success, message = self.delete_note(note_id)
            if success:
                return f"✅ Note deleted successfully", self.get_notes_html(week_num)
            else:
                return f"❌ {message}", self.get_notes_html(week_num)
        
        # Event handlers
        week_selector.change(
            fn=update_week_content,
            inputs=[week_selector],
            outputs=[week_content]
        )
        
        view_resources_btn.click(
            fn=show_aigp_resources,
            inputs=[],
            outputs=[resources_display, resources_display]
        )
        
        # Add Notes button event
        add_notes_btn.click(
            fn=show_auth_interface,
            outputs=[auth_notes_area]
        )
        
        # Authentication events
        login_btn.click(
            fn=handle_login,
            inputs=[login_email, login_password],
            outputs=[login_message, auth_section, notes_section, user_info, notes_week_selector, note_title, note_content, existing_notes]
        )
        
        register_btn.click(
            fn=handle_registration,
            inputs=[reg_email, reg_password, reg_confirm],
            outputs=[register_message]
        )
        
        logout_btn.click(
            fn=handle_logout,
            outputs=[auth_section, notes_section, user_info, login_email, login_password, login_message]
        )
        
        # Notes management events
        save_note_btn.click(
            fn=save_note,
            inputs=[notes_week_selector, note_title, note_content, edit_note_id, edit_mode],
            outputs=[login_message, note_title, note_content, edit_mode, edit_note_id, existing_notes]
        )
        
        clear_note_btn.click(
            fn=clear_note_form,
            outputs=[note_title, note_content, edit_mode, edit_note_id]
        )
        
        notes_week_selector.change(
            fn=load_notes_for_week,
            inputs=[notes_week_selector],
            outputs=[existing_notes]
        )
        
        # Initialize with first week
        week_content.value = update_week_content(1)
        progress_chart.value = create_progress_chart()
        
        return week_selector, week_content, progress_chart 