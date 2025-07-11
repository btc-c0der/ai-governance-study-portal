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
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from components.auth_manager import AuthManager

class PerformanceTracker:
    def __init__(self, auth_manager: Optional[AuthManager] = None):
        self.auth_manager = auth_manager or AuthManager()
        self.db_path = "data/progress.db"
        self.init_progress_database()
        self.progress_data = self.load_progress_data()
    
    def init_progress_database(self):
        """Initialize the progress tracking database"""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User progress table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                week_number INTEGER NOT NULL,
                topic_id TEXT NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completion_percentage REAL DEFAULT 100.0,
                notes TEXT,
                study_hours REAL DEFAULT 0.0,
                quiz_score REAL DEFAULT 0.0,
                UNIQUE(user_id, week_number, topic_id)
            )
        """)
        
        # Weekly statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weekly_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                week_number INTEGER NOT NULL,
                total_topics INTEGER DEFAULT 0,
                completed_topics INTEGER DEFAULT 0,
                total_study_hours REAL DEFAULT 0.0,
                average_quiz_score REAL DEFAULT 0.0,
                week_completion_percentage REAL DEFAULT 0.0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, week_number)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def mark_topic_complete(self, week_number: int, topic_id: str, study_hours: float = 0.0, 
                          quiz_score: float = 0.0, notes: str = "") -> Tuple[bool, str]:
        """Mark a topic as complete for the current user"""
        if not self.auth_manager.is_logged_in():
            return False, "Please log in to track progress"
        
        user_id = self.auth_manager.current_user['user_id']
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert or update topic completion
            cursor.execute("""
                INSERT OR REPLACE INTO user_progress 
                (user_id, week_number, topic_id, completed_at, study_hours, quiz_score, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, week_number, topic_id, datetime.now(), study_hours, quiz_score, notes))
            
            # Update weekly statistics
            self._update_weekly_stats(cursor, user_id, week_number)
            
            conn.commit()
            conn.close()
            
            return True, f"✅ Topic '{topic_id}' marked as complete for Week {week_number}"
            
        except Exception as e:
            return False, f"❌ Error saving progress: {str(e)}"
    
    def _update_weekly_stats(self, cursor, user_id: int, week_number: int):
        """Update weekly statistics for a user"""
        # Get completed topics count for this week
        cursor.execute("""
            SELECT COUNT(*) as completed, AVG(quiz_score) as avg_quiz, SUM(study_hours) as total_hours
            FROM user_progress 
            WHERE user_id = ? AND week_number = ?
        """, (user_id, week_number))
        
        result = cursor.fetchone()
        completed_topics = result[0] if result[0] else 0
        avg_quiz_score = result[1] if result[1] else 0.0
        total_hours = result[2] if result[2] else 0.0
        
        # Assume 5 topics per week (adjust as needed)
        total_topics = 5
        completion_percentage = (completed_topics / total_topics) * 100
        
        # Insert or update weekly stats
        cursor.execute("""
            INSERT OR REPLACE INTO weekly_stats 
            (user_id, week_number, total_topics, completed_topics, total_study_hours, 
             average_quiz_score, week_completion_percentage, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, week_number, total_topics, completed_topics, total_hours, 
              avg_quiz_score, completion_percentage, datetime.now()))
    
    def get_user_progress(self, user_id: Optional[int] = None) -> Dict:
        """Get comprehensive progress data for a user"""
        if not user_id and not self.auth_manager.is_logged_in():
            return self._get_sample_data()
        
        user_id = user_id or self.auth_manager.current_user['user_id']
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get weekly statistics
            cursor.execute("""
                SELECT week_number, completed_topics, total_topics, total_study_hours, 
                       average_quiz_score, week_completion_percentage
                FROM weekly_stats 
                WHERE user_id = ? 
                ORDER BY week_number
            """, (user_id,))
            
            weekly_data = cursor.fetchall()
            
            # Get topic completions
            cursor.execute("""
                SELECT week_number, topic_id, completed_at, study_hours, quiz_score, notes
                FROM user_progress 
                WHERE user_id = ? 
                ORDER BY week_number, completed_at
            """, (user_id,))
            
            topic_data = cursor.fetchall()
            
            conn.close()
            
            if not weekly_data:
                return self._get_sample_data()
            
            # Process data for charts
            weeks = [row[0] for row in weekly_data]
            weekly_progress = [row[5] for row in weekly_data]  # completion percentage
            quiz_scores = [row[4] for row in weekly_data]      # average quiz score
            study_hours = [row[3] for row in weekly_data]      # total study hours
            
            # Fill missing weeks with 0
            for week in range(1, 13):
                if week not in weeks:
                    weeks.insert(week-1, week)
                    weekly_progress.insert(week-1, 0)
                    quiz_scores.insert(week-1, 0)
                    study_hours.insert(week-1, 0)
            
            # Calculate strengths and improvement areas
            topics_completed = [row[1] for row in topic_data]
            strengths, improvement_areas = self._calculate_strengths_and_areas(topic_data)
            
            return {
                "weekly_progress": weekly_progress[:12],
                "quiz_scores": quiz_scores[:12],
                "study_hours": study_hours[:12],
                "topics_mastered": topics_completed,
                "strengths": strengths,
                "improvement_areas": improvement_areas
            }
            
        except Exception as e:
            print(f"Error getting user progress: {e}")
            return self._get_sample_data()
    
    def _calculate_strengths_and_areas(self, topic_data: List) -> Tuple[List[str], List[str]]:
        """Calculate strengths and improvement areas based on topic completion data"""
        # This is a simplified implementation - you can enhance based on your curriculum structure
        topic_scores = {}
        
        for topic_entry in topic_data:
            topic_id = topic_entry[1]
            quiz_score = topic_entry[4] if topic_entry[4] else 0
            
            if topic_id not in topic_scores:
                topic_scores[topic_id] = []
            topic_scores[topic_id].append(quiz_score)
        
        # Calculate average scores per topic
        avg_scores = {}
        for topic, scores in topic_scores.items():
            avg_scores[topic] = sum(scores) / len(scores) if scores else 0
        
        # Sort by performance
        sorted_topics = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Top 3 as strengths, bottom 3 as improvement areas
        strengths = [topic for topic, score in sorted_topics[:3] if score > 75]
        improvement_areas = [topic for topic, score in sorted_topics[-3:] if score < 75]
        
        # Default values if not enough data
        if not strengths:
            strengths = ["Regulatory Knowledge", "Risk Assessment", "Technical Implementation"]
        if not improvement_areas:
            improvement_areas = ["Bias Mitigation", "Sector Applications", "Audit Processes"]
        
        return strengths, improvement_areas
    
    def _get_sample_data(self) -> Dict:
        """Get sample data for demo purposes"""
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

    def load_progress_data(self):
        """Load progress data for the current user"""
        return self.get_user_progress()
    
    def refresh_progress_data(self):
        """Refresh progress data from database"""
        self.progress_data = self.load_progress_data()
        return self.progress_data
    
    def _create_progress_summary_html(self) -> str:
        """Create dynamic progress summary HTML"""
        data = self.progress_data
        
        overall_progress = sum(data['weekly_progress']) / len(data['weekly_progress'])
        quiz_average = sum(data['quiz_scores']) / len(data['quiz_scores'])
        total_hours = sum(data['study_hours'])
        topics_count = len(data['topics_mastered'])
        
        return f"""
        <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); 
                    color: white; padding: 2rem; border-radius: 15px; margin: 1rem 0;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <h3 style="color: #fbbf24; margin-top: 0; font-size: 1.6rem; text-align: center;">
                📈 Progress Summary
            </h3>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; margin-top: 1.5rem;">
                <div style="text-align: center; background: rgba(255, 255, 255, 0.1); 
                            padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 2.5rem; font-weight: bold; color: #fbbf24;">{overall_progress:.0f}%</div>
                    <div style="color: #f3f4f6; font-weight: 500;">Overall Progress</div>
                </div>
                <div style="text-align: center; background: rgba(255, 255, 255, 0.1); 
                            padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 2.5rem; font-weight: bold; color: #fbbf24;">{quiz_average:.0f}%</div>
                    <div style="color: #f3f4f6; font-weight: 500;">Quiz Average</div>
                </div>
                <div style="text-align: center; background: rgba(255, 255, 255, 0.1); 
                            padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 2.5rem; font-weight: bold; color: #fbbf24;">{total_hours:.0f}</div>
                    <div style="color: #f3f4f6; font-weight: 500;">Study Hours</div>
                </div>
                <div style="text-align: center; background: rgba(255, 255, 255, 0.1); 
                            padding: 1rem; border-radius: 10px;">
                    <div style="font-size: 2.5rem; font-weight: bold; color: #fbbf24;">{topics_count}/12</div>
                    <div style="color: #f3f4f6; font-weight: 500;">Topics Mastered</div>
                </div>
            </div>
        </div>
        """
    
    def _create_strengths_html(self) -> str:
        """Create dynamic strengths HTML"""
        strengths = self.progress_data['strengths']
        strengths_list = "\n".join([f"<li>{strength}</li>" for strength in strengths])
        
        return f"""
        <div style="background: #f0f9ff; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
            <h4 style="color: #1e40af;">💪 Strengths</h4>
            <ul style="margin: 0.5rem 0;">
                {strengths_list}
            </ul>
        </div>
        """
    
    def _create_improvements_html(self) -> str:
        """Create dynamic improvements HTML"""
        improvements = self.progress_data['improvement_areas']
        improvements_list = "\n".join([f"<li>{area}</li>" for area in improvements])
        
        return f"""
        <div style="background: #fef3c7; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
            <h4 style="color: #92400e;">🎯 Focus Areas</h4>
            <ul style="margin: 0.5rem 0;">
                {improvements_list}
            </ul>
        </div>
        """
    
    def _create_recommendations_html(self) -> str:
        """Create dynamic recommendations HTML"""
        return """
        <div style="background: #ecfdf5; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
            <h4 style="color: #059669;">📚 Study Recommendations</h4>
            <ul style="margin: 0.5rem 0;">
                <li>Focus on Article 10 (Data Governance)</li>
                <li>Practice bias detection scenarios</li>
                <li>Review sector-specific case studies</li>
                <li>Complete audit framework exercises</li>
            </ul>
        </div>
        """
    
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
                progress_summary = gr.HTML(self._create_progress_summary_html())
            
            with gr.Column():
                # Weekly progress chart with initial value
                progress_chart = gr.Plot(
                    label="📈 Weekly Trends",
                    value=self.create_weekly_progress_chart()
                )
        
        # Progress tracking section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🎯 Mark Topic Complete")
                
                with gr.Row():
                    week_input = gr.Number(
                        label="Week Number",
                        value=1,
                        minimum=1,
                        maximum=12,
                        step=1
                    )
                    topic_input = gr.Textbox(
                        label="Topic ID",
                        placeholder="e.g., 'Risk Management', 'EU AI Act Basics'",
                        value=""
                    )
                
                with gr.Row():
                    study_hours_input = gr.Number(
                        label="Study Hours",
                        value=0.0,
                        minimum=0,
                        step=0.5
                    )
                    quiz_score_input = gr.Number(
                        label="Quiz Score (%)",
                        value=0.0,
                        minimum=0,
                        maximum=100,
                        step=1
                    )
                
                notes_input = gr.Textbox(
                    label="Notes",
                    placeholder="Add any notes about your learning...",
                    lines=3
                )
                
                mark_complete_btn = gr.Button("✅ Mark Topic Complete", variant="primary")
                completion_message = gr.Textbox(label="Status", interactive=False)
        
        with gr.Row():
            with gr.Column():
                # Strengths and improvements
                strengths_display = gr.HTML(self._create_strengths_html())
                improvements_display = gr.HTML(self._create_improvements_html())
            
            with gr.Column():
                # Study recommendations
                recommendations = gr.HTML(self._create_recommendations_html())
        
        # Add refresh button to update charts
        with gr.Row():
            refresh_btn = gr.Button("🔄 Refresh Progress Data", variant="secondary")
            
        # Event handlers
        def handle_mark_complete(week_num, topic_id, study_hours, quiz_score, notes):
            """Handle marking a topic as complete"""
            if not topic_id.strip():
                return "❌ Please enter a topic ID"
            
            success, message = self.mark_topic_complete(
                int(week_num), topic_id.strip(), study_hours, quiz_score, notes
            )
            
            if success:
                # Refresh progress data
                self.refresh_progress_data()
                return message
            else:
                return message
        
        def handle_refresh():
            """Handle refresh button click"""
            self.refresh_progress_data()
            return (
                self.create_progress_radar(),
                self.create_weekly_progress_chart(),
                self._create_progress_summary_html(),
                self._create_strengths_html(),
                self._create_improvements_html(),
                "✅ Progress data refreshed!"
            )
        
        # Bind events
        mark_complete_btn.click(
            fn=handle_mark_complete,
            inputs=[week_input, topic_input, study_hours_input, quiz_score_input, notes_input],
            outputs=[completion_message]
        )
        
        refresh_btn.click(
            fn=handle_refresh,
            outputs=[radar_chart, progress_chart, progress_summary, strengths_display, improvements_display, completion_message]
        )
        
        return radar_chart, progress_chart