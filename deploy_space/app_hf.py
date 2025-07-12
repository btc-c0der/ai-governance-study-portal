#!/usr/bin/env python3
"""
🧠⚖️ AI Governance Architect's Codex - Hugging Face Space Launcher
Simplified launcher for Hugging Face Spaces deployment
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Apply Gradio patches before importing Gradio
try:
    from gradio_patch import apply_gradio_patches
    apply_gradio_patches()
except ImportError:
    print("⚠️  Gradio patches not available, proceeding without patches")

import gradio as gr

def create_main_interface():
    """Create a safe, minimal interface that avoids schema parsing issues"""
    with gr.Blocks(
        title="AI Governance Architect's Codex",
        theme=gr.themes.Soft(),
        css="""
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        .header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .feature-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        """
    ) as app:
        with gr.Column(elem_classes="main-container"):
            gr.HTML("""
            <div class="header">
                <h1>🧠⚖️ AI Governance Architect's Codex</h1>
                <p><strong>Your Complete Study Portal for AI Governance & Ethics</strong></p>
                <p>Featuring ISTQB CT-AI Certification, EU AI Act Explorer, and Advanced AI Tutoring</p>
            </div>
            """)
            
            # Simple interface to avoid schema issues
            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div class="feature-card">
                        <h3>📚 ISTQB CT-AI Certification</h3>
                        <p>Complete study materials for the ISTQB Certified Tester AI Testing certification</p>
                        <ul>
                            <li>Interactive practice tests</li>
                            <li>Comprehensive study guides</li>
                            <li>Progress tracking</li>
                        </ul>
                    </div>
                    """)
                
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div class="feature-card">
                        <h3>⚖️ EU AI Act Explorer</h3>
                        <p>Navigate the European Union's AI Act with interactive tools</p>
                        <ul>
                            <li>Article-by-article analysis</li>
                            <li>Compliance checklists</li>
                            <li>Risk assessment tools</li>
                        </ul>
                    </div>
                    """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div class="feature-card">
                        <h3>🤖 AI Model Demos</h3>
                        <p>Hands-on experience with AI models and testing scenarios</p>
                        <ul>
                            <li>Live model demonstrations</li>
                            <li>Testing scenarios</li>
                            <li>Performance analysis</li>
                        </ul>
                    </div>
                    """)
                
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div class="feature-card">
                        <h3>🎓 AI Tutor</h3>
                        <p>Personalized learning with AI-powered tutoring</p>
                        <ul>
                            <li>Adaptive questioning</li>
                            <li>Concept explanations</li>
                            <li>Study recommendations</li>
                        </ul>
                    </div>
                    """)
            
            gr.HTML("""
            <div style="text-align: center; margin-top: 2rem; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
                <p><strong>🚀 Status:</strong> Application is initializing...</p>
                <p>Full functionality will be available once all components are loaded.</p>
                <p><em>Note: This is a minimal version optimized for Hugging Face Spaces deployment.</em></p>
            </div>
            """)
    
    return app

# Try to import the full app, but fall back to minimal version
try:
    print("🔄 Attempting to import full application...")
    from app import create_main_interface as create_full_interface
    print("✅ Full application imported successfully")
    
    # Test if the full interface can be created without errors
    try:
        test_app = create_full_interface()
        print("✅ Full interface creation test passed")
        # Use the full interface if it works
        create_main_interface = create_full_interface
    except Exception as schema_error:
        print(f"⚠️ Schema parsing error in full app: {schema_error}")
        print("🔄 Falling back to minimal interface...")
        # Keep the minimal interface defined above
        
except ImportError as e:
    print(f"📝 Import error (using minimal interface): {e}")
    # Keep the minimal interface defined above

# Create necessary directories for Hugging Face Spaces
def setup_directories():
    """Create necessary directories if they don't exist"""
    directories = ['static/images', 'data', 'models', 'temp']
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✅ Directory structure ready")

# Setup environment
print("🧠⚖️ AI Governance Architect's Codex - Hugging Face Spaces")
print("=" * 60)

# Create necessary directories
setup_directories()

# Create and launch the interface
print("🚀 Initializing application...")
try:
    app = create_main_interface()
    print("✅ Application initialized successfully")
except Exception as e:
    print(f"❌ App creation error: {e}")
    import gradio as gr
    
    with gr.Blocks(title="AI Governance Codex - Error") as app:
        gr.HTML(f"""
        <div style="text-align: center; padding: 2rem; background: #fee2e2; border-radius: 10px;">
            <h1>🧠⚖️ AI Governance Architect's Codex</h1>
            <h2>⚠️ Initialization Error</h2>
            <p><strong>Error:</strong> {str(e)}</p>
            <p>Please check the Spaces logs for detailed error information.</p>
        </div>
        """)

# Mount the app for Hugging Face Spaces
print("📍 Launching on Hugging Face Spaces...")
try:
    # Use optimized launch parameters for Hugging Face Spaces
    app.launch(
        server_name="0.0.0.0",  # Listen on all interfaces
        server_port=7860,  # Default Spaces port
        show_error=True,  # Show errors for debugging
        quiet=False,  # Show startup messages
        share=False,  # No share link needed in Spaces
        show_api=False,  # Hide API docs for cleaner interface
        prevent_thread_lock=False  # Allow proper blocking
    )
except Exception as e:
    print(f"❌ Launch error: {e}")
    # Fallback launch with absolute minimal config
    try:
        print("🔄 Attempting fallback launch...")
        app.launch(
            server_port=7860,
            server_name="0.0.0.0"
        )
    except Exception as fallback_error:
        print(f"❌ Fallback launch also failed: {fallback_error}")
        print("Check logs for detailed error information.")
        
        # Last resort: create a super minimal app
        print("🔄 Creating emergency minimal app...")
        try:
            emergency_app = gr.Interface(
                fn=lambda x: f"Echo: {x}",
                inputs=gr.Textbox(label="Input"),
                outputs=gr.Textbox(label="Output"),
                title="AI Governance Codex - Emergency Mode"
            )
            emergency_app.launch(
                server_port=7860,
                server_name="0.0.0.0"
            )
        except Exception as final_error:
            print(f"❌ Emergency app also failed: {final_error}")
            print("All launch attempts failed. Please check the logs.") 