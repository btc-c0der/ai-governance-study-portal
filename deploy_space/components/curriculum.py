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
                    "title": "🏢 Organizational Implementation",
                    "objectives": [
                        "Design governance operating models",
                        "Establish roles and responsibilities",
                        "Implement change management"
                    ],
                    "topics": [
                        "Governance operating models",
                        "Role definitions and RACI matrices",
                        "Change management strategies",
                        "Training and awareness programs"
                    ],
                    "deliverables": ["Operating model", "Training program"],
                    "estimated_hours": 10,
                    "difficulty": "Advanced",
                    "resources": [
                        "Organizational design guides",
                        "Change management frameworks",
                        "Training materials"
                    ]
                },
                {
                    "week": 9,
                    "title": "🔍 Audit & Compliance Monitoring",
                    "objectives": [
                        "Design audit frameworks",
                        "Implement continuous monitoring",
                        "Learn compliance reporting"
                    ],
                    "topics": [
                        "Audit planning and execution",
                        "Compliance monitoring systems",
                        "Key performance indicators",
                        "Regulatory reporting requirements"
                    ],
                    "deliverables": ["Audit framework", "KPI dashboard"],
                    "estimated_hours": 9,
                    "difficulty": "Advanced",
                    "resources": [
                        "Audit methodologies",
                        "Monitoring tools",
                        "Reporting templates"
                    ]
                },
                {
                    "week": 10,
                    "title": "🚨 Incident Management & Response",
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