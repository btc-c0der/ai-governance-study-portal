#!/usr/bin/env python3
"""
🧠⚖️ AI Governance Architect's Codex - Simplified Version
Minimal layout to test Hugging Face Spaces compatibility
"""

import gradio as gr
from datetime import datetime, timedelta
from pathlib import Path

# Import our custom modules with fallbacks
try:
    from components.curriculum import CurriculumManager
    from components.ai_act_explorer import AIActExplorer
    from components.model_demos import ModelDemos
    from components.ai_tutor import AITutor
    from components.performance_tracker import PerformanceTracker
    from components.quiz_engine import QuizEngine
    from components.auth_manager import AuthManager
    from components.istqb_ai_tester import ISTQBAITester
    COMPONENTS_LOADED = True
except ImportError as e:
    print(f"Warning: Could not import some components: {e}")
    COMPONENTS_LOADED = False

def create_simple_interface():
    """Create a simplified Gradio interface for testing"""
    
    print("🚀 Starting AI Governance Architect's Codex (Simplified)...")
    
    # Initialize components if available
    components = {}
    
    if COMPONENTS_LOADED:
        try:
            auth_manager = AuthManager()
            performance_tracker = PerformanceTracker(auth_manager)
            curriculum_mgr = CurriculumManager(auth_manager, performance_tracker)
            quiz_engine = QuizEngine(auth_manager)
            istqb_ai_tester = ISTQBAITester(auth_manager)
            ai_act_explorer = AIActExplorer()
            model_demos = ModelDemos()
            ai_tutor = AITutor()
            
            components = {
                'auth_manager': auth_manager,
                'performance_tracker': performance_tracker,
                'curriculum_mgr': curriculum_mgr,
                'quiz_engine': quiz_engine,
                'istqb_ai_tester': istqb_ai_tester,
                'ai_act_explorer': ai_act_explorer,
                'model_demos': model_demos,
                'ai_tutor': ai_tutor
            }
            print(f"✅ All {len(components)} components initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing components: {e}")
            components = {}
    
    # Create simplified interface
    with gr.Blocks(
        title="🧠⚖️ AI Governance Architect's Codex",
        theme=gr.themes.Soft()
    ) as app:
        
        # Simple header
        gr.HTML("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; margin-bottom: 2rem;">
            <h1>🧠⚖️ AI Governance Architect's Codex</h1>
            <p>Next-Gen AI/ML Study Portal • EU AI Act • AIGP Certification • Model Demos</p>
        </div>
        """)
        
        # Simple tabs
        with gr.Tabs():
            
            # Curriculum Explorer Tab
            with gr.Tab("📖 Curriculum Explorer"):
                if components.get('curriculum_mgr'):
                    try:
                        components['curriculum_mgr'].create_interface()
                    except Exception as e:
                        gr.Markdown(f"## 📖 Curriculum Explorer\n**Loading Error:** {e}")
                else:
                    gr.Markdown("## 📖 Curriculum Explorer\n*Component not available*")
            
            # EU AI Act Explorer Tab
            with gr.Tab("⚖️ EU AI Act Explorer"):
                if components.get('ai_act_explorer'):
                    try:
                        components['ai_act_explorer'].create_interface()
                    except Exception as e:
                        gr.Markdown(f"## ⚖️ EU AI Act Explorer\n**Loading Error:** {e}")
                else:
                    gr.Markdown("## ⚖️ EU AI Act Explorer\n*Component not available*")
            
            # Model Demos Tab
            with gr.Tab("🤖 Model Demos"):
                if components.get('model_demos'):
                    try:
                        components['model_demos'].create_interface()
                    except Exception as e:
                        gr.Markdown(f"## 🤖 Model Demos\n**Loading Error:** {e}")
                else:
                    gr.Markdown("## 🤖 Model Demos\n*Component not available*")
            
            # Quiz Tab
            with gr.Tab("🧪 Mock Quiz"):
                if components.get('quiz_engine'):
                    try:
                        components['quiz_engine'].create_interface()
                    except Exception as e:
                        gr.Markdown(f"## 🧪 Mock Quiz\n**Loading Error:** {e}")
                else:
                    gr.Markdown("## 🧪 Mock Quiz\n*Component not available*")
            
            # Authentication Tab
            with gr.Tab("🔐 Authentication"):
                if components.get('auth_manager'):
                    try:
                        components['auth_manager'].create_auth_interface()
                    except Exception as e:
                        gr.Markdown(f"## 🔐 Authentication\n**Loading Error:** {e}")
                else:
                    gr.Markdown("## 🔐 Authentication\n*Component not available*")
        
        # Simple footer
        gr.HTML("""
        <div style="text-align: center; padding: 1rem; margin-top: 2rem; color: #666;">
            <p>🧠⚖️ AI Governance Architect's Codex - Simplified Version</p>
        </div>
        """)
    
    print("✅ Simplified interface created successfully!")
    return app

if __name__ == "__main__":
    app = create_simple_interface()
    app.launch()
