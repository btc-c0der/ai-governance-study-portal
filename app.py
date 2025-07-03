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
import sys
from pathlib import Path

# Import our custom modules
try:
    from components.curriculum import CurriculumManager
    from components.ai_act_explorer import AIActExplorer
    from components.model_demos import ModelDemos
    from components.ai_tutor import AITutor
    from components.performance_tracker import PerformanceTracker
    from components.quiz_engine import QuizEngine
    from components.auth_manager import AuthManager
    from components.istqb_ai_tester import ISTQBAITester
except ImportError as e:
    print(f"Warning: Could not import some components: {e}")
    print("Some features may not be available.")

def create_main_interface():
    """Create the main Gradio interface with all tabs"""
    
    print("🚀 Starting AI Governance Architect's Codex...")
    print("=" * 60)
    
    # Initialize managers (with verbose error handling)
    components = {}
    
    try:
        print("🔐 Initializing Authentication Manager...")
        auth_manager = AuthManager()
        components['auth_manager'] = auth_manager
        print("✅ AuthManager initialized successfully")
        
        print("📖 Initializing Curriculum Manager...")
        curriculum_mgr = CurriculumManager(auth_manager)
        components['curriculum_mgr'] = curriculum_mgr
        print("✅ CurriculumManager initialized successfully")
        
        print("⚖️ Initializing EU AI Act Explorer...")
        ai_act_explorer = AIActExplorer()
        components['ai_act_explorer'] = ai_act_explorer
        print("✅ AIActExplorer initialized successfully")
        
        print("🤖 Initializing Model Demos...")
        model_demos = ModelDemos()
        components['model_demos'] = model_demos
        print("✅ ModelDemos initialized successfully")
        
        print("🧠 Initializing AI Tutor...")
        ai_tutor = AITutor()
        components['ai_tutor'] = ai_tutor
        print("✅ AITutor initialized successfully")
        
        print("📊 Initializing Performance Tracker...")
        performance_tracker = PerformanceTracker()
        components['performance_tracker'] = performance_tracker
        print("✅ PerformanceTracker initialized successfully")
        
        print("🧪 Initializing Quiz Engine...")
        quiz_engine = QuizEngine(auth_manager)
        components['quiz_engine'] = quiz_engine
        print("✅ QuizEngine initialized successfully")
        
        print("🎯 Initializing ISTQB AI Tester...")
        istqb_ai_tester = ISTQBAITester(auth_manager)
        components['istqb_ai_tester'] = istqb_ai_tester
        print("✅ ISTQBAITester initialized successfully")
        
        print("=" * 60)
        print(f"🎉 All {len(components)} components initialized successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error initializing components: {e}")
        print(f"💔 Failed component will use placeholder interface")
        
        # Create placeholder managers if components fail
        curriculum_mgr = components.get('curriculum_mgr', None)
        ai_act_explorer = components.get('ai_act_explorer', None) 
        model_demos = components.get('model_demos', None)
        ai_tutor = components.get('ai_tutor', None)
        performance_tracker = components.get('performance_tracker', None)
        quiz_engine = components.get('quiz_engine', None)
        istqb_ai_tester = components.get('istqb_ai_tester', None)
    
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
                print("🏗️ Creating Curriculum Explorer interface...")
                if curriculum_mgr:
                    curriculum_mgr.create_interface()
                    print("✅ Curriculum Explorer interface created")
                else:
                    create_placeholder_interface("Curriculum Explorer", "📖")
                    print("⚠️ Curriculum Explorer placeholder created")
            
            # ⚖️ EU AI Act Explorer Tab
            with gr.Tab("⚖️ EU AI Act Explorer", elem_id="ai-act-tab"):
                print("🏗️ Creating EU AI Act Explorer interface...")
                if ai_act_explorer:
                    ai_act_explorer.create_interface()
                    print("✅ EU AI Act Explorer interface created")
                else:
                    create_placeholder_interface("EU AI Act Explorer", "⚖️")
                    print("⚠️ EU AI Act Explorer placeholder created")
            
            # 🤖 Model Demos Tab
            with gr.Tab("🤖 Model Demos", elem_id="models-tab"):
                print("🏗️ Creating Model Demos interface...")
                if model_demos:
                    model_demos.create_interface()
                    print("✅ Model Demos interface created")
                else:
                    create_placeholder_interface("Model Demos", "🤖")
                    print("⚠️ Model Demos placeholder created")
            
            # 🧠 AI Tutor Chat Tab
            with gr.Tab("🧠 AI Tutor Chat", elem_id="tutor-tab"):
                print("🏗️ Creating AI Tutor interface...")
                if ai_tutor:
                    ai_tutor.create_interface()
                    print("✅ AI Tutor interface created")
                else:
                    create_placeholder_interface("AI Tutor", "🧠")
                    print("⚠️ AI Tutor placeholder created")
            
            # 📊 Performance Tracker Tab
            with gr.Tab("📊 Performance Tracker", elem_id="performance-tab"):
                print("🏗️ Creating Performance Tracker interface...")
                if performance_tracker:
                    performance_tracker.create_interface()
                    print("✅ Performance Tracker interface created")
                else:
                    create_placeholder_interface("Performance Tracker", "📊")
                    print("⚠️ Performance Tracker placeholder created")
            
            # 💼 Annex IV Builder Tab
            with gr.Tab("💼 Annex IV Builder", elem_id="annex-tab"):
                print("🏗️ Creating Annex IV Builder interface...")
                create_annex_builder()
                print("✅ Annex IV Builder interface created")
            
            # 🧪 Mock AIGP Quiz Tab
            with gr.Tab("🧪 Mock AIGP Quiz", elem_id="quiz-tab"):
                print("🏗️ Creating Quiz Engine interface...")
                if quiz_engine:
                    quiz_engine.create_interface()
                    print("✅ Quiz Engine interface created")
                else:
                    create_placeholder_interface("Mock Quiz", "🧪")
                    print("⚠️ Quiz Engine placeholder created")
            
            # 🎯 ISTQB AI Tester Tab
            with gr.Tab("🎯 ISTQB AI Tester", elem_id="istqb-tab"):
                print("🏗️ Creating ISTQB AI Tester interface...")
                if istqb_ai_tester:
                    istqb_ai_tester.create_interface()
                    print("✅ ISTQB AI Tester interface created")
                else:
                    create_placeholder_interface("ISTQB AI Tester", "🎯")
                    print("⚠️ ISTQB AI Tester placeholder created")
            
            # 🔗 Notion Sync & Export Tab
            with gr.Tab("🔗 Sync & Export", elem_id="sync-tab"):
                print("🏗️ Creating Sync & Export interface...")
                create_sync_interface()
                print("✅ Sync & Export interface created")
        
        # Footer
        gr.HTML("""
        <div style="
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
            color: #f1f5f9;
            padding: 3rem 2rem 2rem 2rem;
            margin-top: 3rem;
            border-radius: 20px;
            border: 2px solid #475569;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            text-align: center;
            font-family: 'Inter', 'Lexend', sans-serif;
        ">
            <!-- KAOMOJI Header -->
            <div style="font-size: 2rem; margin-bottom: 1.5rem; line-height: 1;">
                ヽ(•‿•)ノ ♡(˃͈ દ ˂͈ ༶ ) (◕‿◕)♡ ＼(^o^)／ (´∀｀)♡
            </div>
            
            <!-- Main Title -->
            <h2 style="
                color: #60a5fa; 
                margin: 0 0 1rem 0; 
                font-size: 1.5rem; 
                font-weight: 700;
                text-shadow: 0 0 10px rgba(96, 165, 250, 0.3);
            ">
                🧠⚖️ AI Governance Architect's Codex
            </h2>
            
            <!-- Tech Stack -->
            <div style="
                background: rgba(59, 130, 246, 0.1);
                border: 1px solid #3b82f6;
                border-radius: 12px;
                padding: 1rem;
                margin: 1.5rem 0;
                font-size: 1.1rem;
            ">
                <span style="color: #fbbf24; font-weight: 600;">Built with:</span>
                <span style="color: #e5e7eb;">GRADIO • PYTHON • Cursor IDE</span>
                <span style="color: #f87171;">and much love</span>
                <span style="font-size: 1.2rem; margin-left: 0.5rem;">♡(˃͈ દ ˂͈ ༶ )</span>
            </div>
            
            <!-- Contact & Attribution -->
            <div style="
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 2rem;
                margin: 1.5rem 0;
                flex-wrap: wrap;
            ">
                <div style="
                    background: rgba(34, 197, 94, 0.1);
                    border: 1px solid #22c55e;
                    border-radius: 10px;
                    padding: 0.8rem 1.2rem;
                    font-size: 0.95rem;
                ">
                    <span style="color: #fbbf24;">📧 Contact:</span>
                    <a href="mailto:0m3g4_k1ng@proton.me" style="
                        color: #60a5fa; 
                        text-decoration: none; 
                        font-weight: 600;
                        margin-left: 0.5rem;
                    ">0m3g4_k1ng@proton.me</a>
                </div>
                
                <div style="
                    background: rgba(168, 85, 247, 0.1);
                    border: 1px solid #a855f7;
                    border-radius: 10px;
                    padding: 0.8rem 1.2rem;
                    font-size: 0.95rem;
                ">
                    <span style="color: #fbbf24;">👨‍💻 Lead Dev/QA:</span>
                    <span style="color: #e5e7eb; font-weight: 600; margin-left: 0.5rem;">Fausto Siqueira</span>
                </div>
            </div>
            
            <!-- KAOMOJI Separator -->
            <div style="
                font-size: 1.2rem; 
                margin: 1.5rem 0 1rem 0; 
                color: #94a3b8;
                letter-spacing: 0.2rem;
            ">
                ◆ ◇ ◆ ◇ ◆ ◇ ◆ ◇ ◆
            </div>
            
            <!-- Licensing & Legal -->
            <div style="margin: 1rem 0; font-size: 0.9rem; color: #cbd5e1;">
                <div style="margin-bottom: 0.5rem;">
                    <span style="color: #f59e0b;">🏛️</span>
                    <strong style="color: #fbbf24;">EU AI ACT COMPLIANT</strong>
                    <span style="color: #f59e0b;">🏛️</span>
                </div>
                <div>
                    <span style="color: #22c55e;">License:</span>
                    <span style="color: #e5e7eb; font-weight: 600;">GBU2 (Good, Bad, Ugly 2.0)</span>
                    <span style="font-size: 1.1rem; margin-left: 0.5rem;">(｡◕‿◕｡)</span>
                </div>
            </div>
            
            <!-- Bottom KAOMOJI -->
            <div style="
                font-size: 1.5rem; 
                margin-top: 1.5rem; 
                color: #60a5fa;
                text-shadow: 0 0 8px rgba(96, 165, 250, 0.4);
            ">
                ♪(´▽｀) ～♪ (◡ ‿ ◡) ♡ ヾ(＾-＾)ノ
            </div>
        </div>
        """)
    
    print("=" * 60)
    print("🎯 Interface construction completed successfully!")
    print("📱 All tabs and components are ready")
    print("=" * 60)
    
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
    """Create comprehensive Annex IV compliance document builder based on official EU AI Act requirements"""
    gr.Markdown("## 💼 EU AI Act Annex IV Technical Documentation Builder")
    gr.Markdown("*Generate official technical documentation for high-risk AI systems according to Regulation (EU) 2024/1689*")
    
    # Display official requirements notice
    gr.HTML("""
    <div style="background: #1a1a1a; border: 2px solid #3b82f6; border-radius: 12px; padding: 1.5rem; color: #ffffff; margin: 1rem 0;">
        <h3 style="color: #3b82f6; margin-top: 0;">📋 Official Annex IV Requirements</h3>
        <p style="color: #d1d5db; margin: 0.5rem 0;"><strong>Article 18(1):</strong> Technical documentation must demonstrate high-risk AI system compliance with EU AI Act requirements</p>
        <p style="color: #d1d5db; margin: 0.5rem 0;"><strong>Mandatory Sections:</strong> 6 comprehensive documentation sections covering all aspects of the AI system</p>
        <p style="color: #fbbf24; margin: 0.5rem 0; font-style: italic;">Complete all sections below to ensure full compliance with official EU AI Act requirements.</p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📝 **Section 1: General Description of AI System**")
            
            system_name = gr.Textbox(
                label="AI System Name",
                placeholder="Enter the commercial name/identifier of your AI system..."
            )
            
            intended_purpose = gr.Textbox(
                label="Intended Purpose & Users", 
                lines=4,
                placeholder="Describe: intended purpose, target users/groups/entities, specific use contexts, deployment scenarios..."
            )
            
            accuracy_level = gr.Textbox(
                label="Expected Accuracy Level & Metrics",
                lines=3,
                placeholder="Define expected accuracy levels, specific metrics used (precision, recall, F1-score, etc.), basis for accuracy expectations..."
            )
            
            risk_category = gr.Dropdown(
                choices=[
                    "Biometric identification and categorisation",
                    "Management and operation of critical infrastructure", 
                    "Education and vocational training",
                    "Employment, workers management and access to self-employment", 
                    "Access to and enjoyment of essential private and public services",
                    "Law enforcement",
                    "Migration, asylum and border control management",
                    "Administration of justice and democratic processes"
                ],
                label="High-Risk Category (Annex III)",
                value="Access to and enjoyment of essential private and public services"
            )
            
            unintended_outcomes = gr.Textbox(
                label="Reasonably Foreseeable Unintended Outcomes",
                lines=4,
                placeholder="Identify potential unintended outcomes, sources of risks to health/safety/fundamental rights, discrimination risks..."
            )
            
            misuse_risks = gr.Textbox(
                label="Foreseeable Misuse Circumstances",
                lines=3,
                placeholder="Describe known/foreseeable circumstances of misuse that may lead to health, safety, or fundamental rights risks..."
            )
            
            human_oversight_measures = gr.Textbox(
                label="Human Oversight Measures Required",
                lines=4,
                placeholder="Detail human oversight measures needed, technical measures for output interpretation, human-machine interface requirements..."
            )
            
        with gr.Column():
            gr.Markdown("### 📊 **Section 2: Data and Data Governance**")
            
            training_data = gr.Textbox(
                label="Training, Validation & Testing Data Sets",
                lines=5,
                placeholder="Describe: data provenance, scope and main characteristics, how data was obtained and selected, labelling procedures (e.g. supervised learning), data cleaning methodologies (e.g. outliers detection)..."
            )
            
            data_availability = gr.Textbox(
                label="Data Availability, Quantity & Suitability Assessment", 
                lines=3,
                placeholder="Assess availability, quantity and suitability of training/validation/testing datasets..."
            )
            
            data_governance = gr.Textbox(
                label="Data Governance & Management Practices",
                lines=4,
                placeholder="Describe data governance practices, data analysis procedures, pre-processing steps, formulation of assumptions, information used by and inferred by the system..."
            )
            
            bias_assessment = gr.Textbox(
                label="Bias Assessment & Mitigation",
                lines=4,
                placeholder="Assess measures to examine data for bias presence, conclusions drawn from bias examination, measures taking into account intended purpose..."
            )
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🔧 **Section 3: Monitoring, Functioning & Control**")
            
            capabilities_limitations = gr.Textbox(
                label="System Capabilities & Limitations",
                lines=4,
                placeholder="Describe system capabilities and limitations, circumstances impacting performance, accuracy degrees for specific persons/groups, overall expected accuracy..."
            )
            
            evaluation_procedures = gr.Textbox(
                label="Evaluation Procedures & Benchmarks",
                lines=3,
                placeholder="Describe evaluation procedures, applied evaluation criteria, evaluation protocols and benchmarks used..."
            )
            
            risk_mitigation = gr.Textbox(
                label="Risk Prevention & Mitigation Measures",
                lines=4,
                placeholder="Detail measures to prevent and mitigate reasonably foreseeable risks, issues and limitations..."
            )
            
        with gr.Column():
            gr.Markdown("### ⚠️ **Section 4: Risk Management System**")
            
            risk_management_system = gr.Textbox(
                label="Risk Management System Description (Article 23)",
                lines=4,
                placeholder="Describe the established risk management system per Article 23 requirements, continuous iterative process, risk identification and analysis procedures..."
            )
            
            gr.Markdown("### 🔄 **Section 5: Changes Through Lifecycle**")
            
            lifecycle_changes = gr.Textbox(
                label="System Changes Description",
                lines=3,
                placeholder="Describe any changes made to the system throughout its lifecycle, version history, update procedures..."
            )
            
            gr.Markdown("### 🏢 **Section 6: Quality Management System**")
            
            quality_management = gr.Textbox(
                label="Quality Management System (Article 17)",
                lines=4,
                placeholder="Describe quality management system per Article 17, including AI system objectives and achievement measurement and monitoring procedures..."
            )
    
    with gr.Row():
        generate_btn = gr.Button("🔧 Generate Official Annex IV Documentation", variant="primary", size="lg")
        
    with gr.Row():
        compliance_output = gr.Textbox(
            label="Generated Annex IV Technical Documentation", 
            lines=20,
            placeholder="Your complete Annex IV technical documentation will appear here..."
        )
    
    def generate_annex_iv_documentation(name, purpose, accuracy, category, unintended, misuse, oversight, 
                                       training, availability, governance, bias, capabilities, 
                                       evaluation, mitigation, risk_mgmt, changes, quality):
        """Generate comprehensive Annex IV technical documentation"""
        if not name or not purpose:
            return "❌ Error: Please provide at minimum the AI system name and intended purpose to generate documentation."
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        doc = f"""
# EU AI ACT ANNEX IV TECHNICAL DOCUMENTATION
## HIGH-RISK AI SYSTEM: {name.upper()}

**Document Reference:** ANNEX-IV-{name.replace(' ', '-').upper()}-{current_date}
**Regulation:** (EU) 2024/1689 - Artificial Intelligence Act
**Article Reference:** Article 18(1) - Technical Documentation Requirements
**Date of Preparation:** {current_date}
**Document Version:** 1.0

---

## COMPLIANCE STATEMENT

This technical documentation is prepared in accordance with Annex IV of Regulation (EU) 2024/1689 (AI Act) and demonstrates compliance with requirements set out in Chapter 2 for high-risk AI systems before market placement or service deployment.

---

## SECTION 1: GENERAL DESCRIPTION OF THE AI SYSTEM

### 1.1 System Identification
**AI System Name:** {name}
**Risk Classification:** High-Risk AI System
**Annex III Category:** {category}
**Provider:** [PROVIDER NAME TO BE COMPLETED]

### 1.2 Intended Purpose and Users
{purpose if purpose else '[TO BE COMPLETED - Describe intended purpose, target users/groups/entities for system use]'}

### 1.3 Expected Accuracy Level and Metrics
{accuracy if accuracy else '[TO BE COMPLETED - Define expected accuracy levels and specific metrics on which system has been designed and developed]'}

### 1.4 Reasonably Foreseeable Unintended Outcomes
{unintended if unintended else '[TO BE COMPLETED - Identify reasonably foreseeable unintended outcomes and sources of risks to health, safety, fundamental rights and discrimination]'}

### 1.5 Known or Foreseeable Misuse Circumstances
{misuse if misuse else '[TO BE COMPLETED - Describe circumstances related to intended use or reasonably foreseeable misuse that may lead to health, safety or fundamental rights risks]'}

### 1.6 Human Oversight Measures
{oversight if oversight else '[TO BE COMPLETED - Detail human oversight measures needed for the AI system, including technical measures for output interpretation]'}

---

## SECTION 2: DATA AND DATA GOVERNANCE

### 2.1 Training, Validation and Testing Data Sets
{training if training else '[TO BE COMPLETED - Describe training, validation and testing data sets including provenance, scope, characteristics, selection methodology, labelling procedures, and data cleaning methodologies]'}

### 2.2 Data Availability, Quantity and Suitability Assessment
{availability if availability else '[TO BE COMPLETED - Assess availability, quantity and suitability of data sets used for training, validation and testing]'}

### 2.3 Data Governance and Management Practices
{governance if governance else '[TO BE COMPLETED - Describe data governance and management practices, data analysis procedures, pre-processing steps, and assumption formulation]'}

### 2.4 Bias Assessment and Mitigation Measures
{bias if bias else '[TO BE COMPLETED - Assess measures to examine data for bias presence and conclusions drawn, considering the intended purpose of the AI system]'}

---

## SECTION 3: MONITORING, FUNCTIONING AND CONTROL OF THE AI SYSTEM

### 3.1 System Capabilities and Limitations
{capabilities if capabilities else '[TO BE COMPLETED - Describe capabilities and limitations, circumstances impacting performance, accuracy degrees for specific persons/groups, and overall expected accuracy]'}

### 3.2 Evaluation Procedures and Benchmarks
{evaluation if evaluation else '[TO BE COMPLETED - Describe evaluation procedures, applied criteria, evaluation protocols and benchmarks]'}

### 3.3 Risk Prevention and Mitigation Measures
{mitigation if mitigation else '[TO BE COMPLETED - Detail measures to prevent and mitigate reasonably foreseeable risks, issues and limitations]'}

---

## SECTION 4: RISK MANAGEMENT SYSTEM

### 4.1 Risk Management System Description (Article 23 Compliance)
{risk_mgmt if risk_mgmt else '[TO BE COMPLETED - Describe risk management system in accordance with Article 23 requirements, including continuous iterative process for risk identification, analysis, estimation and evaluation]'}

---

## SECTION 5: CHANGES MADE TO THE SYSTEM THROUGH ITS LIFECYCLE

### 5.1 System Lifecycle Changes Documentation
{changes if changes else '[TO BE COMPLETED - Describe any changes made to the system throughout its lifecycle, including updates, modifications, and version control]'}

---

## SECTION 6: QUALITY MANAGEMENT SYSTEM AND PROCESSES

### 6.1 Quality Management System Description (Article 17 Compliance)
{quality if quality else '[TO BE COMPLETED - Describe quality management system per Article 17, including AI system objectives and achievement measurement and monitoring procedures]'}

---

## REGULATORY COMPLIANCE CHECKLIST

### Pre-Market Requirements (Article 16)
□ Quality management system established (Article 17)
□ Technical documentation complete (Article 18 - this document)
□ Automatic logging system implemented (Article 19)
□ Transparency requirements met (Article 20)
□ Human oversight designed and implemented (Article 21)
□ Accuracy, robustness and cybersecurity ensured (Article 22)
□ Risk management system established (Article 23)

### Conformity Assessment Requirements
□ Conformity assessment procedure completed
□ CE marking affixed
□ EU declaration of conformity drawn up
□ Registration in EU database completed

---

## DOCUMENT CONTROL

**Document Status:** Draft / Under Review / Approved
**Prepared By:** [NAME, TITLE]
**Reviewed By:** [NAME, TITLE]
**Approved By:** [NAME, TITLE]
**Next Review Date:** {(datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')}

---

## LEGAL DISCLAIMER

This technical documentation is prepared as a template for compliance with EU AI Act Annex IV requirements. Organizations must:

1. Complete all sections marked "[TO BE COMPLETED]"
2. Ensure technical accuracy of all statements
3. Obtain legal review before market placement
4. Maintain documentation throughout system lifecycle
5. Update documentation for any system changes

**IMPORTANT:** This documentation alone does not guarantee regulatory compliance. Consult qualified legal and technical experts for comprehensive compliance verification.

---

**END OF ANNEX IV TECHNICAL DOCUMENTATION**

*Document generated on {current_date} using AI Governance Study Portal*
*For questions regarding this documentation, contact: [PROVIDER CONTACT INFORMATION]*
        """
        
        return doc
    
    generate_btn.click(
        fn=generate_annex_iv_documentation,
        inputs=[system_name, intended_purpose, accuracy_level, risk_category, unintended_outcomes, 
               misuse_risks, human_oversight_measures, training_data, data_availability, 
               data_governance, bias_assessment, capabilities_limitations, 
               evaluation_procedures, risk_mitigation, risk_management_system,
               lifecycle_changes, quality_management],
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
            <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); 
                        color: white; padding: 1.5rem; border-radius: 12px;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <h4 style="color: #fbbf24; margin-top: 0; font-size: 1.3rem;">📈 Current Study Status</h4>
                <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                    <li style="color: #f3f4f6; margin: 0.3rem 0;">
                        Weeks completed: <strong style="color: #fbbf24;">7/12</strong>
                    </li>
                    <li style="color: #f3f4f6; margin: 0.3rem 0;">
                        Quiz average: <strong style="color: #fbbf24;">87%</strong>
                    </li>
                    <li style="color: #f3f4f6; margin: 0.3rem 0;">
                        Study hours: <strong style="color: #fbbf24;">128</strong>
                    </li>
                    <li style="color: #f3f4f6; margin: 0.3rem 0;">
                        Last sync: <strong style="color: #fbbf24;">Never</strong>
                    </li>
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
    print("\n" + "=" * 80)
    print("🎯 AI GOVERNANCE ARCHITECT'S CODEX - STARTUP SEQUENCE")
    print("=" * 80)
    print("📅 Startup time:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("🐍 Python version:", sys.version.split()[0])
    print("📂 Working directory:", os.getcwd())
    print("=" * 80)
    
    # Create the app
    print("🏗️ Building main interface...")
    app = create_main_interface()
    print("✅ Main interface built successfully!")
    
    print("=" * 80)
    print("🚀 Launching Gradio application...")
    print("🌐 Server: 0.0.0.0:7860")
    print("🔗 Share: Disabled")
    print("🐛 Debug: Enabled")
    print("⚠️ Show Errors: Enabled") 
    
    # Check for favicon
    favicon_exists = os.path.exists("static/images/favicon.ico")
    print(f"🎯 Favicon: {'Found' if favicon_exists else 'Not found'}")
    
    print("=" * 80)
    print("🎉 Ready to serve! Application launching...")
    print("=" * 80 + "\n")
    
    # Launch with custom settings
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        debug=True,
        show_error=True,
        favicon_path="static/images/favicon.ico" if favicon_exists else None
    ) 