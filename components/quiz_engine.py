"""
🧪 Quiz Engine Component
Interactive AIGP mock exam system with scoring and detailed explanations.
"""

import gradio as gr
import random
import json
from datetime import datetime

class QuizEngine:
    def __init__(self):
        self.question_bank = self.load_question_bank()
        self.current_quiz = []
        self.quiz_results = {}
    
    def load_question_bank(self):
        """Load comprehensive AIGP question bank"""
        return [
            {
                "id": 1,
                "category": "EU AI Act Fundamentals",
                "question": "Which article of the EU AI Act defines prohibited AI practices?",
                "options": ["Article 3", "Article 5", "Article 9", "Article 52"],
                "correct": 1,
                "explanation": "Article 5 explicitly lists the prohibited AI practices including subliminal techniques and exploitation of vulnerabilities.",
                "difficulty": "Easy"
            },
            {
                "id": 2,
                "category": "High-Risk AI Systems",
                "question": "What is required before placing a high-risk AI system on the market?",
                "options": ["User training", "Conformity assessment", "Insurance policy", "Government approval"],
                "correct": 1,
                "explanation": "Article 16 requires providers to ensure conformity assessment procedures are completed before market placement.",
                "difficulty": "Medium"
            },
            {
                "id": 3,
                "category": "Risk Management",
                "question": "Risk management for high-risk AI systems must be:",
                "options": ["One-time assessment", "Annual review", "Continuous iterative process", "Market-based evaluation"],
                "correct": 2,
                "explanation": "Article 9 emphasizes risk management as a continuous, iterative process throughout the system lifecycle.",
                "difficulty": "Medium"
            },
            {
                "id": 4,
                "category": "Data Governance",
                "question": "Training datasets for high-risk AI systems must be:",
                "options": ["As large as possible", "Representative and error-free", "Publicly available", "Pre-approved by authorities"],
                "correct": 1,
                "explanation": "Article 10 requires training datasets to be representative, error-free, and complete with appropriate statistical properties.",
                "difficulty": "Hard"
            },
            {
                "id": 5,
                "category": "Transparency Requirements",
                "question": "AI systems that interact with humans must:",
                "options": ["Be fully automated", "Disclose they are AI systems", "Require human approval", "Use biometric identification"],
                "correct": 1,
                "explanation": "Article 52 mandates clear disclosure when humans interact with AI systems, ensuring transparency.",
                "difficulty": "Easy"
            }
        ]
    
    def generate_quiz(self, num_questions=10, difficulty="Mixed"):
        """Generate a quiz with specified parameters"""
        available_questions = self.question_bank.copy()
        
        if difficulty != "Mixed":
            available_questions = [q for q in available_questions if q["difficulty"] == difficulty]
        
        if len(available_questions) < num_questions:
            num_questions = len(available_questions)
        
        self.current_quiz = random.sample(available_questions, num_questions)
        return self.current_quiz
    
    def calculate_score(self, answers):
        """Calculate quiz score and provide detailed feedback"""
        if not self.current_quiz:
            return 0, []
        
        correct_answers = 0
        detailed_results = []
        
        for i, question in enumerate(self.current_quiz):
            user_answer = answers.get(i, -1)
            is_correct = user_answer == question["correct"]
            
            if is_correct:
                correct_answers += 1
            
            detailed_results.append({
                "question": question["question"],
                "user_answer": question["options"][user_answer] if 0 <= user_answer < len(question["options"]) else "No answer",
                "correct_answer": question["options"][question["correct"]],
                "is_correct": is_correct,
                "explanation": question["explanation"],
                "category": question["category"]
            })
        
        score_percentage = (correct_answers / len(self.current_quiz)) * 100
        
        return score_percentage, detailed_results
    
    def create_interface(self):
        """Create the quiz interface"""
        
        gr.Markdown("## 🧪 AIGP Mock Examination Center")
        gr.Markdown("Practice with realistic AIGP certification questions and receive detailed feedback.")
        
        with gr.Tabs():
            # Quiz Setup Tab
            with gr.Tab("🎯 Quiz Setup"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 📋 Quiz Configuration")
                        
                        num_questions = gr.Slider(
                            minimum=5,
                            maximum=20,
                            value=10,
                            step=1,
                            label="Number of Questions"
                        )
                        
                        difficulty_level = gr.Dropdown(
                            choices=["Mixed", "Easy", "Medium", "Hard"],
                            value="Mixed",
                            label="Difficulty Level"
                        )
                        
                        quiz_mode = gr.Radio(
                            choices=["Practice Mode", "Exam Mode"],
                            value="Practice Mode",
                            label="Quiz Mode"
                        )
                        
                        start_quiz_btn = gr.Button("🚀 Start Quiz", variant="primary", size="lg")
                    
                    with gr.Column():
                        gr.Markdown("### 📊 Quiz Statistics")
                        
                        stats_display = gr.HTML("""
                        <div style="background: #f8fafc; padding: 1rem; border-radius: 10px;">
                            <h4>📈 Your Performance History</h4>
                            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 1rem;">
                                <div style="text-align: center; background: white; padding: 0.5rem; border-radius: 5px;">
                                    <div style="font-size: 1.5rem; font-weight: bold; color: #059669;">87%</div>
                                    <div style="font-size: 0.9rem; color: #6b7280;">Average Score</div>
                                </div>
                                <div style="text-align: center; background: white; padding: 0.5rem; border-radius: 5px;">
                                    <div style="font-size: 1.5rem; font-weight: bold; color: #3b82f6;">15</div>
                                    <div style="font-size: 0.9rem; color: #6b7280;">Quizzes Taken</div>
                                </div>
                                <div style="text-align: center; background: white; padding: 0.5rem; border-radius: 5px;">
                                    <div style="font-size: 1.5rem; font-weight: bold; color: #8b5cf6;">92%</div>
                                    <div style="font-size: 0.9rem; color: #6b7280;">Best Score</div>
                                </div>
                                <div style="text-align: center; background: white; padding: 0.5rem; border-radius: 5px;">
                                    <div style="font-size: 1.5rem; font-weight: bold; color: #f59e0b;">78%</div>
                                    <div style="font-size: 0.9rem; color: #6b7280;">Last Score</div>
                                </div>
                            </div>
                        </div>
                        """)
            
            # Quiz Taking Tab
            with gr.Tab("📝 Take Quiz"):
                quiz_container = gr.HTML("""
                <div style="text-align: center; padding: 2rem; color: #6b7280;">
                    <h3>🎯 Ready to Start?</h3>
                    <p>Configure your quiz in the Setup tab and click "Start Quiz" to begin.</p>
                </div>
                """)
                
                submit_quiz_btn = gr.Button("📤 Submit Quiz", variant="primary", visible=False)
                
            # Results Tab
            with gr.Tab("📊 Results"):
                results_display = gr.HTML("""
                <div style="text-align: center; padding: 2rem; color: #6b7280;">
                    <h3>📈 Results will appear here</h3>
                    <p>Complete a quiz to see detailed results and explanations.</p>
                </div>
                """)
                
                # Performance breakdown
                category_breakdown = gr.Plot(label="📊 Performance by Category")
                
                # Detailed feedback
                detailed_feedback = gr.HTML("")
        
        # Quiz generation and display
        def generate_quiz_interface(num_q, difficulty, mode):
            """Generate quiz interface with questions"""
            questions = self.generate_quiz(num_q, difficulty)
            
            if not questions:
                return "<p>No questions available for the selected criteria.</p>", gr.update(visible=False)
            
            quiz_html = f"""
            <div style="background: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e5e7eb;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; 
                            padding-bottom: 1rem; border-bottom: 2px solid #e5e7eb;">
                    <h3 style="margin: 0; color: #1f2937;">🧪 AIGP Mock Exam</h3>
                    <div style="background: #3b82f6; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;">
                        {len(questions)} Questions | {difficulty} Level | {mode}
                    </div>
                </div>
            """
            
            for i, q in enumerate(questions):
                quiz_html += f"""
                <div style="margin-bottom: 2rem; padding: 1rem; background: #f8fafc; border-radius: 8px; border-left: 4px solid #3b82f6;">
                    <h4 style="margin: 0 0 1rem 0; color: #1f2937;">Question {i+1}: {q['question']}</h4>
                    <div style="margin-left: 1rem;">
                """
                
                for j, option in enumerate(q['options']):
                    quiz_html += f"""
                        <div style="margin: 0.5rem 0;">
                            <label style="display: flex; align-items: center; cursor: pointer; padding: 0.5rem; 
                                         border-radius: 5px; transition: background 0.2s;"
                                   onmouseover="this.style.background='#e0e7ff'" 
                                   onmouseout="this.style.background='transparent'">
                                <input type="radio" name="q{i}" value="{j}" 
                                       style="margin-right: 0.5rem; transform: scale(1.2);">
                                <span>{chr(65+j)}) {option}</span>
                            </label>
                        </div>
                    """
                
                quiz_html += f"""
                    </div>
                    <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #6b7280;">
                        Category: {q['category']} | Difficulty: {q['difficulty']}
                    </div>
                </div>
                """
            
            quiz_html += "</div>"
            
            return quiz_html, gr.update(visible=True)
        
        def show_results():
            """Display quiz results and analysis"""
            # Placeholder results
            results_html = """
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                        color: white; padding: 2rem; border-radius: 15px; margin-bottom: 1.5rem;">
                <div style="text-align: center;">
                    <h2 style="margin: 0 0 1rem 0;">🎉 Quiz Complete!</h2>
                    <div style="font-size: 3rem; font-weight: bold; margin: 1rem 0;">87%</div>
                    <p style="font-size: 1.2rem; margin: 0;">Excellent performance! You're well-prepared for the AIGP exam.</p>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1.5rem 0;">
                <div style="background: #f0f9ff; padding: 1rem; border-radius: 10px; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #3b82f6;">8/10</div>
                    <div style="color: #6b7280;">Correct Answers</div>
                </div>
                <div style="background: #ecfdf5; padding: 1rem; border-radius: 10px; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #059669;">12 min</div>
                    <div style="color: #6b7280;">Time Taken</div>
                </div>
                <div style="background: #fef3c7; padding: 1rem; border-radius: 10px; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #d97706;">Mixed</div>
                    <div style="color: #6b7280;">Difficulty</div>
                </div>
            </div>
            """
            
            return results_html
        
        # Event handlers
        start_quiz_btn.click(
            fn=generate_quiz_interface,
            inputs=[num_questions, difficulty_level, quiz_mode],
            outputs=[quiz_container, submit_quiz_btn]
        )
        
        submit_quiz_btn.click(
            fn=show_results,
            outputs=[results_display]
        )
        
        return quiz_container, results_display 