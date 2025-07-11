#!/usr/bin/env python3
"""
🔐 Authentication Manager for AI Governance Architect's Codex
Comprehensive user management system with role-based access control.

Features:
- User registration and login
- Admin panel for user management
- Session management
- Password hashing and security
- Student portal access control
"""

import sqlite3
import hashlib
import secrets
import gradio as gr
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

from .database_manager import DatabaseManager

class AuthManager:
    def __init__(self, db_path="data/users.db"):
        self.db_path = db_path
        self.session_duration = timedelta(hours=24)  # 24 hour sessions
        self.active_sessions = {}  # In-memory session storage
        self.current_user = None  # Track current logged-in user
        
        # Initialize shared database manager
        self.db_manager = DatabaseManager(db_path)
        
        # Initialize database
        self.init_database()
        
        # Create default admin user
        self.create_default_admin()
    
    def init_database(self):
        """Initialize the user database with required tables using shared database manager"""
        # Users table
        users_schema = """
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            profile_data TEXT DEFAULT '{}'
        """
        
        # Sessions table (for persistent sessions if needed)
        sessions_schema = """
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_token TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        """
        
        # User progress tracking
        progress_schema = """
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            module_id TEXT,
            progress_data TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        """
        
        # Create tables using shared database manager
        self.db_manager.create_table_if_not_exists("users", users_schema)
        self.db_manager.create_table_if_not_exists("sessions", sessions_schema)
        self.db_manager.create_table_if_not_exists("user_progress", progress_schema)
        
        print("✅ Auth database tables initialized")
    
    def create_default_admin(self):
        """Create default admin user if not exists"""
        admin_email = "fartec0@protonmail.com"
        admin_password = "fartec0@protonmail.com"  # Initial password same as email
        
        if not self.user_exists(admin_email):
            self.create_user(admin_email, admin_password, role="admin")
            print(f"✅ Default admin created: {admin_email}")
            print(f"🔑 Initial password: {admin_password}")
            print("⚠️  Please change this password after first login!")
    
    def hash_password(self, password, salt=None):
        """Hash password with salt using shared database manager utility"""
        return self.db_manager.hash_password(password, salt)
    
    def user_exists(self, email):
        """Check if user exists using shared database manager"""
        return self.db_manager.record_exists("users", "email = ?", (email,))
    
    def create_user(self, email, password, role="student", profile_data=None):
        """Create new user using shared database manager"""
        
        # Validate email format
        if not email or "@" not in email:
            return False, "Invalid email format"
        
        email_parts = email.split("@")
        if len(email_parts) != 2 or not email_parts[0] or not email_parts[1]:
            return False, "Invalid email format"
        
        domain = email_parts[1]
        if "." not in domain or domain.endswith(".") or domain.startswith("."):
            return False, "Invalid email format"
        
        if self.user_exists(email):
            return False, "User already exists"
        
        password_hash, salt = self.hash_password(password)
        
        profile_json = json.dumps(profile_data or {})
        
        try:
            user_data = {
                "email": email,
                "password_hash": password_hash,
                "salt": salt,
                "role": role,
                "profile_data": profile_json
            }
            
            user_id = self.db_manager.insert_record("users", user_data)
            return True, f"User created successfully with ID: {user_id}"
        
        except Exception as e:
            return False, f"Error creating user: {str(e)}"
    
    def authenticate_user(self, email, password):
        """Authenticate user login"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, password_hash, salt, role, is_active 
            FROM users WHERE email = ?
        """, (email,))
        
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False, "User not found"
        
        user_id, stored_hash, salt, role, is_active = result
        
        if not is_active:
            conn.close()
            return False, "Account is deactivated"
        
        # Verify password
        password_hash, _ = self.hash_password(password, salt)
        
        if password_hash == stored_hash:
            # Update last login
            cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (user_id,))
            conn.commit()
            
            # Create session
            session_token = self.create_session(user_id)
            
            # Set current user
            self.current_user = {
                "user_id": user_id,
                "email": email,
                "role": role,
                "session_token": session_token
            }
            
            conn.close()
            
            return True, {
                "user_id": user_id,
                "email": email,
                "role": role,
                "session_token": session_token
            }
        else:
            conn.close()
            return False, "Invalid password"
    
    def create_session(self, user_id):
        """Create new session for user"""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + self.session_duration
        
        self.active_sessions[session_token] = {
            "user_id": user_id,
            "expires_at": expires_at
        }
        
        return session_token
    
    def validate_session(self, session_token):
        """Validate session token"""
        if session_token not in self.active_sessions:
            return False, None
        
        session_data = self.active_sessions[session_token]
        
        if datetime.now() > session_data["expires_at"]:
            # Session expired
            del self.active_sessions[session_token]
            return False, None
        
        return True, session_data["user_id"]
    
    def logout(self):
        """Logout current user"""
        if self.current_user and self.current_user.get("session_token"):
            session_token = self.current_user["session_token"]
            if session_token in self.active_sessions:
                del self.active_sessions[session_token]
        
        self.current_user = None
        return True
    
    def is_logged_in(self):
        """Check if user is logged in"""
        return self.current_user is not None
    
    def is_admin(self):
        """Check if current user is admin"""
        return self.current_user and self.current_user.get("role") == "admin"
    
    def get_user_info(self, user_id):
        """Get user information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT email, role, created_at, last_login, profile_data
            FROM users WHERE id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            email, role, created_at, last_login, profile_data = result
            return {
                "id": user_id,
                "email": email,
                "role": role,
                "created_at": created_at,
                "last_login": last_login,
                "profile_data": json.loads(profile_data)
            }
        
        return None
    
    def get_all_users(self):
        """Get all users (admin only)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, role, created_at, last_login, is_active
            FROM users ORDER BY created_at DESC
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        users = []
        for row in results:
            users.append({
                "id": row[0],
                "email": row[1],
                "role": row[2],
                "created_at": row[3],
                "last_login": row[4],
                "is_active": bool(row[5])
            })
        
        return users
    
    def update_user_role(self, user_id, new_role):
        """Update user role (admin only)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET role = ? WHERE id = ?
        """, (new_role, user_id))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def deactivate_user(self, user_id):
        """Deactivate user account"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET is_active = 0 WHERE id = ?
        """, (user_id,))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def change_password(self, user_id, old_password, new_password):
        """Change user password"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current password hash and salt
        cursor.execute("""
            SELECT password_hash, salt FROM users WHERE id = ?
        """, (user_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False, "User not found"
        
        stored_hash, salt = result
        
        # Verify old password
        old_hash, _ = self.hash_password(old_password, salt)
        if old_hash != stored_hash:
            conn.close()
            return False, "Current password is incorrect"
        
        # Hash new password
        new_hash, new_salt = self.hash_password(new_password)
        
        # Update password
        cursor.execute("""
            UPDATE users SET password_hash = ?, salt = ? WHERE id = ?
        """, (new_hash, new_salt, user_id))
        
        conn.commit()
        conn.close()
        
        return True, "Password changed successfully"
    
    def create_sidebar_auth(self):
        """Create a compact sidebar authentication widget"""
        
        # State variables for UI updates
        with gr.Column(scale=1, min_width=300) as sidebar:
            # Compact header
            gr.HTML("""
            <div style="text-align: center; padding: 1rem; 
                       background: linear-gradient(135deg, #1e40af 0%, #3730a3 100%);
                       border: 2px solid #3b82f6; border-radius: 12px; color: white; margin-bottom: 1rem;">
                <h3 style="margin-bottom: 0.5rem;">🔐 Login Portal</h3>
                <p style="font-size: 0.9rem; margin: 0;">Secure Academic Access</p>
            </div>
            """)
            
            # Current Status Display
            status_display = gr.HTML(value="""
                <div style="background: #1a1a1a; border: 2px solid #3a3a3a; border-radius: 8px; padding: 0.8rem; margin: 0.5rem 0; color: #ffffff;">
                    <h4 style="color: #ffffff; margin: 0; font-size: 0.9rem;">🔓 Not Logged In</h4>
                    <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; color: #cccccc;">Please authenticate</p>
                </div>
            """)
            
            # Compact login form
            with gr.Column():
                login_email = gr.Textbox(
                    label="📧 Email",
                    placeholder="Academic email",
                    value="",
                    scale=1
                )
                login_password = gr.Textbox(
                    label="🔑 Password", 
                    placeholder="Password",
                    type="password",
                    value="",
                    scale=1
                )
                
                with gr.Row():
                    login_btn = gr.Button("🚀 Login", variant="primary", size="sm", scale=2)
                    logout_btn = gr.Button("🚪 Exit", variant="secondary", size="sm", scale=1, visible=False)
                
                login_message = gr.HTML()
            
            # Quick register section
            with gr.Accordion("📝 New User Registration", open=False):
                reg_email = gr.Textbox(
                    label="📧 Email",
                    placeholder="Academic email"
                )
                reg_password = gr.Textbox(
                    label="🔑 Password",
                    placeholder="Strong password",
                    type="password"
                )
                reg_confirm = gr.Textbox(
                    label="🔑 Confirm",
                    placeholder="Confirm password",
                    type="password"
                )
                reg_name = gr.Textbox(
                    label="👤 Name",
                    placeholder="Full name"
                )
                reg_institution = gr.Textbox(
                    label="🏛️ Institution",
                    placeholder="University/Organization"
                )
                
                register_btn = gr.Button("🎓 Register", variant="primary", size="sm")
                register_message = gr.HTML()
            
            # Admin panel (compact)
            with gr.Accordion("👑 Admin Panel", open=False, visible=False) as admin_accordion:
                admin_panel = gr.Column()
                
                with admin_panel:
                    gr.Markdown("#### 📊 User Management")
                    
                    refresh_btn = gr.Button("🔄 Refresh", size="sm")
                    users_display = gr.HTML()
                    
                    target_user_id = gr.Number(
                        label="User ID", 
                        precision=0,
                        minimum=1
                    )
                    new_role = gr.Dropdown(
                        ["student", "admin"],
                        label="Role",
                        value="student"
                    )
                    
                    with gr.Row():
                        update_role_btn = gr.Button("🔄 Update", size="sm", scale=1)
                        deactivate_btn = gr.Button("🚫 Deactivate", variant="stop", size="sm", scale=1)
                    
                    admin_action_message = gr.HTML()
            
            # SIDEBAR LOGIN FUNCTION
            def handle_sidebar_login(email, password):
                if not email or not password:
                    return [
                        """<div style="background: #2a1a1a; border: 1px solid #dc2626; border-radius: 8px; padding: 0.8rem; color: #ef4444; font-size: 0.8rem;">
                        ❌ Email and password required</div>""",
                        gr.update(visible=False), gr.update(visible=True),
                        """<div style="background: #1a1a1a; border: 2px solid #3a3a3a; border-radius: 8px; padding: 0.8rem; margin: 0.5rem 0; color: #ffffff;">
                        <h4 style="color: #ffffff; margin: 0; font-size: 0.9rem;">🔓 Not Logged In</h4>
                        <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; color: #cccccc;">Please authenticate</p></div>""",
                        gr.update(visible=False)
                    ]
                
                success, result = self.authenticate_user(email, password)
                
                if success:
                    user_info = result
                    status_html = f"""
                    <div style="background: #1a2e1a; border: 2px solid #16a34a; border-radius: 8px; padding: 0.8rem; margin: 0.5rem 0; color: #ffffff;">
                        <h4 style="color: #22c55e; margin: 0; font-size: 0.9rem;">✅ Authenticated</h4>
                        <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; color: #cccccc;">{user_info['email']}</p>
                        <p style="margin: 0.2rem 0 0 0; font-size: 0.7rem; color: #9ca3af;">Role: {user_info['role'].title()}</p>
                    </div>
                    """
                    
                    login_msg = f"""<div style="background: #1a2e1a; border: 1px solid #22c55e; border-radius: 8px; padding: 0.8rem; color: #22c55e; font-size: 0.8rem;">
                    ✅ Welcome, {user_info['email'].split('@')[0]}!</div>"""
                    
                    # Show admin panel if admin
                    admin_visible = user_info['role'] == 'admin'
                    
                    return [
                        login_msg,
                        gr.update(visible=True),  # logout button
                        gr.update(visible=False), # login button
                        status_html,
                        gr.update(visible=admin_visible)  # admin accordion
                    ]
                else:
                    error_msg = f"""<div style="background: #2a1a1a; border: 1px solid #dc2626; border-radius: 8px; padding: 0.8rem; color: #ef4444; font-size: 0.8rem;">
                    ❌ {result}</div>"""
                    
                    return [
                        error_msg,
                        gr.update(visible=False), gr.update(visible=True),
                        """<div style="background: #1a1a1a; border: 2px solid #3a3a3a; border-radius: 8px; padding: 0.8rem; margin: 0.5rem 0; color: #ffffff;">
                        <h4 style="color: #ffffff; margin: 0; font-size: 0.9rem;">🔓 Not Logged In</h4>
                        <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; color: #cccccc;">Please authenticate</p></div>""",
                        gr.update(visible=False)
                    ]
            
            # SIDEBAR LOGOUT FUNCTION
            def handle_sidebar_logout():
                self.logout()
                return [
                    """<div style="background: #1a2a2a; border: 1px solid #0288d1; border-radius: 8px; padding: 0.8rem; color: #38bdf8; font-size: 0.8rem;">
                    👋 Logged out</div>""",
                    gr.update(visible=False), # logout button
                    gr.update(visible=True),  # login button
                    """<div style="background: #1a1a1a; border: 2px solid #3a3a3a; border-radius: 8px; padding: 0.8rem; margin: 0.5rem 0; color: #ffffff;">
                    <h4 style="color: #ffffff; margin: 0; font-size: 0.9rem;">🔓 Not Logged In</h4>
                    <p style="margin: 0.3rem 0 0 0; font-size: 0.8rem; color: #cccccc;">Please authenticate</p></div>""",
                    gr.update(visible=False)  # admin accordion
                ]
            
            # SIDEBAR REGISTER FUNCTION
            def handle_sidebar_registration(email, password, confirm, name, institution):
                if not all([email, password, confirm, name]):
                    return """<div style="background: #2a1a1a; border: 1px solid #dc2626; border-radius: 8px; padding: 0.8rem; color: #ef4444; font-size: 0.8rem;">
                    ❌ All fields required</div>"""
                
                if password != confirm:
                    return """<div style="background: #2a1a1a; border: 1px solid #dc2626; border-radius: 8px; padding: 0.8rem; color: #ef4444; font-size: 0.8rem;">
                    ❌ Passwords don't match</div>"""
                
                if len(password) < 8:
                    return """<div style="background: #2a1a1a; border: 1px solid #dc2626; border-radius: 8px; padding: 0.8rem; color: #ef4444; font-size: 0.8rem;">
                    ❌ Password must be 8+ characters</div>"""
                
                profile_data = {
                    "name": name,
                    "institution": institution
                }
                
                success, message = self.create_user(email, password, profile_data=profile_data)
                
                if success:
                    return f"""<div style="background: #1a2e1a; border: 1px solid #22c55e; border-radius: 8px; padding: 0.8rem; color: #22c55e; font-size: 0.8rem;">
                    ✅ Account created! Please login.</div>"""
                else:
                    return f"""<div style="background: #2a1a1a; border: 1px solid #dc2626; border-radius: 8px; padding: 0.8rem; color: #ef4444; font-size: 0.8rem;">
                    ❌ {message}</div>"""
            
            # Copy admin functions from main interface
            def refresh_users():
                users = self.get_all_users()
                if users:
                    html = "<div style='background: #1a1a1a; padding: 0.8rem; border-radius: 8px; color: #ffffff; font-size: 0.8rem;'>"
                    html += "<h4>📊 Active Users</h4>"
                    for user in users:
                        role_color = "#fbbf24" if user['role'] == 'admin' else "#38bdf8"
                        status_color = "#22c55e" if user['is_active'] else "#ef4444"
                        html += f"""
                        <div style='margin: 0.5rem 0; padding: 0.5rem; background: #2a2a2a; border-radius: 6px;'>
                            <strong>ID: {user['id']}</strong> | {user['email']}<br>
                            <span style='color: {role_color}'>Role: {user['role']}</span> | 
                            <span style='color: {status_color}'>Status: {"Active" if user['is_active'] else "Inactive"}</span><br>
                            <small>Last Login: {user['last_login'] or 'Never'}</small>
                        </div>
                        """
                    html += "</div>"
                    return html
                else:
                    return "<div style='background: #2a1a1a; padding: 0.8rem; border-radius: 8px; color: #ef4444; font-size: 0.8rem;'>No users found</div>"
            
            def update_user_role(user_id, role):
                if not user_id:
                    return """<div style="background: #2a1a1a; border: 1px solid #dc2626; border-radius: 8px; padding: 0.8rem; color: #ef4444; font-size: 0.8rem;">
                    ❌ Please enter user ID</div>"""
                
                success, message = self.update_user_role(int(user_id), role)
                
                if success:
                    return f"""<div style="background: #1a2e1a; border: 1px solid #22c55e; border-radius: 8px; padding: 0.8rem; color: #22c55e; font-size: 0.8rem;">
                    ✅ {message}</div>"""
                else:
                    return f"""<div style="background: #2a1a1a; border: 1px solid #dc2626; border-radius: 8px; padding: 0.8rem; color: #ef4444; font-size: 0.8rem;">
                    ❌ {message}</div>"""
            
            def deactivate_user_account(user_id):
                if not user_id:
                    return """<div style="background: #2a1a1a; border: 1px solid #dc2626; border-radius: 8px; padding: 0.8rem; color: #ef4444; font-size: 0.8rem;">
                    ❌ Please enter user ID</div>"""
                
                success, message = self.deactivate_user(int(user_id))
                
                if success:
                    return f"""<div style="background: #1a2e1a; border: 1px solid #22c55e; border-radius: 8px; padding: 0.8rem; color: #22c55e; font-size: 0.8rem;">
                    ✅ {message}</div>"""
                else:
                    return f"""<div style="background: #2a1a1a; border: 1px solid #dc2626; border-radius: 8px; padding: 0.8rem; color: #ef4444; font-size: 0.8rem;">
                    ❌ {message}</div>"""
            
            # Connect sidebar events
            login_btn.click(
                fn=handle_sidebar_login,
                inputs=[login_email, login_password],
                outputs=[login_message, logout_btn, login_btn, status_display, admin_accordion]
            )
            
            logout_btn.click(
                fn=handle_sidebar_logout,
                inputs=[],
                outputs=[login_message, logout_btn, login_btn, status_display, admin_accordion]
            )
            
            register_btn.click(
                fn=handle_sidebar_registration,
                inputs=[reg_email, reg_password, reg_confirm, reg_name, reg_institution],
                outputs=[register_message]
            )
            
            refresh_btn.click(
                fn=refresh_users,
                inputs=[],
                outputs=[users_display]
            )
            
            update_role_btn.click(
                fn=update_user_role,
                inputs=[target_user_id, new_role],
                outputs=[admin_action_message]
            )
            
            deactivate_btn.click(
                fn=deactivate_user_account,
                inputs=[target_user_id],
                outputs=[admin_action_message]
            )
        
        return sidebar
    
    def create_auth_interface(self):
        """Create the authentication interface with working buttons"""
        
        # State variables for UI updates
        with gr.Row():
            # Hidden state variables to track login status
            login_state = gr.State(value=False)
            user_role = gr.State(value="")
            user_email = gr.State(value="")
        
        with gr.Column() as auth_interface:
            # Header
            gr.HTML("""
            <div style="text-align: center; padding: 2rem; 
                       background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
                       border: 3px solid #fbbf24; border-radius: 20px; color: white; margin-bottom: 2rem;">
                <h1 style="font-family: 'Crimson Text', serif; margin-bottom: 1rem;">
                    🎓 AI Governance Portal Authentication
                </h1>
                <p style="font-size: 1.1rem;">
                    Secure access to your PhD-level AI governance studies
                </p>

            </div>
            """)
            
            # Current Status Display
            status_display = gr.HTML(value="""
                <div style="background: #f0f9ff; border: 2px solid #0ea5e9; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                    <h3 style="color: #0369a1; margin: 0;">🔓 Not Logged In</h3>
                    <p style="margin: 0.5rem 0 0 0;">Please login or register to access the student portal</p>
                </div>
            """)
            
            with gr.Tabs() as auth_tabs:
                # LOGIN TAB
                with gr.Tab("🔐 Login"):
                    with gr.Column():
                        gr.Markdown("### 🔑 Account Login")
                        
                        login_email = gr.Textbox(
                            label="Email Address",
                            placeholder="Enter your email address",
                            value=""
                        )
                        login_password = gr.Textbox(
                            label="Password", 
                            placeholder="Enter your password",
                            type="password",
                            value=""
                        )
                        
                        with gr.Row():
                            login_btn = gr.Button("🚀 Login", variant="primary", size="lg")
                            logout_btn = gr.Button("🚪 Logout", variant="secondary", visible=False)
                        
                        login_message = gr.HTML()
                
                # REGISTER TAB
                with gr.Tab("📝 Register"):
                    with gr.Column():
                        gr.Markdown("### 🎓 New Student Registration")
                        
                        reg_email = gr.Textbox(
                            label="Email Address",
                            placeholder="Enter your email address"
                        )
                        reg_password = gr.Textbox(
                            label="Password",
                            placeholder="Create a strong password (8+ characters)",
                            type="password"
                        )
                        reg_confirm = gr.Textbox(
                            label="Confirm Password",
                            placeholder="Confirm your password",
                            type="password"
                        )
                        reg_name = gr.Textbox(
                            label="Full Name",
                            placeholder="Enter your full name"
                        )
                        reg_institution = gr.Textbox(
                            label="Institution/Organization",
                            placeholder="Your university or company (optional)"
                        )
                        
                        register_btn = gr.Button("🎓 Create Account", variant="primary", size="lg")
                        register_message = gr.HTML()
                
                # ADMIN PANEL TAB
                with gr.Tab("👑 Admin Panel"):
                    with gr.Column():
                        gr.Markdown("### 👑 Administrative Controls")
                        gr.Markdown("*Automatic access after admin login*")
                        
                        admin_panel = gr.Column(visible=False)
                        
                        with admin_panel:
                            gr.Markdown("#### 📊 User Management Dashboard")
                            
                            refresh_btn = gr.Button("🔄 Refresh User List")
                            users_display = gr.HTML()
                            
                            gr.Markdown("#### ⚙️ User Actions")
                            with gr.Row():
                                target_user_id = gr.Number(
                                    label="User ID", 
                                    precision=0,
                                    minimum=1
                                )
                                new_role = gr.Dropdown(
                                    ["student", "admin"],
                                    label="New Role",
                                    value="student"
                                )
                            
                            with gr.Row():
                                update_role_btn = gr.Button("🔄 Update Role")
                                deactivate_btn = gr.Button("🚫 Deactivate User", variant="stop")
                            
                            admin_action_message = gr.HTML()
            
            # LOGIN FUNCTION
            def handle_login(email, password):
                if not email or not password:
                    return [
                        """<div style="background: #fee2e2; border: 1px solid #fca5a5; border-radius: 10px; padding: 1rem; color: #dc2626;">
                        ❌ Please enter both email and password</div>""",
                        False, "", "", gr.update(visible=False), gr.update(visible=True),
                        """<div style="background: #f0f9ff; border: 2px solid #0ea5e9; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                        <h3 style="color: #0369a1; margin: 0;">🔓 Not Logged In</h3>
                        <p style="margin: 0.5rem 0 0 0;">Please login or register to access the student portal</p></div>""",
                        gr.update(visible=False)
                    ]
                
                success, result = self.authenticate_user(email, password)
                
                if success:
                    user_info = result
                    status_html = f"""
                    <div style="background: #dcfce7; border: 2px solid #16a34a; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                        <h3 style="color: #15803d; margin: 0;">✅ Logged In Successfully</h3>
                        <p style="margin: 0.5rem 0 0 0;"><strong>Welcome {user_info['email']}</strong> ({user_info['role'].title()})</p>
                        <p style="margin: 0.5rem 0 0 0;"><small>Session: {user_info['session_token'][:20]}...</small></p>
                    </div>
                    """
                    
                    login_msg = f"""<div style="background: #dcfce7; border: 1px solid #86efac; border-radius: 10px; padding: 1rem; color: #16a34a;">
                    ✅ Welcome back, {user_info['email']}! You can now access the Student Portal.</div>"""
                    
                    # Show admin panel if admin
                    admin_visible = user_info['role'] == 'admin'
                    
                    return [
                        login_msg,
                        True, 
                        user_info['role'], 
                        user_info['email'],
                        gr.update(visible=True),  # logout button
                        gr.update(visible=False), # login button
                        status_html,
                        gr.update(visible=admin_visible)  # admin panel
                    ]
                else:
                    error_msg = f"""<div style="background: #fee2e2; border: 1px solid #fca5a5; border-radius: 10px; padding: 1rem; color: #dc2626;">
                    ❌ {result}</div>"""
                    
                    return [
                        error_msg,
                        False, "", "", gr.update(visible=False), gr.update(visible=True),
                        """<div style="background: #f0f9ff; border: 2px solid #0ea5e9; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                        <h3 style="color: #0369a1; margin: 0;">🔓 Not Logged In</h3>
                        <p style="margin: 0.5rem 0 0 0;">Please login or register to access the student portal</p></div>""",
                        gr.update(visible=False)
                    ]
            
            # LOGOUT FUNCTION
            def handle_logout():
                self.logout()
                return [
                    """<div style="background: #e0f2fe; border: 1px solid #0288d1; border-radius: 10px; padding: 1rem; color: #01579b;">
                    👋 Logged out successfully</div>""",
                    False, "", "",
                    gr.update(visible=False), # logout button
                    gr.update(visible=True),  # login button
                    """<div style="background: #f0f9ff; border: 2px solid #0ea5e9; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                    <h3 style="color: #0369a1; margin: 0;">🔓 Not Logged In</h3>
                    <p style="margin: 0.5rem 0 0 0;">Please login or register to access the student portal</p></div>""",
                    gr.update(visible=False)  # admin panel
                ]
            
            # REGISTER FUNCTION
            def handle_registration(email, password, confirm, name, institution):
                if not all([email, password, confirm, name]):
                    return """<div style="background: #fee2e2; border: 1px solid #fca5a5; border-radius: 10px; padding: 1rem; color: #dc2626;">
                    ❌ Please fill in all required fields</div>"""
                
                if password != confirm:
                    return """<div style="background: #fee2e2; border: 1px solid #fca5a5; border-radius: 10px; padding: 1rem; color: #dc2626;">
                    ❌ Passwords do not match</div>"""
                
                if len(password) < 8:
                    return """<div style="background: #fee2e2; border: 1px solid #fca5a5; border-radius: 10px; padding: 1rem; color: #dc2626;">
                    ❌ Password must be at least 8 characters long</div>"""
                
                profile_data = {
                    "name": name,
                    "institution": institution or "Not specified"
                }
                
                success, message = self.create_user(email, password, "student", profile_data)
                
                if success:
                    return f"""<div style="background: #dcfce7; border: 1px solid #86efac; border-radius: 10px; padding: 1rem; color: #16a34a;">
                    ✅ Account created successfully! You can now login with your credentials.
                    <br><small>{message}</small></div>"""
                else:
                    return f"""<div style="background: #fee2e2; border: 1px solid #fca5a5; border-radius: 10px; padding: 1rem; color: #dc2626;">
                    ❌ {message}</div>"""
            
            # ADMIN FUNCTIONS
            def refresh_users():
                if not self.is_admin():
                    return "<p style='color: red;'>❌ Admin access required</p>"
                
                users = self.get_all_users()
                if not users:
                    return "<p>No users found</p>"
                
                html = """
                <div style="background: white; border-radius: 10px; padding: 1rem; border: 1px solid #e2e8f0;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="background: #f1f5f9; border-bottom: 2px solid #e2e8f0;">
                            <th style="padding: 0.75rem; text-align: left; border: 1px solid #e2e8f0;">ID</th>
                            <th style="padding: 0.75rem; text-align: left; border: 1px solid #e2e8f0;">Email</th>
                            <th style="padding: 0.75rem; text-align: left; border: 1px solid #e2e8f0;">Role</th>
                            <th style="padding: 0.75rem; text-align: left; border: 1px solid #e2e8f0;">Created</th>
                            <th style="padding: 0.75rem; text-align: left; border: 1px solid #e2e8f0;">Last Login</th>
                            <th style="padding: 0.75rem; text-align: left; border: 1px solid #e2e8f0;">Status</th>
                        </tr>
                """
                
                for user in users:
                    status_color = "#16a34a" if user['is_active'] else "#dc2626"
                    status_text = "Active" if user['is_active'] else "Inactive"
                    role_color = "#f59e0b" if user['role'] == 'admin' else "#3b82f6"
                    
                    html += f"""
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 0.75rem; border: 1px solid #e2e8f0;">{user['id']}</td>
                        <td style="padding: 0.75rem; border: 1px solid #e2e8f0;">{user['email']}</td>
                        <td style="padding: 0.75rem; border: 1px solid #e2e8f0;">
                            <span style="background: {role_color}; color: white; padding: 0.25rem 0.5rem; border-radius: 15px; font-size: 0.8rem;">
                                {user['role'].upper()}
                            </span>
                        </td>
                        <td style="padding: 0.75rem; border: 1px solid #e2e8f0;">{user['created_at'][:10] if user['created_at'] else 'N/A'}</td>
                        <td style="padding: 0.75rem; border: 1px solid #e2e8f0;">{user['last_login'][:10] if user['last_login'] else 'Never'}</td>
                        <td style="padding: 0.75rem; border: 1px solid #e2e8f0; color: {status_color}; font-weight: bold;">{status_text}</td>
                    </tr>
                    """
                
                html += "</table></div>"
                return html
            
            def update_user_role(user_id, role):
                if not self.is_admin():
                    return "❌ Admin access required"
                
                if not user_id:
                    return "❌ Please enter a user ID"
                
                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, int(user_id)))
                    conn.commit()
                    rows_affected = cursor.rowcount
                    conn.close()
                    
                    if rows_affected > 0:
                        return f"✅ User {user_id} role updated to {role}"
                    else:
                        return f"❌ User {user_id} not found"
                except Exception as e:
                    return f"❌ Error: {str(e)}"
            
            def deactivate_user_account(user_id):
                if not self.is_admin():
                    return "❌ Admin access required"
                
                if not user_id:
                    return "❌ Please enter a user ID"
                
                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (int(user_id),))
                    conn.commit()
                    rows_affected = cursor.rowcount
                    conn.close()
                    
                    if rows_affected > 0:
                        return f"✅ User {user_id} has been deactivated"
                    else:
                        return f"❌ User {user_id} not found"
                except Exception as e:
                    return f"❌ Error: {str(e)}"
            
            # CONNECT ALL BUTTON HANDLERS
            login_btn.click(
                fn=handle_login,
                inputs=[login_email, login_password],
                outputs=[login_message, login_state, user_role, user_email, logout_btn, login_btn, status_display, admin_panel]
            )
            
            logout_btn.click(
                fn=handle_logout,
                inputs=[],
                outputs=[login_message, login_state, user_role, user_email, logout_btn, login_btn, status_display, admin_panel]
            )
            
            register_btn.click(
                fn=handle_registration,
                inputs=[reg_email, reg_password, reg_confirm, reg_name, reg_institution],
                outputs=[register_message]
            )
            
            refresh_btn.click(
                fn=refresh_users,
                inputs=[],
                outputs=[users_display]
            )
            
            update_role_btn.click(
                fn=update_user_role,
                inputs=[target_user_id, new_role],
                outputs=[admin_action_message]
            )
            
            deactivate_btn.click(
                fn=deactivate_user_account,
                inputs=[target_user_id],
                outputs=[admin_action_message]
            )
        
        # Return the interface and state variables for external access
        return auth_interface, login_state, user_role, user_email 