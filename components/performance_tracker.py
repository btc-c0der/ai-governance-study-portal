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
        try:
            categories = ['AI Governance', 'Risk Management', 'Regulatory Compliance', 
                         'Ethics & Bias', 'Technical Implementation']
            scores = [85, 92, 88, 75, 82]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=scores + [scores[0]],  # Close the polygon
                theta=categories + [categories[0]],
                fill='toself',
                name='Current Level',
                marker_color='rgba(59, 130, 246, 0.6)',
                line_color='rgba(59, 130, 246, 0.8)'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True, 
                        range=[0, 100],
                        ticksuffix='%',
                        gridcolor='rgba(0,0,0,0.1)'
                    ),
                    angularaxis=dict(
                        gridcolor='rgba(0,0,0,0.1)'
                    )
                ),
                title="🎯 Competency Radar",
                height=400,
                template='plotly_white',
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            return fig
        except Exception as e:
            print(f"Error creating radar chart: {e}")
            # Return empty figure if there's an error
            return go.Figure().add_annotation(
                text="Chart temporarily unavailable",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
    
    def create_weekly_progress_chart(self):
        """Create weekly progress line chart"""
        try:
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
                hovermode='x unified',
                template='plotly_white',
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            return fig
        except Exception as e:
            print(f"Error creating weekly progress chart: {e}")
            # Return empty figure if there's an error
            return go.Figure().add_annotation(
                text="Chart temporarily unavailable",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
    
    def create_study_hours_chart(self):
        """Create study hours bar chart"""
        try:
            weeks = list(range(1, 13))
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=weeks,
                y=self.progress_data['study_hours'],
                name='Study Hours',
                marker_color='rgba(16, 185, 129, 0.8)',
                text=self.progress_data['study_hours'],
                textposition='auto',
            ))
            
            fig.update_layout(
                title="⏱️ Weekly Study Hours",
                xaxis_title="Week",
                yaxis_title="Hours",
                height=300,
                template='plotly_white',
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            return fig
        except Exception as e:
            print(f"Error creating study hours chart: {e}")
            return go.Figure().add_annotation(
                text="Chart temporarily unavailable",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )

    def create_interface(self):
        """Create the performance tracking interface"""
        
        gr.Markdown("## 📊 Learning Performance Dashboard")
        
        with gr.Row():
            with gr.Column():
                # Radar chart with initial value
                radar_chart = gr.Plot(
                    label="🎯 Competency Assessment",
                    value=self.create_progress_radar()
                )
                
                # Progress summary
                progress_summary = gr.HTML("""
                <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); 
                            color: white; padding: 2rem; border-radius: 15px; margin: 1rem 0;
                            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                    <h3 style="color: #fbbf24; margin-top: 0; font-size: 1.6rem; text-align: center;">
                        📈 Progress Summary
                    </h3>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; margin-top: 1.5rem;">
                        <div style="text-align: center; background: rgba(255, 255, 255, 0.1); 
                                    padding: 1rem; border-radius: 10px;">
                            <div style="font-size: 2.5rem; font-weight: bold; color: #fbbf24;">87%</div>
                            <div style="color: #f3f4f6; font-weight: 500;">Overall Progress</div>
                        </div>
                        <div style="text-align: center; background: rgba(255, 255, 255, 0.1); 
                                    padding: 1rem; border-radius: 10px;">
                            <div style="font-size: 2.5rem; font-weight: bold; color: #fbbf24;">89%</div>
                            <div style="color: #f3f4f6; font-weight: 500;">Quiz Average</div>
                        </div>
                        <div style="text-align: center; background: rgba(255, 255, 255, 0.1); 
                                    padding: 1rem; border-radius: 10px;">
                            <div style="font-size: 2.5rem; font-weight: bold; color: #fbbf24;">128</div>
                            <div style="color: #f3f4f6; font-weight: 500;">Study Hours</div>
                        </div>
                        <div style="text-align: center; background: rgba(255, 255, 255, 0.1); 
                                    padding: 1rem; border-radius: 10px;">
                            <div style="font-size: 2.5rem; font-weight: bold; color: #fbbf24;">7/12</div>
                            <div style="color: #f3f4f6; font-weight: 500;">Topics Mastered</div>
                        </div>
                    </div>
                </div>
                """)
            
            with gr.Column():
                # Weekly progress chart with initial value
                progress_chart = gr.Plot(
                    label="📈 Weekly Trends",
                    value=self.create_weekly_progress_chart()
                )
        
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
        
        # Add a refresh button to update charts
        with gr.Row():
            refresh_btn = gr.Button("🔄 Refresh Charts", variant="primary")
            refresh_btn.click(
                fn=lambda: (self.create_progress_radar(), self.create_weekly_progress_chart()),
                outputs=[radar_chart, progress_chart]
            )
        
        return radar_chart, progress_chart