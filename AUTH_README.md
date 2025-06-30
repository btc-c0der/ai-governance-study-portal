# 🔐 Authentication System - AI Governance PhD Study Portal

## 🎓 Overview

Your AI Governance Architect's Codex now features a complete authentication system with user management, role-based access control, and protected student portal functionality. This transforms your study portal into a multi-user academic environment with secure access control.

## 🚀 Quick Start

### 1. Starting with Authentication

**Option A: Use the Launcher (Recommended)**
```bash
python3 launch_auth_portal.py
```

**Option B: Direct Launch**
```bash
python3 app.py
```

### 2. Accessing the Portal

1. Navigate to **🔐 Authentication** tab (first tab)
2. Choose your action:
   - **Login** if you have existing credentials
   - **Register** to create a new student account
   - **Admin Panel** for administrative tasks

### 3. Default Admin Access

**👑 Administrator Credentials:**
- **Email:** `fartec0@protonmail.com`
- **Initial Password:** `fartec0@protonmail.com`

⚠️ **IMPORTANT:** Change this password immediately after first login!

## 🔐 Authentication Features

### User Registration
- **🎓 Student Registration:** Create new student accounts with profile information
- **📧 Email Validation:** Unique email addresses required
- **🔒 Secure Passwords:** Minimum 8 characters with hashing + salt
- **👤 Profile Data:** Name and institution information

### User Login
- **🔑 Credential Verification:** Email and password authentication
- **⏰ Session Management:** 24-hour session duration
- **🛡️ Security:** PBKDF2 password hashing with 100k iterations
- **📊 Login Tracking:** Last login timestamps

### Admin Panel
- **👑 Admin-Only Access:** Restricted to admin role users
- **📊 User Management:** View all users, roles, and activity
- **🔄 Role Management:** Change user roles (student ↔ admin)
- **🚫 Account Control:** Deactivate user accounts
- **📈 User Analytics:** Registration and login statistics

## 🎓 Protected Student Portal

Once authenticated, students gain access to the **🎓 Student Portal** containing:

### 📚 Educational Content
- **📖 Curriculum Explorer** - Personal progress tracking through 12-week program
- **⚖️ EU AI Act Explorer** - Interactive legal content with bookmarking
- **🧠 AI Tutor Chat** - Personalized AI assistance and Q&A
- **🧪 Mock AIGP Quiz** - Certification exam preparation

### 🛠️ Interactive Tools
- **🤖 Model Demos** - ML model demonstrations with explanations
- **📊 Performance Tracker** - Individual analytics and progress charts
- **🔗 Sync & Export** - Data synchronization and export capabilities

### 📚 Public Resources
Available without authentication:
- **📄 EU AI Act Quick Reference**
- **🔗 External Resources** - Curated legal AI links
- **💼 Annex IV Builder** - Compliance document generator

## 💽 Database Structure

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    profile_data TEXT DEFAULT '{}'
);
```

### Session Management
- **In-Memory Sessions:** Active session tokens stored in memory
- **Session Duration:** 24-hour automatic expiration
- **Token Security:** URL-safe random tokens (256-bit entropy)

## 🛡️ Security Features

### Password Security
- **🔐 PBKDF2 Hashing:** Industry-standard password hashing
- **🧂 Unique Salt:** 32-byte random salt per password
- **⚡ 100k Iterations:** Computational hardening against attacks

### Session Security
- **🎟️ Secure Tokens:** Cryptographically secure random tokens
- **⏰ Auto-Expiration:** Sessions expire after 24 hours
- **🚫 Session Invalidation:** Logout removes session tokens

### Access Control
- **🎯 Role-Based Access:** Student vs Admin role separation
- **🔒 Protected Routes:** Authentication required for student portal
- **🛡️ Admin Restrictions:** Admin panel requires admin role

## 🎯 User Roles

### 👤 Student Role
**Permissions:**
- ✅ Access student portal and all educational content
- ✅ Track personal progress and take quizzes
- ✅ Use AI tutor and interactive demos
- ✅ Export personal data and sync with external services
- ❌ Cannot access admin panel or manage other users

### 👑 Admin Role
**Permissions:**
- ✅ All student permissions
- ✅ Access admin control panel
- ✅ View all users and their activity
- ✅ Change user roles and deactivate accounts
- ✅ System-wide user management

## 🔧 Configuration

### Environment Variables
```bash
GRADIO_SERVER_PORT=7861  # Custom port if 7860 is busy
```

### Database Location
- **Default Path:** `data/users.db`
- **Auto-Creation:** Database and tables created automatically
- **Backup Recommended:** SQLite file can be backed up

## 📊 Usage Analytics

### User Management Statistics
- **Total Users:** Track registration growth
- **Active Sessions:** Monitor concurrent users
- **Login Frequency:** User engagement metrics
- **Role Distribution:** Student vs admin ratios

### Learning Analytics
- **Progress Tracking:** Individual curriculum completion
- **Quiz Performance:** Assessment results and trends
- **Study Time:** Time spent in educational modules
- **Feature Usage:** Most popular portal sections

## 🚨 Security Best Practices

### For Administrators
1. **🔄 Change Default Password:** Immediately after first login
2. **👥 Limit Admin Accounts:** Only trusted users should have admin role
3. **🔍 Monitor Activity:** Regularly check user activity logs
4. **💾 Backup Database:** Regular SQLite database backups

### For Students
1. **🔒 Strong Passwords:** Use complex, unique passwords
2. **🔐 Secure Sessions:** Log out when finished studying
3. **📧 Email Security:** Keep registered email secure
4. **🚫 No Sharing:** Don't share login credentials

## 🛠️ Troubleshooting

### Common Issues

**Authentication Tab Not Visible**
```bash
# Check if auth_manager.py exists in components/
ls components/auth_manager.py
```

**Database Errors**
```bash
# Ensure data directory exists
mkdir -p data
# Check permissions
ls -la data/
```

**Port Already in Use**
```bash
# Kill existing process
lsof -ti:7860 | xargs kill -9
# Or use different port
GRADIO_SERVER_PORT=7861 python3 app.py
```

**Login Not Working**
- Verify correct email and password
- Check if account is active (not deactivated)
- Try refreshing the page
- Check browser console for errors

## 🔄 Updates and Maintenance

### Regular Tasks
- **🔄 Password Updates:** Encourage regular password changes
- **🧹 Session Cleanup:** Old sessions auto-expire
- **📊 User Activity Review:** Monitor for suspicious activity
- **💾 Database Maintenance:** Regular backups and optimization

### Adding New Features
The authentication system is designed to be extensible:
- **New Roles:** Add specialized roles (instructor, observer, etc.)
- **Enhanced Permissions:** Fine-grained access control
- **External Auth:** Integration with OAuth providers
- **Advanced Analytics:** Detailed usage reporting

## 📞 Support

### Getting Help
1. **📖 Check Documentation:** Review this README thoroughly
2. **🔍 Search Issues:** Look for similar problems in logs
3. **🧪 Test Basic Functions:** Verify authentication works
4. **📝 Provide Details:** Include specific error messages

### Development
- **🔧 Configuration:** Most settings in `auth_manager.py`
- **🎨 UI Styling:** Authentication interface styling in `app.py`
- **💾 Database:** SQLite operations in authentication methods
- **🛡️ Security:** Password hashing and session management

---

## 🎉 Congratulations!

Your AI Governance PhD Study Portal now features:

✅ **Complete Authentication System**
✅ **User Registration & Login**
✅ **Admin Panel for User Management**
✅ **Protected Student Portal Access**
✅ **Role-Based Access Control**
✅ **Secure Session Management**
✅ **Professional PhD Diploma Theme**

**🚀 Start your authenticated AI governance journey today!**

---

*Generated by AI Governance Architect's Codex Authentication System*
*📜 GBU2 Licensed • Academic Excellence • Security First 🔐* 