#!/usr/bin/env python3
"""
🧪 Gradio Deployment Test Script
Verifies app functionality before deployment to Hugging Face Spaces
"""

import gradio as gr
import requests
import time
import sys
import os
import logging
from pathlib import Path
import json
from typing import Dict, Any, List, Tuple
import threading
from contextlib import contextmanager
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('deployment_test.log')
    ]
)

logger = logging.getLogger(__name__)

class GradioDeploymentTester:
    def __init__(self, port: int = 7860):
        self.port = port
        self.base_url = f"http://127.0.0.1:{port}"
        self.app = None
        self.server_thread = None
        
    def start_server(self) -> bool:
        """Start the Gradio server in a separate thread"""
        try:
            from app import create_main_interface
            self.app = create_main_interface()
            
            def run_server():
                self.app.launch(
                    server_name="127.0.0.1",
                    server_port=self.port,
                    share=False,
                    debug=False,
                    show_error=True,
                    prevent_thread_lock=True
                )
            
            self.server_thread = threading.Thread(target=run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            # Wait for server to start
            time.sleep(5)
            return True
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    def test_server_health(self) -> bool:
        """Test if server is responding"""
        try:
            response = requests.get(f"{self.base_url}/")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Server health check failed: {e}")
            return False
    
    def test_component_loading(self) -> List[Tuple[str, bool]]:
        """Test if all components load properly"""
        components = [
            ("CurriculumManager", "components.curriculum"),
            ("AIActExplorer", "components.ai_act_explorer"),
            ("ModelDemos", "components.model_demos"),
            ("AITutor", "components.ai_tutor"),
            ("PerformanceTracker", "components.performance_tracker"),
            ("QuizEngine", "components.quiz_engine"),
            ("AuthManager", "components.auth_manager")
        ]
        
        results = []
        for component_name, module_path in components:
            try:
                # Import dynamically
                module = __import__(module_path, fromlist=[component_name])
                component_class = getattr(module, component_name)
                
                # Special handling for components that need AuthManager
                if component_name in ["CurriculumManager", "QuizEngine"]:
                    from components.auth_manager import AuthManager
                    auth_manager = AuthManager()
                    instance = component_class(auth_manager)
                else:
                    instance = component_class()
                    
                results.append((component_name, True))
                logger.info(f"✅ {component_name} loaded successfully")
            except Exception as e:
                logger.error(f"❌ {component_name} loading failed: {e}")
                results.append((component_name, False))
        
        return results
    
    def test_file_dependencies(self) -> List[Tuple[str, bool]]:
        """Test if all required files exist"""
        required_files = [
            "app.py",
            "requirements.txt",
            "components/ai_act_articles.json",
            "components/curriculum.json",
            "static/images/favicon.ico"
        ]
        
        results = []
        for file_path in required_files:
            exists = os.path.exists(file_path)
            results.append((file_path, exists))
            if not exists:
                logger.warning(f"Required file missing: {file_path}")
            else:
                logger.info(f"✅ Found required file: {file_path}")
        
        return results
    
    def test_gradio_config(self) -> Dict[str, bool]:
        """Test Gradio configuration"""
        config_tests = {
            "no_share": True,  # share=False is required for HF Spaces
            "valid_port": self.port == 7860,  # HF Spaces requires port 7860
            "valid_host": True,  # Will be handled by HF Spaces
            "debug_disabled": True  # debug should be False in production
        }
        
        # Check app.py and launch.py for configurations
        try:
            with open("app.py", "r") as f:
                app_content = f.read()
                if "share=True" in app_content:
                    config_tests["no_share"] = False
                if "debug=True" in app_content:
                    config_tests["debug_disabled"] = False
        except Exception as e:
            logger.error(f"Failed to check app.py configuration: {e}")
        
        return config_tests
    
    def run_all_tests(self) -> bool:
        """Run all deployment tests"""
        logger.info("🧪 Starting deployment tests...")
        
        all_passed = True
        results = {
            "server": False,
            "health": False,
            "components": [],
            "files": [],
            "config": {}
        }
        
        # Start server
        logger.info("Starting Gradio server...")
        results["server"] = self.start_server()
        all_passed &= results["server"]
        
        if results["server"]:
            # Test server health
            logger.info("Testing server health...")
            results["health"] = self.test_server_health()
            all_passed &= results["health"]
            
            # Test components
            logger.info("Testing component loading...")
            results["components"] = self.test_component_loading()
            all_passed &= all(success for _, success in results["components"])
        
        # Test file dependencies
        logger.info("Testing file dependencies...")
        results["files"] = self.test_file_dependencies()
        all_passed &= all(exists for _, exists in results["files"])
        
        # Test Gradio configuration
        logger.info("Testing Gradio configuration...")
        results["config"] = self.test_gradio_config()
        all_passed &= all(results["config"].values())
        
        # Save results
        with open("deployment_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        return all_passed

def main():
    """Main entry point"""
    tester = GradioDeploymentTester()
    success = tester.run_all_tests()
    
    if success:
        logger.info("✅ All deployment tests passed!")
        sys.exit(0)
    else:
        logger.error("❌ Some deployment tests failed. Check deployment_test_results.json for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()