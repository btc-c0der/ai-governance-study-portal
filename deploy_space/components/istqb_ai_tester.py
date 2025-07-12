#!/usr/bin/env python3
"""
🎯 ISTQB Certified Tester - AI Testing Component
Advanced study portal for ISTQB Certified Tester - AI Testing (CT-AI) certification with comprehensive syllabus coverage
"""

import gradio as gr
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

class ISTQBAITester:
    """ISTQB Certified Tester - AI Testing study component with comprehensive syllabus and resources"""
    
    def __init__(self, auth_manager=None):
        """Initialize the ISTQB Certified Tester - AI Testing component"""
        self.auth_manager = auth_manager
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Load ISTQB CT-AI syllabus
        self.syllabus_data = self.load_syllabus_data()
        self.progress_data = self.load_progress_data()
        
        print("✅ ISTQB Certified Tester - AI Testing component initialized")
    
    def load_syllabus_data(self):
        """Load ISTQB TAE syllabus data from JSON file"""
        syllabus_file = self.data_dir / "istqb_tae_syllabus.json"
        
        try:
            with open(syllabus_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return self._create_fallback_syllabus()
        except json.JSONDecodeError:
            return self._create_fallback_syllabus()
    
    def _create_fallback_syllabus(self):
        """Create fallback syllabus data if file not found"""
        return {
            "syllabus_metadata": {
                "title": "ISTQB Certified Tester - AI Testing (CT-AI)",
                "version": "1.0",
                "total_hours": 16.0,
                "chapters": 5
            },
            "chapters": []
        }
    
    def load_progress_data(self):
        """Load user progress data"""
        if not self.auth_manager or not self.auth_manager.is_logged_in():
            return {}
        
        # Placeholder for progress tracking
        return {}
    
    def create_interface(self):
        """Create the ISTQB Certified Tester - AI Testing interface"""
        
        # Enhanced dark theme CSS for proper contrast
        dark_theme_css = """
        <style>
        /* Global dark theme overrides */
        .gradio-container {
            background-color: #0f1419 !important;
        }
        
        /* ISTQB specific styling */
        .istqb-container {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
            border: 1px solid #3a4a5c !important;
            border-radius: 12px !important;
            padding: 20px !important;
            margin: 10px 0 !important;
            color: #e0e0e0 !important;
        }
        
        .istqb-header {
            background: linear-gradient(90deg, #2d4a7a 0%, #1e3a8a 100%) !important;
            color: #ffffff !important;
            padding: 15px !important;
            border-radius: 8px !important;
            margin-bottom: 20px !important;
            text-align: center !important;
            font-weight: bold !important;
            font-size: 1.2em !important;
        }
        
        .istqb-chapter {
            background: #2a2a3e !important;
            border: 1px solid #4a5568 !important;
            border-radius: 8px !important;
            padding: 15px !important;
            margin: 10px 0 !important;
            color: #e0e0e0 !important;
        }
        
        .istqb-chapter h3, .istqb-chapter h4 {
            color: #60a5fa !important;
            margin-bottom: 10px !important;
        }
        
        .istqb-objective {
            background: #374151 !important;
            padding: 8px 12px !important;
            margin: 5px 0 !important;
            border-radius: 4px !important;
            border-left: 3px solid #3b82f6 !important;
            color: #d1d5db !important;
        }
        
        .istqb-topic {
            background: #4b5563 !important;
            padding: 6px 10px !important;
            margin: 3px 0 !important;
            border-radius: 4px !important;
            color: #e5e7eb !important;
            font-size: 0.9em !important;
        }
        
        .istqb-stats {
            background: #1f2937 !important;
            border: 1px solid #374151 !important;
            border-radius: 8px !important;
            padding: 15px !important;
            color: #e5e7eb !important;
        }
        
        .istqb-progress {
            background: #065f46 !important;
            height: 20px !important;
            border-radius: 10px !important;
            margin: 5px 0 !important;
        }
        
        .istqb-progress-bg {
            background: #374151 !important;
            border-radius: 10px !important;
            height: 20px !important;
            margin: 10px 0 !important;
        }
        
        .istqb-text {
            color: #e0e0e0 !important;
            line-height: 1.6 !important;
        }
        
        .istqb-text p, .istqb-text div {
            color: #e0e0e0 !important;
        }
        
        .istqb-text strong {
            color: #f3f4f6 !important;
        }
        
        .istqb-link {
            color: #60a5fa !important;
            text-decoration: none !important;
        }
        
        .istqb-link:hover {
            color: #93c5fd !important;
            text-decoration: underline !important;
        }
        
        .istqb-badge {
            background: #1e40af !important;
            color: #ffffff !important;
            padding: 4px 8px !important;
            border-radius: 12px !important;
            font-size: 0.8em !important;
            margin: 2px !important;
            display: inline-block !important;
        }
        
        .istqb-keyword-list {
            background: #374151 !important;
            padding: 10px !important;
            border-radius: 6px !important;
            color: #d1d5db !important;
            margin: 10px 0 !important;
        }
        
        /* Gradio tab styling */
        .tab-nav button {
            background: #1f2937 !important;
            color: #e5e7eb !important;
            border: 1px solid #374151 !important;
        }
        
        .tab-nav button.selected {
            background: #1e40af !important;
            color: #ffffff !important;
        }
        
        /* Override any white backgrounds */
        .gr-panel, .gr-box, .gr-form, .gr-padded {
            background: #1a1a2e !important;
            color: #e0e0e0 !important;
        }
        
        /* Button styling */
        .istqb-button {
            background: #1e40af !important;
            color: #ffffff !important;
            border: none !important;
            padding: 10px 16px !important;
            border-radius: 6px !important;
            cursor: pointer !important;
            margin: 5px !important;
        }
        
        .istqb-button:hover {
            background: #1d4ed8 !important;
        }
        </style>
        """
        
        gr.HTML(dark_theme_css)
        
        gr.HTML("""
        <div class="istqb-header">
            🎯 ISTQB Certified Tester - AI Testing Study Portal
        </div>
        """)
        
        gr.HTML("""
        <div class="istqb-container">
            <div class="istqb-text">
                <p>Master the <strong>ISTQB Advanced Level Test Automation Engineer</strong> certification with comprehensive study materials, practice exercises, and progress tracking.</p>
            </div>
        </div>
        """)
        
        with gr.Tabs():
            # Syllabus Overview Tab
            with gr.Tab("📖 Syllabus Overview"):
                self._create_syllabus_overview()
            
            # Chapter Details Tab
            with gr.Tab("📚 Chapter Details"):
                self._create_chapter_details()
            
            # Progress Tracking Tab
            with gr.Tab("📊 Progress Tracking"):
                self._create_progress_tracking()
            
            # Study Resources Tab
            with gr.Tab("🔗 Study Resources"):
                self._create_study_resources()
            
            # Practice Exercises Tab
            with gr.Tab("💻 Practice Exercises"):
                self._create_practice_exercises()
    
    def _create_syllabus_overview(self):
        """Create syllabus overview interface"""
        metadata = self.syllabus_data.get("syllabus_metadata", {})
        
        overview_html = f"""
        <div class="istqb-container">
            <div class="istqb-stats">
                <h3 style="color: #60a5fa !important; margin-bottom: 15px;">📋 Certification Overview</h3>
                <div class="istqb-text">
                    <p><strong>Title:</strong> {metadata.get('title', 'ISTQB Certified Tester - AI Testing')}</p>
                    <p><strong>Version:</strong> {metadata.get('version', '2016')}</p>
                    <p><strong>Total Study Hours:</strong> {metadata.get('total_hours', 21.5)} hours</p>
                    <p><strong>Chapters:</strong> {metadata.get('chapters', 8)} comprehensive modules</p>
                    <p><strong>Prerequisites:</strong> {metadata.get('prerequisites', 'CTFL Foundation Level')}</p>
                </div>
            </div>
        </div>
        """
        
        gr.HTML(overview_html)
        
        # Chapter summary
        chapters = self.syllabus_data.get("chapters", [])
        if chapters:
            chapter_summary = """
            <div class="istqb-container">
                <h3 style="color: #60a5fa !important;">📚 Chapter Structure</h3>
            """
            
            for chapter in chapters:
                chapter_summary += f"""
                <div class="istqb-chapter">
                    <h4 style="color: #fbbf24 !important;">Chapter {chapter.get('id', 'N/A')}: {chapter.get('title', 'Unknown')}</h4>
                    <div class="istqb-text">
                        <p><span class="istqb-badge">⏱️ {chapter.get('duration_hours', 0)} hours</span> 
                           <span class="istqb-badge">{chapter.get('k_level', 'K1-K4')}</span></p>
                        <p><strong>Focus:</strong> {', '.join(chapter.get('key_topics', [])[:3])}...</p>
                    </div>
                </div>
                """
            
            chapter_summary += "</div>"
            gr.HTML(chapter_summary)
    
    def _create_chapter_details(self):
        """Create detailed chapter interface with enhanced dark theme"""
        chapters = self.syllabus_data.get("chapters", [])
        
        if not chapters:
            gr.HTML("""
            <div class="istqb-container">
                <div class="istqb-text">
                    <p>Chapter details are being loaded. Please check back soon.</p>
                </div>
            </div>
            """)
            return
        
        for chapter in chapters:
            chapter_html = f"""
            <div class="istqb-container">
                <div class="istqb-chapter">
                    <h3>Chapter {chapter.get('id', 'N/A')}: {chapter.get('title', 'Unknown')}</h3>
                    <div class="istqb-text">
                        <p><span class="istqb-badge">⏱️ {chapter.get('duration_hours', 0)} hours</span> 
                           <span class="istqb-badge">{chapter.get('k_level', 'K1-K4')}</span></p>
                        
                        <h4 style="color: #fbbf24 !important; margin-top: 15px;">🎯 Learning Objectives:</h4>
            """
            
            for objective in chapter.get('learning_objectives', []):
                chapter_html += f'<div class="istqb-objective">{objective}</div>'
            
            chapter_html += f"""
                        <h4 style="color: #fbbf24 !important; margin-top: 15px;">📋 Key Topics:</h4>
            """
            
            for topic in chapter.get('key_topics', []):
                chapter_html += f'<div class="istqb-topic">• {topic}</div>'
            
            if chapter.get('keywords'):
                chapter_html += f"""
                        <h4 style="color: #fbbf24 !important; margin-top: 15px;">🔑 Keywords:</h4>
                        <div class="istqb-keyword-list">
                            <p>{', '.join(chapter.get('keywords', []))}</p>
                        </div>
                """
            
            # Add business outcomes if available
            if chapter.get('business_outcomes'):
                chapter_html += f"""
                        <h4 style="color: #fbbf24 !important; margin-top: 15px;">💼 Business Outcomes:</h4>
                """
                for outcome in chapter.get('business_outcomes', []):
                    chapter_html += f'<div class="istqb-topic">• {outcome}</div>'
            
            # Add study action button
            chapter_html += f"""
                        <div style="margin-top: 20px;">
                            <button class="istqb-button">📖 Study Chapter {chapter.get('id', 'N/A')}</button>
                            <button class="istqb-button">✅ Mark as Complete</button>
                        </div>
                    </div>
                </div>
            </div>
            """
            
            gr.HTML(chapter_html)
    
    def _create_progress_tracking(self):
        """Create progress tracking interface with enhanced dark theme"""
        if not self.auth_manager or not self.auth_manager.is_logged_in():
            gr.HTML("""
            <div class="istqb-container">
                <div class="istqb-text">
                    <p>📝 Please <strong>login</strong> to track your study progress and access personalized features.</p>
                    <p>Once logged in, you'll be able to:</p>
                    <div class="istqb-topic">• Track chapter completion</div>
                    <div class="istqb-topic">• Monitor study time</div>
                    <div class="istqb-topic">• Get personalized recommendations</div>
                    <div class="istqb-topic">• Access practice exercises</div>
                </div>
            </div>
            """)
            return
        
        # Progress tracking for logged-in users
        progress_html = """
        <div class="istqb-container">
            <div class="istqb-stats">
                <h3 style="color: #60a5fa !important;">📊 Your Study Progress</h3>
                <div class="istqb-text">
                    <p><strong>Overall Progress:</strong></p>
                    <div class="istqb-progress-bg">
                        <div class="istqb-progress" style="width: 25%;"></div>
                    </div>
                    <p>25% Complete (2 of 8 chapters)</p>
                    
                    <div style="margin-top: 20px;">
                        <div class="istqb-chapter">
                            <h4 style="color: #fbbf24 !important;">📈 Study Statistics</h4>
                            <div class="istqb-text">
                                <p><strong>Study Time:</strong> 12.5 hours logged</p>
                                <p><strong>Chapters Completed:</strong> 2 / 8</p>
                                <p><strong>Last Activity:</strong> Chapter 2 - Preparing for Test Automation</p>
                                <p><strong>Next Recommended:</strong> Chapter 3 - Generic Test Automation Architecture</p>
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <div class="istqb-chapter">
                            <h4 style="color: #fbbf24 !important;">🎯 Chapter Progress</h4>
                            <div class="istqb-text">
                                <div style="margin: 10px 0;">
                                    <span class="istqb-badge">✅ Chapter 1: Introduction to Test Automation</span>
                                </div>
                                <div style="margin: 10px 0;">
                                    <span class="istqb-badge">✅ Chapter 2: Preparing for Test Automation</span>
                                </div>
                                <div style="margin: 10px 0;">
                                    <span class="istqb-badge" style="background: #374151 !important;">📖 Chapter 3: Generic Test Automation Architecture</span>
                                </div>
                                <div style="margin: 10px 0;">
                                    <span class="istqb-badge" style="background: #374151 !important;">⏳ Chapter 4: Deployment Risks and Contingencies</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <button class="istqb-button">📖 Continue Studying</button>
                        <button class="istqb-button">📊 View Detailed Report</button>
                    </div>
                </div>
            </div>
        </div>
        """
        
        gr.HTML(progress_html)
    
    def _create_study_resources(self):
        """Create study resources interface with enhanced dark theme"""
        resources = self.syllabus_data.get("study_resources", [])
        
        resources_html = """
        <div class="istqb-container">
            <h3 style="color: #60a5fa !important;">🔗 Essential Study Resources</h3>
            <div class="istqb-text">
                <p>Comprehensive collection of official ISTQB resources, books, tools, and standards for Test Automation Engineer certification.</p>
            </div>
        """
        
        if resources:
            for resource in resources:
                resources_html += f"""
                <div class="istqb-chapter">
                    <h4 style="color: #fbbf24 !important;">{resource.get('title', 'Unknown')}</h4>
                    <div class="istqb-text">
                        <p><span class="istqb-badge">{resource.get('type', 'Resource')}</span></p>
                        <p>{resource.get('description', 'No description available')}</p>
                        <div style="margin-top: 10px;">
                            <a href="{resource.get('url', '#')}" class="istqb-link" target="_blank">
                                <button class="istqb-button">🔗 Access Resource</button>
                            </a>
                        </div>
                    </div>
                </div>
                """
        else:
            resources_html += """
            <div class="istqb-chapter">
                <div class="istqb-text">
                    <p>Study resources are being prepared. Please check back soon.</p>
                </div>
            </div>
            """
        
        resources_html += "</div>"
        gr.HTML(resources_html)
    
    def _create_practice_exercises(self):
        """Create practice exercises interface with enhanced dark theme"""
        exercises = self.syllabus_data.get("practical_exercises", [])
        
        exercises_html = """
        <div class="istqb-container">
            <h3 style="color: #60a5fa !important;">💻 Practice Exercises</h3>
            <div class="istqb-text">
                <p>Hands-on exercises designed to reinforce learning objectives and prepare you for real-world automation challenges.</p>
            </div>
        """
        
        if exercises:
            for exercise in exercises:
                exercises_html += f"""
                <div class="istqb-chapter">
                    <h4 style="color: #fbbf24 !important;">{exercise.get('title', 'Unknown Exercise')}</h4>
                    <div class="istqb-text">
                        <p><span class="istqb-badge">Chapter {exercise.get('chapter', 'N/A')}</span> 
                           <span class="istqb-badge">⏱️ {exercise.get('duration_minutes', 0)} min</span></p>
                        <p>{exercise.get('description', 'No description available')}</p>
                        <div style="margin-top: 15px;">
                            <button class="istqb-button">🚀 Start Exercise</button>
                            <button class="istqb-button">📋 View Instructions</button>
                        </div>
                    </div>
                </div>
                """
        else:
            exercises_html += """
            <div class="istqb-chapter">
                <div class="istqb-text">
                    <p>Practice exercises are being developed. Please check back soon.</p>
                    <p>Future exercises will include:</p>
                    <div class="istqb-topic">• Tool evaluation workshops</div>
                    <div class="istqb-topic">• Architecture design exercises</div>
                    <div class="istqb-topic">• Risk assessment case studies</div>
                    <div class="istqb-topic">• Automation suitability analysis</div>
                </div>
            </div>
            """
        
        exercises_html += "</div>"
        gr.HTML(exercises_html) 