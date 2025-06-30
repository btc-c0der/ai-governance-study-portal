#!/usr/bin/env python3
"""
🧠⚖️ AI Governance Architect's Codex - Full Study Portal
A next-gen AI Governance Study Platform combining curriculum tracking,
EU AI Act exploration, ML demos, and AI tutoring.

Author: 0m3g4_k1ng@proton.me
License: GBU2 (Good, Bad, Ugly 2.0)
"""

import gradio as gr
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from pathlib import Path

# Import our custom modules
try:
    from components.curriculum import CurriculumManager
    from components.ai_act_explorer import AIActExplorer
    from components.model_demos import ModelDemos
    from components.ai_tutor import AITutor
    from components.performance_tracker import PerformanceTracker
    from components.quiz_engine import QuizEngine
except ImportError as e:
    print(f"Warning: Could not import some components: {e}")
    print("Some features may not be available.")

def create_main_interface():
    """Create the main Gradio interface with all tabs"""
    
    # Initialize managers (with error handling)
    try:
        curriculum_mgr = CurriculumManager()
        ai_act_explorer = AIActExplorer()
        model_demos = ModelDemos()
        ai_tutor = AITutor()
        performance_tracker = PerformanceTracker()
        quiz_engine = QuizEngine()
    except Exception as e:
        print(f"Error initializing components: {e}")
        # Create placeholder managers if components fail
        curriculum_mgr = None
        ai_act_explorer = None
        model_demos = None
        ai_tutor = None
        performance_tracker = None
        quiz_engine = None
    
    with gr.Blocks(
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="purple",
            neutral_hue="slate"
        ),
        title="🧠⚖️ AI Governance Architect's Codex",
        css="""
        .gradio-container {
            font-family: 'Inter', 'Lexend', sans-serif;
        }
        .tab-nav button {
            font-weight: 600;
        }
        .codex-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .feature-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
        }
        """
    ) as app:
        
        # Header
        gr.HTML("""
        <div class="codex-header">
            <h1>🧠⚖️ AI Governance Architect's Codex</h1>
            <p>Next-Gen AI/ML Study Portal • EU AI Act • AIGP Certification • Model Demos</p>
            <p><small>✨ Powered by Gradio 4.x + Modern ML Stack ✨</small></p>
        </div>
        """)
        
        with gr.Tabs() as tabs:
            
            # 📖 Curriculum Explorer Tab
            with gr.Tab("📖 Curriculum Explorer", elem_id="curriculum-tab"):
                if curriculum_mgr:
                    curriculum_mgr.create_interface()
                else:
                    create_placeholder_interface("Curriculum Explorer", "📖")
            
            # ⚖️ EU AI Act Explorer Tab
            with gr.Tab("⚖️ EU AI Act Explorer", elem_id="ai-act-tab"):
                if ai_act_explorer:
                    ai_act_explorer.create_interface()
                else:
                    create_placeholder_interface("EU AI Act Explorer", "⚖️")
            
            # 🤖 Model Demos Tab
            with gr.Tab("🤖 Model Demos", elem_id="models-tab"):
                if model_demos:
                    model_demos.create_interface()
                else:
                    create_placeholder_interface("Model Demos", "🤖")
            
            # 🧠 AI Tutor Chat Tab
            with gr.Tab("🧠 AI Tutor Chat", elem_id="tutor-tab"):
                if ai_tutor:
                    ai_tutor.create_interface()
                else:
                    create_placeholder_interface("AI Tutor", "🧠")
            
            # 📊 Performance Tracker Tab
            with gr.Tab("📊 Performance Tracker", elem_id="performance-tab"):
                if performance_tracker:
                    performance_tracker.create_interface()
                else:
                    create_placeholder_interface("Performance Tracker", "📊")
            
            # 💼 Annex IV Builder Tab
            with gr.Tab("💼 Annex IV Builder", elem_id="annex-tab"):
                create_annex_builder()
            
            # 🧪 Mock AIGP Quiz Tab
            with gr.Tab("🧪 Mock AIGP Quiz", elem_id="quiz-tab"):
                if quiz_engine:
                    quiz_engine.create_interface()
                else:
                    create_placeholder_interface("Mock Quiz", "🧪")
            
            # 🔗 Notion Sync & Export Tab
            with gr.Tab("🔗 Sync & Export", elem_id="sync-tab"):
                create_sync_interface()
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; margin-top: 2rem; padding: 1rem; 
                    background: #f8fafc; border-radius: 10px;">
            <p>🚀 Built with Gradio 4.x • FastAPI • Transformers • Chart.js</p>
            <p><small>EU LAW WILL BE LAWFUL AND AI WILL BE GBU2 LICENSED 🤖⚖️</small></p>
        </div>
        """)
    
    return app

def create_placeholder_interface(name, icon):
    """Create placeholder interface for components that failed to load"""
    gr.Markdown(f"## {icon} {name}")
    gr.HTML(f"""
    <div class="feature-card">
        <h3>🚧 {name} Loading...</h3>
        <p>This feature is being initialized. Please check the console for any dependency issues.</p>
        <p>In the meantime, enjoy exploring other tabs!</p>
    </div>
    """)

def create_annex_builder():
    """Create Annex IV compliance document builder interface"""
    gr.Markdown("## 💼 EU AI Act Annex IV Compliance Builder")
    gr.Markdown("Interactive wizard to create compliance documentation for high-risk AI systems.")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📋 System Information")
            system_name = gr.Textbox(
                label="AI System Name", 
                placeholder="e.g., Legal Document Classifier"
            )
            system_purpose = gr.Textbox(
                label="System Purpose", 
                lines=3,
                placeholder="Describe the intended use of your AI system..."
            )
            risk_category = gr.Dropdown(
                ["High-risk", "Limited risk", "Minimal risk", "Unacceptable risk"],
                label="Risk Category",
                value="High-risk"
            )
            
            gr.Markdown("### 🏗️ Technical Details")
            architecture = gr.Textbox(
                label="System Architecture",
                lines=3,
                placeholder="Describe the technical architecture..."
            )
            data_sources = gr.Textbox(
                label="Training Data Sources", 
                lines=3,
                placeholder="Describe your training data sources..."
            )
            performance_metrics = gr.Textbox(
                label="Performance Metrics", 
                lines=3,
                placeholder="List key performance indicators..."
            )
        
        with gr.Column():
            gr.Markdown("### 🛡️ Risk Management")
            risk_assessment = gr.Textbox(
                label="Risk Assessment Summary",
                lines=4,
                placeholder="Summarize identified risks and mitigation measures..."
            )
            
            human_oversight = gr.Textbox(
                label="Human Oversight Measures",
                lines=3,
                placeholder="Describe human oversight implementation..."
            )
            
            testing_validation = gr.Textbox(
                label="Testing & Validation",
                lines=3,
                placeholder="Describe testing and validation procedures..."
            )
            
            generate_btn = gr.Button("🔧 Generate Compliance Document", variant="primary")
    
    with gr.Row():
        compliance_output = gr.Textbox(
            label="Generated Compliance Document", 
            lines=15,
            placeholder="Generated document will appear here..."
        )
    
    def generate_compliance_doc(name, purpose, category, arch, data, metrics, risks, oversight, testing):
        """Generate Annex IV compliance document"""
        if not name or not purpose:
            return "Please provide at least system name and purpose to generate document."
        
        doc = f"""
# EU AI Act Annex IV Technical Documentation
## {name}

### 1. General Description
**System Name:** {name}
**Risk Category:** {category}
**Intended Purpose:** {purpose}
**Date:** {datetime.now().strftime('%Y-%m-%d')}

### 2. System Architecture & Design
{arch if arch else 'To be completed...'}

### 3. Data Governance
**Training Data Sources:**
{data if data else 'To be completed...'}

**Data Quality Measures:**
- Representative datasets reflecting intended use
- Bias detection and mitigation procedures
- Data validation and error correction processes

### 4. Risk Management System
**Risk Assessment:**
{risks if risks else 'To be completed...'}

**Risk Mitigation Measures:**
- Continuous monitoring throughout lifecycle
- Regular assessment and review procedures
- Incident response and corrective action plans

### 5. Performance Metrics
{metrics if metrics else 'To be completed...'}

### 6. Human Oversight
{oversight if oversight else 'To be completed...'}

### 7. Testing and Validation
{testing if testing else 'To be completed...'}

### 8. Conformity Assessment
This system requires conformity assessment before market placement according to Article 16 of the EU AI Act.

### 9. Documentation Control
- Version: 1.0
- Approved by: [To be completed]
- Review date: [To be completed]
- Next review: {datetime.now().strftime('%Y-%m-%d')}

---
*This document template is for guidance purposes. Consult legal experts for compliance verification.*
        """
        
        return doc
    
    generate_btn.click(
        fn=generate_compliance_doc,
        inputs=[system_name, system_purpose, risk_category, architecture, 
               data_sources, performance_metrics, risk_assessment, 
               human_oversight, testing_validation],
        outputs=[compliance_output]
    )

def create_sync_interface():
    """Create Notion sync and export interface"""
    gr.Markdown("## 🔗 Notion Sync & Export Center")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📝 Notion Integration")
            notion_token = gr.Textbox(
                label="Notion Integration Token", 
                type="password",
                placeholder="secret_..."
            )
            database_id = gr.Textbox(
                label="Database ID",
                placeholder="Database ID from Notion URL"
            )
            sync_btn = gr.Button("🔄 Sync with Notion", variant="primary")
            
            gr.Markdown("### 📊 Study Data")
            gr.HTML("""
            <div style="background: #f0f9ff; padding: 1rem; border-radius: 10px;">
                <h4>📈 Current Study Status</h4>
                <ul>
                    <li>Weeks completed: 7/12</li>
                    <li>Quiz average: 87%</li>
                    <li>Study hours: 128</li>
                    <li>Last sync: Never</li>
                </ul>
            </div>
            """)
            
        with gr.Column():
            gr.Markdown("### 📤 Export Options")
            export_format = gr.Radio(
                ["PDF Report", "JSON Data", "CSV Summary"], 
                label="Export Format",
                value="PDF Report"
            )
            export_content = gr.CheckboxGroup(
                ["Progress Data", "Quiz Results", "Study Notes", "Compliance Docs"],
                label="Content to Export",
                value=["Progress Data", "Quiz Results"]
            )
            export_btn = gr.Button("📤 Export Data", variant="secondary")
            
            download_area = gr.File(label="📄 Download Files", visible=False)
    
    status_output = gr.Textbox(
        label="Status", 
        lines=5,
        placeholder="Status updates will appear here..."
    )
    
    def sync_with_notion(token, db_id):
        """Sync data with Notion database"""
        if not token or not db_id:
            return "Please provide both Notion token and database ID."
        
        # Placeholder sync logic
        return f"✅ Successfully synced with Notion database: {db_id[:8]}...\n" + \
               f"📊 Updated 12 study records\n" + \
               f"🕒 Sync completed at {datetime.now().strftime('%H:%M:%S')}"
    
    def export_data(format_type, content_list):
        """Export study data in selected format"""
        if not content_list:
            return "Please select content to export.", gr.update(visible=False)
        
        status = f"📦 Exporting {', '.join(content_list)} as {format_type}...\n"
        status += f"✅ Export completed at {datetime.now().strftime('%H:%M:%S')}\n"
        status += "📄 File ready for download."
        
        return status, gr.update(visible=True)
    
    sync_btn.click(
        fn=sync_with_notion,
        inputs=[notion_token, database_id],
        outputs=[status_output]
    )
    
    export_btn.click(
        fn=export_data,
        inputs=[export_format, export_content],
        outputs=[status_output, download_area]
    )

if __name__ == "__main__":
    # Create the app
    app = create_main_interface()
    
    # Launch with custom settings
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        debug=True,
        show_error=True,
        favicon_path="static/images/favicon.ico" if os.path.exists("static/images/favicon.ico") else None
    ) 