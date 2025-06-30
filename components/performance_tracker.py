"""
📊 Performance Tracker Component
Interactive progress tracking and analytics for AI governance studies.
"""

import gradio as gr
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import json

class PerformanceTracker:
    def __init__(self):
        self.progress_data = self.load_progress_data()
    
    def load_progress_data(self):
        """Load or create sample progress data"""
        return {
            "weekly_progress": [85, 92, 78, 95, 88, 90, 82, 75, 88, 92, 85, 78],
            "quiz_scores": [75, 82, 88, 92, 85, 90, 88, 94, 91, 87, 93, 89],
            "study_hours": [8, 10, 12, 9, 11, 8, 15, 12, 10, 9, 11, 13],
            "topics_mastered": ["Foundations", "EU AI Act Basics", "Risk Management", 
                              "High-Risk Systems", "Governance", "Ethics", "Global Regs"],
            "strengths": ["Regulatory Knowledge", "Risk Assessment", "Technical Implementation"],
            "improvement_areas": ["Bias Mitigation", "Sector Applications", "Audit Processes"]
        }
    
    def create_progress_radar(self):
        """Create radar chart showing competency areas"""
        categories = ['AI Governance', 'Risk Management', 'Regulatory Compliance', 
                     'Ethics & Bias', 'Technical Implementation']
        scores = [85, 92, 88, 75, 82]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=scores + [scores[0]],  # Close the polygon
            theta=categories + [categories[0]],
            fill='toself',
            name='Current Level',
            marker_color='rgba(59, 130, 246, 0.6)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            title="🎯 Competency Radar",
            height=400
        )
        
        return fig
    
    def create_weekly_progress_chart(self):
        """Create weekly progress line chart"""
        weeks = list(range(1, 13))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=weeks,
            y=self.progress_data['weekly_progress'],
            mode='lines+markers',
            name='Weekly Progress (%)',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=weeks,
            y=self.progress_data['quiz_scores'],
            mode='lines+markers',
            name='Quiz Scores (%)',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="📈 Weekly Progress & Quiz Performance",
            xaxis_title="Week",
            yaxis_title="Score (%)",
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    def create_interface(self):
        """Create the performance tracking interface"""
        
        gr.Markdown("## 📊 Learning Performance Dashboard")
        
        with gr.Row():
            with gr.Column():
                # Radar chart
                radar_chart = gr.Plot(label="🎯 Competency Assessment")
                
                # Progress summary
                progress_summary = gr.HTML("""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            color: white; padding: 1.5rem; border-radius: 15px; margin: 1rem 0;">
                    <h3>📈 Progress Summary</h3>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 1rem;">
                        <div style="text-align: center;">
                            <div style="font-size: 2rem; font-weight: bold;">87%</div>
                            <div>Overall Progress</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 2rem; font-weight: bold;">89%</div>
                            <div>Quiz Average</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 2rem; font-weight: bold;">128</div>
                            <div>Study Hours</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 2rem; font-weight: bold;">7/12</div>
                            <div>Topics Mastered</div>
                        </div>
                    </div>
                </div>
                """)
            
            with gr.Column():
                # Weekly progress chart
                progress_chart = gr.Plot(label="📈 Weekly Trends")
        
        with gr.Row():
            with gr.Column():
                # Strengths and improvements
                strengths_display = gr.HTML("""
                <div style="background: #f0f9ff; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                    <h4 style="color: #1e40af;">💪 Strengths</h4>
                    <ul style="margin: 0.5rem 0;">
                        <li>Regulatory Knowledge (92%)</li>
                        <li>Risk Assessment (88%)</li>
                        <li>Technical Implementation (85%)</li>
                    </ul>
                </div>
                """)
                
                improvements_display = gr.HTML("""
                <div style="background: #fef3c7; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                    <h4 style="color: #92400e;">🎯 Focus Areas</h4>
                    <ul style="margin: 0.5rem 0;">
                        <li>Bias Mitigation (75%)</li>
                        <li>Sector Applications (78%)</li>
                        <li>Audit Processes (72%)</li>
                    </ul>
                </div>
                """)
            
            with gr.Column():
                # Study recommendations
                recommendations = gr.HTML("""
                <div style="background: #ecfdf5; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                    <h4 style="color: #059669;">📚 Study Recommendations</h4>
                    <ul style="margin: 0.5rem 0;">
                        <li>Focus on Article 10 (Data Governance)</li>
                        <li>Practice bias detection scenarios</li>
                        <li>Review sector-specific case studies</li>
                        <li>Complete audit framework exercises</li>
                    </ul>
                </div>
                """)
        
        # Initialize charts
        radar_chart.value = self.create_progress_radar()
        progress_chart.value = self.create_weekly_progress_chart()
        
        return radar_chart, progress_chart 