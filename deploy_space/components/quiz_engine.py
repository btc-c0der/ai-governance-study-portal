#!/usr/bin/env python3
"""
🧪 Quiz Engine Module
Advanced AIGP mock examination system with comprehensive question bank and analytics.

Features:
- Multiple quiz modes (practice, domain focus, exam simulation)
- Real-time progress tracking and performance analytics
- Detailed question bank with official AIGP domains
- Advanced scoring algorithms and personalized recommendations
- Database persistence for authenticated and anonymous users
"""

import json
import sqlite3
import uuid
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import gradio as gr
import plotly.express as px
import plotly.graph_objects as go

from .database_manager import DatabaseManager
from .auth_manager import AuthManager

class QuizEngine:
    def __init__(self, auth_manager: Optional[AuthManager] = None):
        """Initialize quiz engine with database and authentication support"""
        self.auth_manager = auth_manager
        
        # Use shared database manager
        if auth_manager:
            self.db_manager = DatabaseManager(auth_manager.db_path)
        else:
            self.db_manager = DatabaseManager()
        
        # Quiz state
        self.current_quiz_session: Optional[Dict[str, Any]] = None
        self.session_stats: Dict[str, Dict[str, Any]] = {}
        
        # Load quiz data
        self.quiz_data = self.load_quiz_data()
        
        # Initialize database tables
        self.init_quiz_database()
        
        print("✅ Quiz Engine initialized with comprehensive AIGP question bank")
        
    def init_quiz_database(self):
        """Initialize quiz results database"""
        try:
            # Quiz results table
            quiz_results_schema = """
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                user_type TEXT NOT NULL DEFAULT 'anonymous',
                quiz_mode TEXT NOT NULL,
                domain_focus TEXT,
                difficulty_level TEXT,
                total_questions INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL,
                answered_questions INTEGER NOT NULL DEFAULT 0,
                completion_rate REAL NOT NULL DEFAULT 0,
                score REAL NOT NULL,
                passed BOOLEAN NOT NULL,
                time_taken_minutes REAL,
                performance_data TEXT,
                recommendations TEXT,
                detailed_answers TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """
            
            # Quiz responses table (detailed question-by-question data)
            quiz_responses_schema = """
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                question_index INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                user_answer INTEGER,
                correct_answer INTEGER NOT NULL,
                is_correct BOOLEAN NOT NULL,
                domain TEXT,
                difficulty TEXT,
                time_taken_seconds REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES quiz_results (session_id)
            """
            
            # Create tables using shared database manager
            self.db_manager.create_table_if_not_exists("quiz_results", quiz_results_schema)
            self.db_manager.create_table_if_not_exists("quiz_responses", quiz_responses_schema)
            
            print("✅ Quiz database tables initialized")
            
        except Exception as e:
            print(f"❌ Error initializing quiz database: {e}")
            raise e
    
    def load_quiz_data(self) -> Dict[str, Any]:
        """Load quiz questions and metadata from JSON file"""
        quiz_file = Path("data/aigp_quiz_bank.json")
        
        try:
            with open(quiz_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Validate required fields
            if not all(key in data for key in ["quiz_metadata", "questions", "exam_simulation_settings"]):
                raise ValueError("Invalid quiz data structure")
                
            return data
            
        except FileNotFoundError:
            print("Warning: Quiz bank JSON file not found. Creating minimal quiz data.")
            return self._create_minimal_quiz_data()
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Error loading quiz data: {e}. Using minimal quiz data.")
            return self._create_minimal_quiz_data()
    
    def _create_minimal_quiz_data(self) -> Dict[str, Any]:
        """Create minimal quiz data as fallback"""
        return {
            "quiz_metadata": {
                "title": "Basic AIGP Quiz",
                "version": "1.0",
                "total_questions": 5,
                "domains": ["AI Governance Fundamentals"]
            },
            "questions": [
                {
                    "id": 1,
                    "domain": "AI Governance Fundamentals",
                    "difficulty": "Easy",
                    "question": "What does AIGP stand for?",
                    "options": ["AI General Principles", "Artificial Intelligence Governance Professional", "AI Global Protocol", "Advanced Intelligence Guide Program"],
                    "correct": 1,
                    "explanation": "AIGP stands for Artificial Intelligence Governance Professional certification."
                }
            ],
            "exam_simulation_settings": {
                "standard_exam": {"total_questions": 5, "time_limit_minutes": 10, "passing_score": 70}
            }
        }
    
    def get_questions_by_criteria(self, 
                                domain: Optional[str] = None,
                                difficulty: Optional[str] = None,
                                question_type: Optional[str] = None,
                                limit: Optional[int] = None) -> List[Dict]:
        """Filter questions based on specified criteria"""
        questions = self.quiz_data["questions"].copy()
        
        # Apply filters
        if domain and domain != "Mixed":
            questions = [q for q in questions if q.get("domain") == domain]
        
        if difficulty and difficulty != "Mixed":
            questions = [q for q in questions if q.get("difficulty") == difficulty]
            
        if question_type and question_type != "Mixed":
            questions = [q for q in questions if q.get("type") == question_type]
        
        # Shuffle and limit
        random.shuffle(questions)
        if limit:
            questions = questions[:limit]
            
        return questions
    
    def generate_quiz_session(self, 
                            mode: str = "practice",
                            num_questions: int = 10,
                            difficulty: str = "Mixed",
                            domain: str = "Mixed",
                            time_limit: Optional[int] = None) -> Dict[str, Any]:
        """Generate a new quiz session with specified parameters"""
        
        print(f"🎯 Generating quiz session:")
        print(f"   Mode: {mode}")
        print(f"   Questions: {num_questions}")
        print(f"   Difficulty: {difficulty}")
        print(f"   Domain: {domain}")
        print(f"   Time Limit: {time_limit}")
        
        # Apply mode-specific constraints while respecting user choices
        if mode == "exam_simulation":
            # For exam simulation, respect user choice but cap at official exam limits
            settings = self.quiz_data["exam_simulation_settings"]["standard_exam"]
            max_exam_questions = settings["total_questions"]
            if num_questions > max_exam_questions:
                print(f"⚠️ Capping questions at exam maximum: {max_exam_questions}")
                num_questions = max_exam_questions
            
            # Use default exam time limit if user didn't specify one
            if time_limit is None:
                time_limit = settings["time_limit_minutes"]
                print(f"📅 Using default exam time limit: {time_limit} minutes")
        else:
            # For practice modes, respect all user choices
            # Only set default time limit if user didn't specify one
            if time_limit is None:
                practice_settings = self.quiz_data["exam_simulation_settings"]["practice_modes"]
                if mode in practice_settings:
                    time_limit = practice_settings[mode]["time_limit_minutes"]
                    print(f"📅 Using default practice time limit: {time_limit} minutes")
                else:
                    time_limit = 15  # Default fallback
                    print(f"📅 Using fallback time limit: {time_limit} minutes")
        
        # Generate questions based on user criteria
        print(f"🔍 Searching for questions with criteria: domain={domain}, difficulty={difficulty}, limit={num_questions}")
        questions = self.get_questions_by_criteria(
            domain=domain if domain != "Mixed" else None,
            difficulty=difficulty if difficulty != "Mixed" else None,
            limit=num_questions
        )
        
        if not questions:
            print("❌ No questions found for specified criteria")
            return {"error": "No questions available for the specified criteria"}
        
        print(f"✅ Found {len(questions)} questions")
        
        # Create session
        session_id = f"quiz_{int(time.time())}"
        self.current_quiz_session = {
            "session_id": session_id,
            "mode": mode,
            "questions": questions,
            "start_time": datetime.now(),
            "time_limit_minutes": time_limit,
            "answers": {},
            "completed": False,
            "domain": domain,
            "difficulty": difficulty,
            "total_questions": len(questions)
        }
        
        print(f"🎉 Quiz session created successfully!")
        print(f"   Session ID: {session_id}")
        print(f"   Actual Questions: {len(questions)}")
        print(f"   Time Limit: {time_limit} minutes")
        
        return self.current_quiz_session
    
    def submit_answer(self, question_index: int, answer_index: int) -> bool:
        """Submit answer for a specific question"""
        if not self.current_quiz_session or self.current_quiz_session["completed"]:
            return False
            
        self.current_quiz_session["answers"][question_index] = answer_index
        return True
    
    def update_progress(self) -> Dict[str, Any]:
        """Get current quiz progress for real-time updates"""
        if not self.current_quiz_session:
            return {"error": "No active session"}
        
        session = self.current_quiz_session
        total_questions = len(session["questions"])
        answered_questions = len(session["answers"])
        progress_percentage = (answered_questions / total_questions) * 100 if total_questions > 0 else 0
        
        # Calculate time remaining if there's a time limit
        time_remaining = None
        if session.get("time_limit_minutes"):
            elapsed = datetime.now() - session["start_time"]
            elapsed_minutes = elapsed.total_seconds() / 60
            time_remaining = max(0, session["time_limit_minutes"] - elapsed_minutes)
        
        return {
            "progress_percentage": progress_percentage,
            "answered_questions": answered_questions,
            "total_questions": total_questions,
            "time_remaining_minutes": time_remaining,
            "session_id": session["session_id"]
        }
    
    def calculate_quiz_results(self) -> Dict[str, Any]:
        """Calculate comprehensive quiz results and analytics"""
        if not self.current_quiz_session:
            return {"error": "No active quiz session"}
        
        session = self.current_quiz_session
        questions = session["questions"]
        answers = session["answers"]
        
        # Calculate basic metrics
        total_questions = len(questions)
        answered_questions = len(answers)
        correct_answers = 0
        domain_performance = {}
        difficulty_performance = {}
        
        detailed_results = []
        
        for i, question in enumerate(questions):
            user_answer = answers.get(i, -1)
            is_correct = user_answer == question["correct"]
            
            if is_correct:
                correct_answers += 1
            
            # Track domain performance
            domain = question["domain"]
            if domain not in domain_performance:
                domain_performance[domain] = {"correct": 0, "total": 0}
            domain_performance[domain]["total"] += 1
            if is_correct:
                domain_performance[domain]["correct"] += 1
            
            # Track difficulty performance
            difficulty = question["difficulty"]
            if difficulty not in difficulty_performance:
                difficulty_performance[difficulty] = {"correct": 0, "total": 0}
            difficulty_performance[difficulty]["total"] += 1
            if is_correct:
                difficulty_performance[difficulty]["correct"] += 1
            
            # Detailed result for each question
            detailed_results.append({
                "question_id": question["id"],
                "question": question["question"],
                "user_answer": question["options"][user_answer] if 0 <= user_answer < len(question["options"]) else "No answer",
                "correct_answer": question["options"][question["correct"]],
                "is_correct": is_correct,
                "explanation": question["explanation"],
                "domain": question["domain"],
                "difficulty": question["difficulty"],
                "legal_reference": question.get("legal_reference", "")
            })
        
        # Calculate percentages
        score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        completion_rate = (answered_questions / total_questions) * 100 if total_questions > 0 else 0
        
        # Calculate time taken
        end_time = datetime.now()
        time_taken = end_time - session["start_time"]
        time_taken_minutes = time_taken.total_seconds() / 60
        
        # Determine pass/fail
        passing_score = self.quiz_data["exam_simulation_settings"]["standard_exam"]["passing_score"]
        passed = score_percentage >= passing_score
        
        # Performance by domain percentages
        domain_percentages = {}
        for domain, perf in domain_performance.items():
            domain_percentages[domain] = (perf["correct"] / perf["total"]) * 100 if perf["total"] > 0 else 0
        
        # Mark session as completed
        session["completed"] = True
        session["end_time"] = end_time
        
        results = {
            "session_id": session["session_id"],
            "score": score_percentage,
            "correct_answers": correct_answers,
            "total_questions": total_questions,
            "answered_questions": answered_questions,
            "completion_rate": completion_rate,
            "time_taken_minutes": time_taken_minutes,
            "passed": passed,
            "passing_score": passing_score,
            "domain_performance": domain_percentages,
            "difficulty_performance": difficulty_performance,
            "detailed_results": detailed_results,
            "mode": session["mode"],
            "recommendations": self._generate_recommendations(domain_percentages, difficulty_performance)
        }
        
        # Store results
        self.session_stats[session["session_id"]] = results
        
        # Persist to database
        self.save_quiz_results(results, session)
        
        return results
    
    def save_quiz_results(self, results: Dict[str, Any], session: Dict[str, Any]):
        """Save quiz results to database using shared database manager"""
        try:
            # Determine user context
            user_id = None
            user_type = "anonymous"
            
            if self.auth_manager and self.auth_manager.is_logged_in():
                user_id = self.auth_manager.current_user["user_id"]
                user_type = "authenticated"
            
            # Prepare main results data
            quiz_data = {
                "session_id": session["session_id"],
                "user_id": user_id,
                "user_type": user_type,
                "quiz_mode": session.get("mode", "practice"),
                "domain_focus": session.get("domain", "Mixed"),
                "difficulty_level": session.get("difficulty", "Mixed"),
                "total_questions": results["total_questions"],
                "correct_answers": results["correct_answers"],
                "answered_questions": results.get("answered_questions", results["total_questions"]),
                "completion_rate": results.get("completion_rate", 100.0),
                "score": results["score"],
                "passed": results["passed"],
                "time_taken_minutes": results.get("time_taken_minutes", 0),
                "performance_data": json.dumps({
                    "domain_performance": results.get("domain_performance", {}),
                    "difficulty_performance": results.get("difficulty_performance", {}),
                    "completion_rate": results.get("completion_rate", 0)
                }),
                "recommendations": json.dumps(results.get("recommendations", [])),
                "detailed_answers": json.dumps(results.get("detailed_results", []))
            }
            
            # Save main quiz results
            quiz_result_id = self.db_manager.insert_record("quiz_results", quiz_data)
            
            # Save detailed question responses
            responses_data = []
            for result in results.get("detailed_results", []):
                response_data = {
                    "session_id": session["session_id"],
                    "question_index": result["question_index"],
                    "question_text": result["question"],
                    "user_answer": result.get("user_answer"),
                    "correct_answer": result["correct_answer"],
                    "is_correct": result["is_correct"],
                    "domain": result.get("domain", "Unknown"),
                    "difficulty": result.get("difficulty", "Unknown"),
                    "time_taken_seconds": result.get("time_taken", 0)
                }
                responses_data.append(response_data)
            
            # Batch insert responses
            if responses_data:
                response_columns = list(responses_data[0].keys())
                placeholders = ['?' for _ in response_columns]
                query = f"""
                    INSERT INTO quiz_responses ({', '.join(response_columns)}) 
                    VALUES ({', '.join(placeholders)})
                """
                
                response_tuples = [tuple(response.values()) for response in responses_data]
                self.db_manager.execute_many(query, response_tuples)
            
            print(f"✅ Quiz results saved to database (User: {user_type}, Score: {results['score']:.1f}%)")
            
        except Exception as e:
            print(f"❌ Error saving quiz results: {e}")
            print(f"Results: {results}")
            print(f"Session: {session}")
    
    def _generate_recommendations(self, domain_performance: Dict[str, float], difficulty_performance: Dict[str, Dict]) -> List[str]:
        """Generate personalized study recommendations based on performance"""
        recommendations = []
        
        # Domain-based recommendations
        weak_domains = [domain for domain, score in domain_performance.items() if score < 70]
        if weak_domains:
            recommendations.append(f"📚 Focus on these domains: {', '.join(weak_domains)}")
        
        # Difficulty-based recommendations  
        for difficulty, perf in difficulty_performance.items():
            if perf["total"] > 0:
                percentage = (perf["correct"] / perf["total"]) * 100
                if percentage < 60:
                    recommendations.append(f"⚡ Practice more {difficulty.lower()} questions")
        
        # General recommendations
        overall_score = sum(domain_performance.values()) / len(domain_performance) if domain_performance else 0
        
        if overall_score >= 90:
            recommendations.append("🎉 Excellent performance! You're ready for the AIGP exam.")
        elif overall_score >= 80:
            recommendations.append("👍 Good progress! Review weak areas and take more practice exams.")
        elif overall_score >= 70:
            recommendations.append("📖 You're on track! Focus on understanding explanations and key concepts.")
        else:
            recommendations.append("📚 More study needed. Review fundamental concepts and retake quizzes.")
        
        return recommendations
    
    def get_quiz_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics from database using shared database manager"""
        try:
            # Determine filtering based on user status
            if self.auth_manager and self.auth_manager.is_logged_in():
                # Get stats for logged-in user
                where_clause = "user_id = ?"
                where_params = (self.auth_manager.current_user["user_id"],)
                limit = None
            else:
                # Get general anonymous stats (last 50 sessions for performance)
                where_clause = "user_type = 'anonymous'"
                where_params = ()
                limit = 50
            
            # Get records using shared database manager
            records = self.db_manager.get_records(
                table="quiz_results",
                where_clause=where_clause,
                where_params=where_params,
                order_by="created_at DESC",
                limit=limit
            )
            
            if not records:
                return {"message": "No quiz history available"}
            
            # Calculate statistics
            total_quizzes = len(records)
            
            # Safe conversion with error handling
            scores = []
            total_questions = []
            correct_answers = []
            passed_flags = []
            time_data = []
            
            for record in records:
                try:
                    # Score (column 11)
                    score_val = record[11]
                    if score_val is not None and str(score_val).replace('.', '').replace('-', '').isdigit():
                        scores.append(float(score_val))
                    else:
                        scores.append(0.0)
                    
                    # Total questions (column 7)
                    total_q = record[7]
                    if total_q is not None and str(total_q).isdigit():
                        total_questions.append(int(total_q))
                    else:
                        total_questions.append(0)
                    
                    # Correct answers (column 8)
                    correct_a = record[8]
                    if correct_a is not None and str(correct_a).isdigit():
                        correct_answers.append(int(correct_a))
                    else:
                        correct_answers.append(0)
                    
                    # Passed flag (column 12)
                    passed_val = record[12]
                    if passed_val is not None:
                        if isinstance(passed_val, bool):
                            passed_flags.append(passed_val)
                        elif str(passed_val).lower() in ['true', '1', 'yes']:
                            passed_flags.append(True)
                        else:
                            passed_flags.append(False)
                    else:
                        passed_flags.append(False)
                    
                    # Time data (column 13)
                    time_val = record[13]
                    if time_val is not None and str(time_val).replace('.', '').replace('-', '').isdigit():
                        time_data.append(float(time_val))
                        
                except (ValueError, IndexError, TypeError) as e:
                    print(f"⚠️ Warning: Error processing quiz record: {e}")
                    continue
            
            # Calculate aggregated stats
            average_score = sum(scores) / len(scores) if scores else 0
            best_score = max(scores) if scores else 0
            latest_score = scores[0] if scores else 0  # First record is latest due to ORDER BY DESC
            
            total_questions_answered = sum(total_questions) if total_questions else 0
            passed_count = sum(1 for p in passed_flags if p)
            pass_rate = (passed_count / total_quizzes * 100) if total_quizzes > 0 else 0
            
            # Average time calculation
            average_time = sum(time_data) / len(time_data) if time_data else 0
            
            return {
                "total_quizzes": total_quizzes,
                "average_score": average_score,
                "best_score": best_score,
                "latest_score": latest_score,
                "pass_rate": pass_rate,
                "total_questions_answered": total_questions_answered,
                "average_time_per_quiz": average_time
            }
            
        except Exception as e:
            print(f"❌ Error loading quiz statistics: {e}")
            return {"message": "Error loading quiz history"}
    
    def create_performance_charts(self, results: Dict[str, Any]) -> Tuple[go.Figure, go.Figure]:
        """Create performance visualization charts"""
        
        # Domain performance chart
        domain_perf = results["domain_performance"]
        domain_fig = px.bar(
            x=list(domain_perf.keys()),
            y=list(domain_perf.values()),
            title="Performance by Domain",
            labels={"x": "Domain", "y": "Score (%)"},
            color=list(domain_perf.values()),
            color_continuous_scale="RdYlGn"
        )
        domain_fig.update_layout(showlegend=False, height=400)
        domain_fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Passing Score (70%)")
        
        # Score distribution chart if multiple sessions
        if len(self.session_stats) > 1:
            session_scores = [(i+1, result["score"]) for i, result in enumerate(self.session_stats.values())]
            score_fig = px.line(
                x=[s[0] for s in session_scores],
                y=[s[1] for s in session_scores],
                title="Score Progression Over Time",
                labels={"x": "Quiz Session", "y": "Score (%)"},
                markers=True
            )
            score_fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Passing Score")
        else:
            # Single session - show question-by-question performance
            correct_answers = [1 if result["is_correct"] else 0 for result in results["detailed_results"]]
            cumulative_score = []
            running_total = 0
            for i, correct in enumerate(correct_answers):
                running_total += correct
                cumulative_score.append((running_total / (i + 1)) * 100)
            
            score_fig = px.line(
                x=list(range(1, len(cumulative_score) + 1)),
                y=cumulative_score,
                title="Cumulative Score Throughout Quiz",
                labels={"x": "Question Number", "y": "Cumulative Score (%)"},
                markers=True
            )
            score_fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Passing Score")
        
        score_fig.update_layout(height=400)
        
        return domain_fig, score_fig
    
    def submit_bulk_answers(self, answers_dict: Dict[int, int]) -> bool:
        """Submit multiple answers at once"""
        if not self.current_quiz_session or self.current_quiz_session["completed"]:
            return False
        
        for question_index, answer_index in answers_dict.items():
            self.current_quiz_session["answers"][question_index] = answer_index
        
        return True
    
    def get_quiz_summary(self) -> Dict[str, Any]:
        """Get a summary of the current quiz session"""
        if not self.current_quiz_session:
            return {"error": "No active session"}
        
        session = self.current_quiz_session
        return {
            "session_id": session["session_id"],
            "mode": session["mode"],
            "total_questions": len(session["questions"]),
            "answered_questions": len(session["answers"]),
            "domain": session.get("domain", "Mixed"),
            "difficulty": session.get("difficulty", "Mixed"),
            "time_limit": session.get("time_limit_minutes"),
            "start_time": session["start_time"].isoformat(),
            "completed": session["completed"]
        }
    
    def reset_session(self):
        """Reset current quiz session"""
        self.current_quiz_session = None
    
    def get_available_domains(self) -> List[str]:
        """Get list of available domains from quiz data"""
        domains = set()
        for question in self.quiz_data["questions"]:
            domains.add(question.get("domain", "Unknown"))
        return sorted(list(domains))
    
    def get_available_difficulties(self) -> List[str]:
        """Get list of available difficulty levels"""
        difficulties = set()
        for question in self.quiz_data["questions"]:
            difficulties.add(question.get("difficulty", "Unknown"))
        return sorted(list(difficulties))
    
    def create_interface(self):
        """Create the comprehensive quiz interface"""
        
        gr.Markdown("## 🧪 AIGP Mock Examination Center")
        gr.Markdown("Advanced practice system with comprehensive question bank and detailed analytics.")
        
        with gr.Tabs():
            # Quiz Setup Tab
            with gr.Tab("🎯 Quiz Setup") as setup_tab:
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 📋 Quiz Configuration")
                        
                        quiz_mode = gr.Radio(
                            choices=["quick_practice", "domain_focus", "exam_simulation"],
                            value="quick_practice",
                            label="🎯 Quiz Mode",
                            info="• Quick Practice: Fast review sessions\n• Domain Focus: Target specific areas\n• Exam Simulation: Full AIGP exam experience"
                        )
                        
                        num_questions = gr.Slider(
                            minimum=5,
                            maximum=50,
                            value=10,
                            step=1,
                            label="📊 Number of Questions",
                            info="Your selected count will be respected (exam simulation capped at 50)"
                        )
                        
                        difficulty_level = gr.Dropdown(
                            choices=["Mixed"] + self.get_available_difficulties(),
                            value="Mixed",
                            label="⚡ Difficulty Level",
                            info="Mixed = Random difficulty for varied practice"
                        )
                        
                        domain_focus = gr.Dropdown(
                            choices=["Mixed"] + self.get_available_domains(),
                            value="Mixed",
                            label="🎯 Domain Focus",
                            info="Mixed = Questions from all AIGP domains"
                        )
                        
                        time_limit = gr.Slider(
                            minimum=0,
                            maximum=120,
                            value=15,
                            step=5,
                            label="⏱️ Time Limit (minutes)",
                            info="Set to 0 for unlimited time • Your choice will be respected"
                        )
                        
                        start_quiz_btn = gr.Button("🚀 Start Quiz", variant="primary", size="lg")
                    
                    with gr.Column():
                        gr.Markdown("### 🎯 Quiz Preview")
                        quiz_preview = gr.HTML(self._generate_quiz_preview())
                        
                        gr.Markdown("### 📊 Your Performance Statistics")
                        stats_display = gr.HTML(self._generate_stats_html())
                        refresh_stats_btn = gr.Button("🔄 Refresh Stats", size="sm")
            
            # Quiz Taking Tab  
            with gr.Tab("📝 Take Quiz") as quiz_tab:
                quiz_container = gr.HTML(self._generate_welcome_html())
                quiz_state = gr.State({"session_id": None, "state": "inactive"})  # Initialize with structured state
                quiz_answers = gr.State({"answers": {}})  # Initialize with empty answers dict
                
                with gr.Row():
                    submit_answer_btn = gr.Button(
                        "💾 Save Progress",
                        variant="secondary",
                        visible=False
                    )
                    submit_quiz_btn = gr.Button(
                        "📤 Submit Quiz",
                        variant="primary",
                        visible=False
                    )
                
                quiz_timer = gr.HTML(
                    value="",
                    visible=False
                )
            
            # Results Tab
            with gr.Tab("📊 Results & Analytics") as results_tab:
                results_container = gr.HTML(self._generate_no_results_html())
                
                with gr.Row():
                    with gr.Column():
                        domain_chart = gr.Plot(label="📊 Performance by Domain")
                    with gr.Column():
                        progress_chart = gr.Plot(label="📈 Score Progression")
                
                detailed_feedback = gr.HTML("")
                recommendations_display = gr.HTML("")
                
                new_quiz_btn = gr.Button("🔄 Start New Quiz", variant="primary")
        
        # Event Handlers
        def start_quiz(mode, num_q, difficulty, domain, time_limit_min):
            """Initialize a new quiz session"""
            session = self.generate_quiz_session(
                mode=mode,
                num_questions=num_q,
                difficulty=difficulty,
                domain=domain,
                time_limit=time_limit_min if time_limit_min > 0 else None
            )
            
            if "error" in session:
                return (
                    f"<div style='color: red;'>❌ {session['error']}</div>",
                    {"session_id": None, "state": "error"},
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(visible=False, value="")
                )
            
            return (
                self._generate_quiz_html(session),
                {"session_id": session.get("id"), "state": "active"},
                gr.update(visible=True),
                gr.update(visible=True),
                gr.update(visible=True, value=self._generate_timer_html(session))
            )
        
        def submit_quiz(session_state, answers):
            """Submit quiz answers and generate results"""
            if not session_state or not isinstance(session_state, dict):
                return (
                    "<div style='color: red;'>❌ No active quiz session</div>",
                    "",
                    None,
                    None,
                    "",
                    "",
                    {"answers": {}},
                    {"session_id": None, "state": "inactive"}
                )
            
            session_id = session_state.get("session_id")
            if not session_id:
                return (
                    "<div style='color: red;'>❌ Invalid quiz session</div>",
                    "",
                    None,
                    None,
                    "",
                    "",
                    {"answers": {}},
                    {"session_id": None, "state": "error"}
                )
            
            results = self.calculate_quiz_results()
            quiz_results_html = self._generate_quiz_results_html(session_state, results)
            results_html = self._generate_results_html(results)
            
            domain_fig = self._generate_domain_performance_chart(results)
            progress_fig = self._generate_progress_chart()
            
            # Generate detailed feedback
            feedback_html = self._generate_detailed_feedback_html(results)
            recommendations_html = self._generate_recommendations_html(results)
            
            return (
                quiz_results_html,
                results_html,
                domain_fig,
                progress_fig,
                feedback_html,
                recommendations_html,
                {"answers": {}},
                {"session_id": None, "state": "inactive"}
            )
        
        def refresh_statistics():
            """Refresh performance statistics"""
            return self._generate_stats_html()
        
        def start_new_quiz():
            """Reset to start a new quiz"""
            self.reset_session()
            return (
                self._generate_welcome_html(),  # Reset quiz container
                "",                            # Reset results
                {"session_id": None, "state": "inactive"},  # Reset session with structured state
                gr.update(visible=False),  # Hide submit answer
                gr.update(visible=False),  # Hide submit quiz
                gr.update(visible=False, value=""),  # Hide timer
                "",                            # Reset feedback
                "",                            # Reset recommendations
                None,                          # Reset domain chart
                None                           # Reset progress chart
            )
        
        # Wire up event handlers
        start_quiz_btn.click(
            fn=start_quiz,
            inputs=[quiz_mode, num_questions, difficulty_level, domain_focus, time_limit],
            outputs=[quiz_container, quiz_state, submit_answer_btn, submit_quiz_btn, quiz_timer]
        )
        
        submit_quiz_btn.click(
            fn=submit_quiz,
            inputs=[quiz_state, quiz_answers],
            outputs=[quiz_container, results_container, domain_chart, progress_chart, detailed_feedback, recommendations_display, quiz_answers, quiz_state]
        )
        
        refresh_stats_btn.click(
            fn=refresh_statistics,
            outputs=[stats_display]
        )
        
        new_quiz_btn.click(
            fn=start_new_quiz,
            outputs=[quiz_container, results_container, quiz_state, submit_answer_btn, submit_quiz_btn, quiz_timer, 
                    detailed_feedback, recommendations_display, domain_chart, progress_chart]
        )
        
        # Dynamic preview updates
        def update_preview(mode, num_q, difficulty, domain, time_limit_min):
            """Update quiz preview when parameters change"""
            return self._generate_quiz_preview(mode, num_q, difficulty, domain, time_limit_min)
        
        # Wire up preview updates to all parameter changes
        for component in [quiz_mode, num_questions, difficulty_level, domain_focus, time_limit]:
            component.change(
                fn=update_preview,
                inputs=[quiz_mode, num_questions, difficulty_level, domain_focus, time_limit],
                outputs=[quiz_preview]
            )
        
        return quiz_container, results_container
    
    def _generate_quiz_preview(self, mode="quick_practice", num_q=10, difficulty="Mixed", domain="Mixed", time_limit=15) -> str:
        """Generate preview HTML showing what quiz will be created"""
        
        # Count available questions for criteria
        available_questions = len(self.get_questions_by_criteria(
            domain=domain if domain != "Mixed" else None,
            difficulty=difficulty if difficulty != "Mixed" else None,
            limit=None  # Get all to count
        ))
        
        # Calculate actual parameters that will be used
        actual_questions = min(num_q, available_questions) if available_questions > 0 else 0
        actual_time = time_limit if time_limit > 0 else "Unlimited"
        
        # Mode-specific adjustments
        mode_info = ""
        if mode == "exam_simulation":
            exam_max = self.quiz_data["exam_simulation_settings"]["standard_exam"]["total_questions"]
            if num_q > exam_max:
                actual_questions = exam_max
                mode_info = f"<br>⚠️ Capped at {exam_max} for exam simulation"
        
        # Status indicators
        questions_status = "✅" if actual_questions > 0 else "❌"
        time_status = "⏱️" if actual_time != "Unlimited" else "♾️"
        
        return f"""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                    padding: 1.5rem; border-radius: 12px; border: 2px solid #3b82f6; color: white;">
            <h4 style="color: #60a5fa; margin-top: 0; margin-bottom: 1rem;">🎯 Your Quiz Configuration</h4>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                <div style="background: rgba(59, 130, 246, 0.1); padding: 0.8rem; border-radius: 8px; border: 1px solid #3b82f6;">
                    <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 0.3rem;">Mode</div>
                    <div style="font-weight: bold; color: #e2e8f0;">{mode.replace('_', ' ').title()}</div>
                </div>
                
                <div style="background: rgba(16, 185, 129, 0.1); padding: 0.8rem; border-radius: 8px; border: 1px solid #10b981;">
                    <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 0.3rem;">Questions</div>
                    <div style="font-weight: bold; color: #e2e8f0;">{questions_status} {actual_questions} / {available_questions} available</div>
                </div>
                
                <div style="background: rgba(245, 158, 11, 0.1); padding: 0.8rem; border-radius: 8px; border: 1px solid #f59e0b;">
                    <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 0.3rem;">Difficulty</div>
                    <div style="font-weight: bold; color: #e2e8f0;">{difficulty}</div>
                </div>
                
                <div style="background: rgba(139, 92, 246, 0.1); padding: 0.8rem; border-radius: 8px; border: 1px solid #8b5cf6;">
                    <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 0.3rem;">Domain</div>
                    <div style="font-weight: bold; color: #e2e8f0;">{domain}</div>
                </div>
                
                <div style="background: rgba(236, 72, 153, 0.1); padding: 0.8rem; border-radius: 8px; border: 1px solid #ec4899; grid-column: span 2;">
                    <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 0.3rem;">Time Limit</div>
                    <div style="font-weight: bold; color: #e2e8f0;">{time_status} {actual_time} {'minutes' if actual_time != 'Unlimited' else ''}</div>
                </div>
            </div>
            
            {mode_info}
            
            <div style="margin-top: 1rem; padding: 0.8rem; background: rgba(34, 197, 94, 0.1); 
                        border-radius: 8px; border-left: 4px solid #22c55e;">
                <div style="font-size: 0.9rem; color: #86efac;">
                    ✨ <strong>Ready to start!</strong> Your parameters will be respected exactly as configured.
                </div>
            </div>
        </div>
        """
    
    def _generate_stats_html(self) -> str:
        """Generate HTML for performance statistics"""
        stats = self.get_quiz_statistics()
        
        if "message" in stats:
            return f"""
            <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 10px; text-align: center; border: 2px solid #3b82f6;">
                <h4 style="color: #60a5fa;">📊 Performance Statistics</h4>
                <p style="color: #d1d5db;">{stats["message"]}</p>
                <p style="font-size: 0.9rem; color: #9ca3af;">Take a quiz to see your statistics here!</p>
            </div>
            """
        
        return f"""
        <div style="background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%); 
                    color: white; padding: 1.5rem; border-radius: 12px;">
            <h4 style="color: #fbbf24; margin-top: 0;">📊 Your Performance</h4>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 1rem;">
                <div style="text-align: center; background: rgba(255,255,255,0.1); padding: 0.8rem; border-radius: 8px;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #fbbf24;">{stats["average_score"]:.1f}%</div>
                    <div style="font-size: 0.9rem;">Average Score</div>
                </div>
                <div style="text-align: center; background: rgba(255,255,255,0.1); padding: 0.8rem; border-radius: 8px;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #fbbf24;">{stats["total_quizzes"]}</div>
                    <div style="font-size: 0.9rem;">Quizzes Taken</div>
                </div>
                <div style="text-align: center; background: rgba(255,255,255,0.1); padding: 0.8rem; border-radius: 8px;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #fbbf24;">{stats["best_score"]:.1f}%</div>
                    <div style="font-size: 0.9rem;">Best Score</div>
                </div>
                <div style="text-align: center; background: rgba(255,255,255,0.1); padding: 0.8rem; border-radius: 8px;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #fbbf24;">{stats["pass_rate"]:.1f}%</div>
                    <div style="font-size: 0.9rem;">Pass Rate</div>
                </div>
            </div>
        </div>
        """
    
    def _generate_welcome_html(self) -> str:
        """Generate welcome HTML for quiz tab"""
        return """
        <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%); 
                    border-radius: 15px; margin: 1rem 0; border: 2px solid #3b82f6;">
            <h2 style="color: #60a5fa; margin-bottom: 1rem;">🎯 Ready to Test Your AIGP Knowledge?</h2>
            <p style="color: #d1d5db; font-size: 1.1rem; margin-bottom: 2rem;">
                Configure your quiz in the Setup tab and click "Start Quiz" to begin your practice session.
            </p>
            <div style="background: #065f46; padding: 1rem; border-radius: 8px; display: inline-block; border: 1px solid #10b981;">
                <strong style="color: #10b981;">💡 Tip:</strong> 
                <span style="color: #d1fae5;">Choose "exam_simulation" mode for the most realistic AIGP exam experience!</span>
            </div>
        </div>
        """
    
    def _generate_no_results_html(self) -> str:
        """Generate HTML for empty results tab"""
        return """
        <div style="text-align: center; padding: 2rem; color: #d1d5db; background: #1a1a1a; border-radius: 12px; border: 2px solid #3b82f6;">
            <h3 style="color: #60a5fa;">📈 Quiz Results Will Appear Here</h3>
            <p>Complete a quiz to see detailed results, performance analytics, and personalized recommendations.</p>
        </div>
        """
    
    def _generate_quiz_html(self, session: Dict[str, Any]) -> str:
        """Generate the quiz HTML with proper state management"""
        if not session or not isinstance(session, dict):
            return self._generate_welcome_html()
            
        questions = session.get("questions", [])
        if not questions:
            return "<div class='error'>No questions available</div>"
            
        quiz_html = """
        <div class="quiz-container">
            <div class="quiz-header">
                <h3>🧪 AIGP Mock Exam</h3>
                <div class="quiz-meta">
                    <span class="quiz-count">Questions: """ + str(len(questions)) + """</span>
                    <span class="quiz-mode">Mode: """ + session.get("mode", "practice").replace("_", " ").title() + """</span>
                    <span class="quiz-difficulty">Level: """ + session.get("difficulty", "Mixed") + """</span>
                </div>
            </div>
            
            <div id="quiz-progress" class="quiz-progress">
                Progress: 0/""" + str(len(questions)) + """ (0%)
            </div>
            
            <div class="questions-container">
        """
        
        for i, q in enumerate(questions):
            quiz_html += f"""
            <div class="question" id="question-{i}">
                <h4>Question {i + 1}</h4>
                <p class="question-text">{q['question']}</p>
                <div class="options-container">
            """
            
            for j, option in enumerate(q['options']):
                quiz_html += f"""
                <div class="option" onclick="updateAnswer({i}, {j})">
                    <input type="radio" name="q{i}" id="q{i}o{j}" value="{j}">
                    <label for="q{i}o{j}">{chr(65 + j)}) {option}</label>
                </div>
                """
            
            quiz_html += """
                </div>
            </div>
            """
        
        quiz_html += """
        </div>
        <script>
        (function() {
            let quizState = {
                answers: {},
                timeStarted: Date.now(),
                completed: false
            };
            
            window.updateAnswer = function(questionIndex, answerIndex) {
                quizState.answers[questionIndex] = answerIndex;
                updateProgress();
                notifyGradio();
            };
            
            function updateProgress() {
                const total = """ + str(len(questions)) + """;
                const answered = Object.keys(quizState.answers).length;
                const percent = Math.round((answered / total) * 100);
                
                document.getElementById('quiz-progress').innerHTML = 
                    `Progress: ${answered}/${total} (${percent}%)`;
            }
            
            function notifyGradio() {
                // Use Gradio's custom events to update state
                document.dispatchEvent(new CustomEvent('quiz-state-update', {
                    detail: {
                        answers: quizState.answers,
                        timeStarted: quizState.timeStarted,
                        completed: quizState.completed
                    }
                }));
            }
            
            // Initialize
            updateProgress();
        })();
        </script>
        """
        
        return quiz_html
    
    def _generate_timer_html(self, session: Dict[str, Any]) -> str:
        """Generate timer HTML with proper state handling"""
        if not session or not isinstance(session, dict):
            return ""
            
        time_limit = session.get("time_limit_minutes")
        if not time_limit:
            return ""
            
        return f"""
        <div id="quiz-timer" class="quiz-timer">
            Time Remaining: {time_limit}:00
        </div>
        <script>
        (function() {{
            const timeLimit = {time_limit} * 60;
            let timeLeft = timeLimit;
            
            function updateTimer() {{
                const minutes = Math.floor(timeLeft / 60);
                const seconds = timeLeft % 60;
                document.getElementById('quiz-timer').innerHTML = 
                    `Time Remaining: ${{minutes}}:${{seconds.toString().padStart(2, '0')}}`;
                    
                if (timeLeft <= 0) {{
                    clearInterval(timerInterval);
                    document.dispatchEvent(new CustomEvent('quiz-timeout'));
                }}
                timeLeft--;
            }}
            
            const timerInterval = setInterval(updateTimer, 1000);
            updateTimer();
        }})();
        </script>
        """
    
    def _generate_quiz_results_html(self, session: Dict[str, Any], results: Dict[str, Any]) -> str:
        """Generate HTML for quiz questions with results overlaid"""
        questions = session["questions"]
        answers = session["answers"]
        score = results["score"]
        
        # Determine score color and message
        if score >= 90:
            score_color = "#059669"
            message = "Outstanding! 🎉"
        elif score >= 80:
            score_color = "#3b82f6"
            message = "Excellent work! 👏"
        elif score >= 70:
            score_color = "#f59e0b"
            message = "Good job! ✅"
        else:
            score_color = "#dc2626"
            message = "Keep studying! 📚"
        
        quiz_html = f"""
        <div style="background: #1a1a1a; padding: 2rem; border-radius: 15px; border: 2px solid {score_color}; color: #ffffff;">
            <!-- Results Header -->
            <div style="background: linear-gradient(135deg, {score_color} 0%, {score_color}dd 100%); 
                        color: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; text-align: center;">
                <h2 style="margin: 0 0 0.5rem 0;">{message}</h2>
                <div style="font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">{score:.1f}%</div>
                <p style="font-size: 1.1rem; margin: 0;">
                    {"🎯 Passed!" if results['passed'] else "📖 More study needed"} 
                    ({results['correct_answers']}/{results['total_questions']} correct)
                </p>
            </div>
            
            <!-- Quiz Info -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; 
                        padding-bottom: 1rem; border-bottom: 2px solid #374151;">
                <h3 style="margin: 0; color: #60a5fa;">📝 Quiz Review</h3>
                <div style="display: flex; gap: 1rem;">
                    <div style="background: #3b82f6; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;">
                        {len(questions)} Questions
                    </div>
                    <div style="background: #059669; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;">
                        {session.get('difficulty', 'Mixed')} Level
                    </div>
                    <div style="background: #7c3aed; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;">
                        {session.get('mode', 'practice').replace('_', ' ').title()}
                    </div>
                </div>
            </div>
        """
        
        # Questions with results
        for i, q in enumerate(questions):
            category_color = self._get_category_color(q.get("domain", "Unknown"))
            user_answer = answers.get(i, -1)
            correct_answer = q["correct"]
            is_correct = user_answer == correct_answer
            
            # Question result styling
            if is_correct:
                result_icon = "✅"
                result_color = "#059669"
                result_bg = "#065f46"
            else:
                result_icon = "❌"
                result_color = "#dc2626"
                result_bg = "#7f1d1d"
            
            quiz_html += f"""
            <div style="margin-bottom: 2rem; padding: 1.5rem; background: #262626; border-radius: 10px; 
                        border-left: 5px solid {result_color}; border: 2px solid {result_color};">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <h4 style="margin: 0; color: #e5e7eb; flex-grow: 1;">
                        {result_icon} Question {i+1}: {q['question']}
                    </h4>
                    <div style="margin-left: 1rem; text-align: right;">
                        <div style="background: {category_color}; color: white; padding: 0.2rem 0.5rem; 
                                    border-radius: 4px; font-size: 0.8rem; margin-bottom: 0.3rem;">
                            {q.get('domain', 'Unknown')}
                        </div>
                        <div style="font-size: 0.8rem; color: #9ca3af;">
                            {q.get('difficulty', 'Unknown')} | {q.get('type', 'Multiple Choice')}
                        </div>
                    </div>
                </div>
                
                <div style="margin-left: 1rem;">
            """
            
            # Show all options with styling
            for j, option in enumerate(q['options']):
                is_user_choice = j == user_answer
                is_correct_answer = j == correct_answer
                
                # Determine styling for each option
                if is_correct_answer and is_user_choice:
                    # User chose correct answer
                    option_style = f"""
                        background: #065f46; border: 2px solid #10b981; color: #d1fae5;
                        box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
                    """
                    option_icon = "✅"
                elif is_correct_answer:
                    # Correct answer (user didn't choose)
                    option_style = f"""
                        background: #065f46; border: 2px solid #10b981; color: #d1fae5;
                    """
                    option_icon = "✓"
                elif is_user_choice:
                    # User's wrong choice
                    option_style = f"""
                        background: #7f1d1d; border: 2px solid #dc2626; color: #fecaca;
                    """
                    option_icon = "❌"
                else:
                    # Regular option
                    option_style = f"""
                        background: #374151; border: 1px solid #4b5563; color: #d1d5db;
                    """
                    option_icon = ""
                
                quiz_html += f"""
                    <div style="margin: 0.8rem 0;">
                        <div style="display: flex; align-items: center; padding: 0.8rem; 
                                   border-radius: 8px; {option_style}">
                            <span style="font-size: 1rem; line-height: 1.4; font-weight: {'bold' if (is_correct_answer or is_user_choice) else 'normal'};">
                                {option_icon} {chr(65+j)}) {option}
                            </span>
                        </div>
                    </div>
                """
            
            # Add explanation if available
            if q.get("explanation"):
                quiz_html += f"""
                    <div style="margin-top: 1rem; padding: 1rem; background: #374151; border-radius: 8px; 
                               border-left: 4px solid #3b82f6;">
                        <strong style="color: #60a5fa;">💡 Explanation:</strong>
                        <p style="margin: 0.5rem 0 0 0; color: #d1d5db; line-height: 1.5;">{q['explanation']}</p>
                    </div>
                """
            
            quiz_html += """
                </div>
            </div>
            """
        
        # Add action buttons
        quiz_html += f"""
            <div style="text-align: center; margin-top: 2rem; padding-top: 2rem; border-top: 2px solid #374151;">
                <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                    <button onclick="window.scrollTo(0, 0)" 
                            style="background: #3b82f6; color: white; border: none; padding: 0.8rem 1.5rem; 
                                   border-radius: 8px; cursor: pointer; font-weight: bold;">
                        📊 Back to Top
                    </button>
                    <button onclick="location.reload()" 
                            style="background: #059669; color: white; border: none; padding: 0.8rem 1.5rem; 
                                   border-radius: 8px; cursor: pointer; font-weight: bold;">
                        🔄 Take New Quiz
                    </button>
                </div>
                
                <!-- Legend -->
                <div style="margin-top: 1.5rem; padding: 1rem; background: #374151; border-radius: 8px;">
                    <h4 style="color: #60a5fa; margin: 0 0 0.5rem 0;">🔍 Answer Key:</h4>
                    <div style="display: flex; gap: 1.5rem; justify-content: center; flex-wrap: wrap; font-size: 0.9rem;">
                        <span style="color: #d1fae5;">✅ Your correct answer</span>
                        <span style="color: #d1fae5;">✓ Correct answer</span>
                        <span style="color: #fecaca;">❌ Your incorrect choice</span>
                        <span style="color: #d1d5db;">Regular option</span>
                    </div>
                </div>
            </div>
        </div>
        """
        
        return quiz_html
    
    def _generate_results_html(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive results HTML"""
        score = results["score"]
        passed = results["passed"]
        
        # Determine score color and message
        if score >= 90:
            score_color = "#059669"
            message = "Outstanding! 🎉"
        elif score >= 80:
            score_color = "#3b82f6"
            message = "Excellent work! 👏"
        elif score >= 70:
            score_color = "#f59e0b"
            message = "Good job! ✅"
        else:
            score_color = "#dc2626"
            message = "Keep studying! 📚"
        
        return f"""
        <div style="background: linear-gradient(135deg, {score_color} 0%, {score_color}dd 100%); 
                    color: white; padding: 2rem; border-radius: 15px; margin-bottom: 1.5rem; text-align: center;">
            <h2 style="margin: 0 0 1rem 0;">{message}</h2>
            <div style="font-size: 3rem; font-weight: bold; margin: 1rem 0;">{score:.1f}%</div>
            <p style="font-size: 1.2rem; margin: 0;">
                {"🎯 Passed!" if passed else "📖 More study needed"} 
                ({results['correct_answers']}/{results['total_questions']} correct)
            </p>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                    gap: 1rem; margin: 1.5rem 0;">
            <div style="background: #1e3a8a; padding: 1rem; border-radius: 10px; text-align: center; border: 1px solid #3b82f6;">
                <div style="font-size: 1.5rem; font-weight: bold; color: #60a5fa;">
                    {results['correct_answers']}/{results['total_questions']}
                </div>
                <div style="color: #d1d5db;">Correct Answers</div>
            </div>
            <div style="background: #065f46; padding: 1rem; border-radius: 10px; text-align: center; border: 1px solid #10b981;">
                <div style="font-size: 1.5rem; font-weight: bold; color: #10b981;">
                    {results['time_taken_minutes']:.1f} min
                </div>
                <div style="color: #d1d5db;">Time Taken</div>
            </div>
            <div style="background: #92400e; padding: 1rem; border-radius: 10px; text-align: center; border: 1px solid #f59e0b;">
                <div style="font-size: 1.5rem; font-weight: bold; color: #fbbf24;">
                    {results['completion_rate']:.1f}%
                </div>
                <div style="color: #d1d5db;">Completion Rate</div>
            </div>
            <div style="background: #831843; padding: 1rem; border-radius: 10px; text-align: center; border: 1px solid #ec4899;">
                <div style="font-size: 1.5rem; font-weight: bold; color: #f9a8d4;">
                    {results['mode'].replace('_', ' ').title()}
                </div>
                <div style="color: #d1d5db;">Quiz Mode</div>
            </div>
        </div>
        """
    
    def _generate_detailed_feedback_html(self, results: Dict[str, Any]) -> str:
        """Generate detailed question-by-question feedback"""
        feedback_html = """
        <div style="background: #1a1a1a; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; border: 2px solid #3b82f6;">
            <h4 style="color: #60a5fa; margin-top: 0;">📝 Detailed Question Review</h4>
        """
        
        for i, result in enumerate(results["detailed_results"]):
            icon = "✅" if result["is_correct"] else "❌"
            border_color = "#059669" if result["is_correct"] else "#dc2626"
            
            feedback_html += f"""
            <div style="border-left: 4px solid {border_color}; padding: 1rem; margin: 1rem 0; 
                        background: #262626; border-radius: 4px; border: 1px solid #4b5563;">
                <h5 style="margin: 0 0 0.5rem 0; color: #e5e7eb;">
                    {icon} Question {i+1}: {result["question"]}
                </h5>
                <p style="margin: 0.5rem 0; color: #d1d5db;">
                    <strong>Your answer:</strong> {result["user_answer"]}
                </p>
                <p style="margin: 0.5rem 0; color: #d1d5db;">
                    <strong>Correct answer:</strong> {result["correct_answer"]}
                </p>
                <div style="background: #374151; padding: 0.8rem; border-radius: 6px; margin: 0.5rem 0; border: 1px solid #4b5563;">
                    <strong style="color: #60a5fa;">Explanation:</strong>
                    <p style="margin: 0.3rem 0 0 0; color: #d1d5db;">{result["explanation"]}</p>
                </div>
                {f'<p style="font-size: 0.9rem; color: #9ca3af; margin: 0.3rem 0;"><strong>Reference:</strong> {result["legal_reference"]}</p>' if result.get("legal_reference") else ''}
            </div>
            """
        
        feedback_html += "</div>"
        return feedback_html
    
    def _generate_recommendations_html(self, results: Dict[str, Any]) -> str:
        """Generate personalized recommendations HTML"""
        recommendations = results.get("recommendations", [])
        
        if not recommendations:
            return ""
        
        rec_html = """
        <div style="background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%); 
                    color: white; padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
            <h4 style="color: #fbbf24; margin-top: 0;">💡 Personalized Study Recommendations</h4>
            <ul style="margin: 0; padding-left: 1.5rem;">
        """
        
        for rec in recommendations:
            rec_html += f"<li style='margin: 0.5rem 0; line-height: 1.4;'>{rec}</li>"
        
        rec_html += "</ul></div>"
        return rec_html
    
    def _get_category_color(self, domain: str) -> str:
        """Get color for domain category"""
        colors = {
            "AI Governance Fundamentals": "#3b82f6",
            "EU AI Act & Regulatory Compliance": "#dc2626", 
            "Risk Management & Assessment": "#f59e0b",
            "Data Governance & Quality": "#059669",
            "Ethics & Bias Mitigation": "#8b5cf6",
            "Technical Implementation": "#0891b2",
            "International Standards & Frameworks": "#6366f1",
            "Organizational Governance": "#be185d"
        }
        return colors.get(domain, "#6b7280")
    
    def _generate_interactive_quiz_components(self, session: Dict[str, Any]) -> Tuple[List[gr.Radio], gr.HTML]:
        """Generate interactive quiz using Gradio components for proper answer capture"""
        questions = session["questions"]
        
        # Create header HTML
        header_html = f"""
        <div style="background: #1a1a1a; padding: 2rem; border-radius: 15px; border: 2px solid #3b82f6; color: #ffffff; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; 
                        padding-bottom: 1rem; border-bottom: 2px solid #374151;">
                <h3 style="margin: 0; color: #60a5fa;">🧪 AIGP Mock Exam</h3>
                <div style="display: flex; gap: 1rem;">
                    <div style="background: #3b82f6; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;">
                        {len(questions)} Questions
                    </div>
                    <div style="background: #059669; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;">
                        {session.get('difficulty', 'Mixed')} Level
                    </div>
                    <div style="background: #7c3aed; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;">
                        {session.get('mode', 'practice').replace('_', ' ').title()}
                    </div>
                </div>
            </div>
            
            <div id="quiz-progress" style="background: #374151; padding: 0.8rem; border-radius: 8px; 
                                          text-align: center; font-weight: bold; color: #d1d5db; border: 1px solid #4b5563;">
                Progress: 0/{len(questions)} (0%)
            </div>
        </div>
        """
        
        # Create radio button components for each question
        radio_components = []
        for i, q in enumerate(questions):
            category_color = self._get_category_color(q.get("domain", "Unknown"))
            
            # Create choices with letters
            choices = [f"{chr(65+j)}) {option}" for j, option in enumerate(q['options'])]
            
            # Create radio component
            radio = gr.Radio(
                choices=choices,
                label=f"Question {i+1}: {q['question']}",
                info=f"Domain: {q.get('domain', 'Unknown')} | Difficulty: {q.get('difficulty', 'Unknown')}",
                value=None
            )
            radio_components.append(radio)
        
        return radio_components, gr.HTML(header_html)
    
    def _create_answer_capture_interface(self):
        """Create a quiz interface with proper answer capture using Gradio components"""
        
        # This will be used in future versions for better answer capture
        # For now, we'll continue with the HTML approach but improve it
        
        # Quiz state
        quiz_session = gr.State(value=None)
        captured_answers = gr.State(value={})
        
        # Quiz container
        quiz_display = gr.HTML("")
        
        # Answer capture mechanism using hidden components
        answer_updater = gr.Button("Update Answers", visible=False)
        
        def update_answer(q_index: int, answer: str, current_answers: dict):
            """Update a single answer in the captured answers"""
            if current_answers is None:
                current_answers = {}
            
            # Extract answer index from choice (e.g., "A) Option" -> 0)
            if answer and answer.startswith(('A)', 'B)', 'C)', 'D)', 'E)')):
                answer_index = ord(answer[0]) - ord('A')
                current_answers[q_index] = answer_index
                print(f"✅ Captured answer for Q{q_index + 1}: {answer} (index: {answer_index})")
            
            return current_answers
        
        return quiz_display, quiz_session, captured_answers 