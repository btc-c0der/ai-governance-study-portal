"""
⚖️ EU AI Act Explorer Component
Interactive exploration of EU AI Act articles, annexes, and compliance requirements.
Based on official Regulation (EU) 2024/1689
"""

import gradio as gr
import json
import pandas as pd
from pathlib import Path
import re
from typing import List, Dict, Any
from datetime import datetime, timedelta

class AIActExplorer:
    def __init__(self):
        self.ai_act_data = self.load_ai_act_data()
        self.search_index = self.build_search_index()
    
    def load_ai_act_data(self):
        """Load structured EU AI Act data from official JSON"""
        data_path = Path("components/ai_act_articles.json")
        
        if not data_path.exists():
            return self.create_fallback_data()
        
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading AI Act data: {e}")
            return self.create_fallback_data()
    
    def create_fallback_data(self):
        """Create fallback data if main file unavailable"""
        return {
            "metadata": {
                "title": "Regulation (EU) 2024/1689 - Artificial Intelligence Act",
                "status": "Fallback data - please check components/ai_act_articles.json"
            }
        }
    
    def build_search_index(self):
        """Build searchable index from AI Act data"""
        index = []
        
        if not self.ai_act_data:
            return index
        
        # Index key definitions
        if "key_definitions" in self.ai_act_data:
            for article_key, article_data in self.ai_act_data["key_definitions"].items():
                if "key_terms" in article_data:
                    for term, definition in article_data["key_terms"].items():
                        index.append({
                            "type": "definition",
                            "article": article_key,
                            "title": f"Definition: {term.replace('_', ' ').title()}",
                            "content": definition,
                            "category": "Definitions",
                            "searchable_text": f"{term} {definition}".lower()
                        })
        
        # Index prohibited practices
        if "prohibited_practices" in self.ai_act_data:
            article_data = self.ai_act_data["prohibited_practices"]["article_5"]
            for practice in article_data.get("prohibited_systems", []):
                index.append({
                    "type": "prohibited_practice",
                    "article": "Article 5",
                    "title": f"Prohibited: {practice['id']}",
                    "content": practice["description"],
                    "category": "Prohibited Practices",
                    "risk_level": practice.get("risk_level", ""),
                    "searchable_text": f"{practice['description']} {practice.get('purpose', '')}".lower()
                })
        
        # Index high-risk systems
        if "high_risk_systems" in self.ai_act_data:
            if "annex_iii" in self.ai_act_data["high_risk_systems"]:
                for category in self.ai_act_data["high_risk_systems"]["annex_iii"].get("categories", []):
                    for system in category.get("systems", []):
                        index.append({
                            "type": "high_risk_system",
                            "article": "Annex III",
                            "title": f"High-Risk: {category['area']}",
                            "content": system,
                            "category": "High-Risk Systems",
                            "area": category["area"],
                            "searchable_text": f"{category['area']} {system}".lower()
                        })
        
        # Index obligations
        if "obligations_providers" in self.ai_act_data:
            article_data = self.ai_act_data["obligations_providers"]["article_16"]
            for obligation in article_data.get("obligations", []):
                index.append({
                    "type": "obligation",
                    "article": "Article 16",
                    "title": f"Obligation: {obligation['requirement']}",
                    "content": obligation["description"],
                    "category": "Provider Obligations",
                    "searchable_text": f"{obligation['requirement']} {obligation['description']}".lower()
                })
        
        # Index technical documentation requirements
        if "technical_documentation" in self.ai_act_data:
            if "annex_iv" in self.ai_act_data["technical_documentation"]:
                for section in self.ai_act_data["technical_documentation"]["annex_iv"].get("sections", []):
                    index.append({
                        "type": "technical_doc",
                        "article": "Annex IV",
                        "title": f"Tech Doc: {section['title']}",
                        "content": ", ".join(section.get("requirements", [])),
                        "category": "Technical Documentation",
                        "searchable_text": f"{section['title']} {' '.join(section.get('requirements', []))}".lower()
                    })
        
        # Index general-purpose AI models
        if "general_purpose_models" in self.ai_act_data:
            for article_key, article_data in self.ai_act_data["general_purpose_models"].items():
                if "obligations" in article_data:
                    for i, obligation in enumerate(article_data["obligations"]):
                        index.append({
                            "type": "gp_ai_obligation",
                            "article": article_key,
                            "title": f"GP AI: Obligation {i+1}",
                            "content": obligation,
                            "category": "General-Purpose AI",
                            "searchable_text": obligation.lower()
                        })
        
        return index
    
    def search_content(self, query: str, category_filter: str = "All") -> List[Dict[str, Any]]:
        """Search through AI Act content"""
        if not query or not self.search_index:
            return []
        
        query_terms = query.lower().split()
        results = []
        
        for item in self.search_index:
            # Category filter
            if category_filter != "All" and item.get("category") != category_filter:
                continue
            
            # Search in searchable text
            searchable = item.get("searchable_text", "")
            score = 0
            
            # Exact phrase match (highest score)
            if query.lower() in searchable:
                score += 10
            
            # Individual term matches
            for term in query_terms:
                if term in searchable:
                    score += 1
            
            if score > 0:
                item["relevance_score"] = score
                results.append(item)
        
        # Sort by relevance score
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return results[:20]  # Limit results
    
    def get_compliance_timeline(self):
        """Get implementation timeline for AI Act"""
        if "implementation_timeline" not in self.ai_act_data:
            return []
        
        timeline = []
        for milestone in self.ai_act_data["implementation_timeline"].get("key_dates", []):
            try:
                date_obj = datetime.strptime(milestone["date"], "%Y-%m-%d")
                days_from_now = (date_obj - datetime.now()).days
                
                if days_from_now > 0:
                    status = f"⏳ {days_from_now} days remaining"
                elif days_from_now > -30:
                    status = f"🔴 {abs(days_from_now)} days overdue"
                else:
                    status = "✅ Implemented"
                
                timeline.append({
                    "date": milestone["date"],
                    "milestone": milestone["milestone"],
                    "status": status,
                    "days_from_now": days_from_now
                })
            except:
                timeline.append({
                    "date": milestone["date"],
                    "milestone": milestone["milestone"],
                    "status": "📅 Scheduled",
                    "days_from_now": 999
                })
        
        return sorted(timeline, key=lambda x: x["days_from_now"])
    
    def assess_ai_system_risk(self, system_description: str) -> Dict[str, Any]:
        """Assess AI system risk level based on description"""
        if not system_description:
            return {"risk_level": "Unknown", "reasoning": "Please provide system description"}
        
        desc_lower = system_description.lower()
        assessment = {
            "risk_level": "Minimal Risk",
            "reasoning": [],
            "applicable_articles": [],
            "next_steps": []
        }
        
        # Check for prohibited practices
        prohibited_keywords = [
            "subliminal", "manipulative", "exploit vulnerabilities", "social scoring",
            "criminal assessment", "predictive policing"
        ]
        
        for keyword in prohibited_keywords:
            if keyword in desc_lower:
                assessment["risk_level"] = "Prohibited"
                assessment["reasoning"].append(f"Contains prohibited element: {keyword}")
                assessment["applicable_articles"].append("Article 5 - Prohibited Practices")
                assessment["next_steps"].append("🚫 System cannot be deployed - prohibited under EU AI Act")
                return assessment
        
        # Check for high-risk areas
        high_risk_keywords = {
            "biometric": "Biometric identification systems",
            "recruitment": "Employment and worker management",
            "hiring": "Employment and worker management", 
            "education": "Educational assessment systems",
            "credit": "Access to essential services",
            "loan": "Access to essential services",
            "law enforcement": "Law enforcement applications",
            "border control": "Migration and border control",
            "judicial": "Administration of justice"
        }
        
        for keyword, area in high_risk_keywords.items():
            if keyword in desc_lower:
                assessment["risk_level"] = "High Risk"
                assessment["reasoning"].append(f"Operates in high-risk area: {area}")
                assessment["applicable_articles"].extend([
                    "Article 6 - High-Risk Classification",
                    "Article 16 - Provider Obligations",
                    "Annex III - High-Risk Systems",
                    "Annex IV - Technical Documentation"
                ])
                assessment["next_steps"].extend([
                    "📋 Prepare comprehensive technical documentation",
                    "🔍 Implement risk management system",
                    "👥 Ensure human oversight capabilities",
                    "✅ Complete conformity assessment"
                ])
                break
        
        # Check for limited risk (transparency obligations)
        limited_risk_keywords = ["chatbot", "interact", "recommendation", "content generation"]
        
        for keyword in limited_risk_keywords:
            if keyword in desc_lower and assessment["risk_level"] == "Minimal Risk":
                assessment["risk_level"] = "Limited Risk"
                assessment["reasoning"].append(f"Requires transparency: {keyword} detected")
                assessment["applicable_articles"].append("Article 52 - Transparency Obligations")
                assessment["next_steps"].append("ℹ️ Implement clear AI disclosure to users")
        
        if not assessment["reasoning"]:
            assessment["reasoning"] = ["System appears to be minimal risk based on description"]
            assessment["next_steps"] = ["📖 Review general AI Act compliance requirements"]
        
        return assessment
    
    def create_interface(self):
        """Create the AI Act Explorer interface"""
        
        with gr.Row():
            # Left column - Search and browse
            with gr.Column(scale=2):
                gr.Markdown("## 🔍 **Search EU AI Act**")
                
                # Search interface
                with gr.Row():
                    search_query = gr.Textbox(
                        label="🔍 Search Terms",
                        placeholder="e.g., 'high-risk systems', 'biometric identification', 'technical documentation'",
                        scale=3
                    )
                    category_filter = gr.Dropdown(
                        choices=["All", "Definitions", "Prohibited Practices", "High-Risk Systems", 
                                "Provider Obligations", "Technical Documentation", "General-Purpose AI"],
                        label="📂 Category",
                        value="All",
                        scale=1
                    )
                
                search_btn = gr.Button("🔍 Search Regulation", variant="primary")
                
                # Quick access buttons
                gr.Markdown("### 🚀 **Quick Access**")
                with gr.Row():
                    prohibited_btn = gr.Button("🚫 Prohibited Practices")
                    high_risk_btn = gr.Button("⚠️ High-Risk Systems") 
                    transparency_btn = gr.Button("👁️ Transparency Rules")
                    definitions_btn = gr.Button("📖 Key Definitions")
                
                # Search results
                search_results = gr.HTML(label="Search Results")
            
            # Right column - Analysis tools
            with gr.Column(scale=1):
                gr.Markdown("## 🎯 **AI System Assessment**")
                
                system_input = gr.Textbox(
                    label="📝 Describe Your AI System",
                    placeholder="Describe what your AI system does, who uses it, and in what context...",
                    lines=4
                )
                
                assess_btn = gr.Button("🔍 Assess Risk Level", variant="secondary")
                
                risk_assessment = gr.HTML()
                
                gr.Markdown("## 📅 **Implementation Timeline**")
                timeline_btn = gr.Button("📅 Show Timeline")
                timeline_display = gr.HTML()
        
        # Detailed article view
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 📋 **Regulation Overview**")
                
                if "metadata" in self.ai_act_data:
                    metadata = self.ai_act_data["metadata"]
                    gr.HTML(f"""
                    <div style="background: #1a1a1a; border: 2px solid #3b82f6; border-radius: 12px; padding: 1.5rem; color: #ffffff; margin: 1rem 0;">
                        <h3 style="color: #3b82f6; margin-top: 0;">📜 {metadata.get('title', 'EU AI Act')}</h3>
                        <p><strong>🔗 Official Source:</strong> <a href="{metadata.get('source', '#')}" target="_blank" style="color: #60a5fa;">EUR-Lex Official Text</a></p>
                        <p><strong>📅 Publication:</strong> {metadata.get('publication_date', 'N/A')}</p>
                        <p><strong>⚡ Entry into Force:</strong> {metadata.get('entry_into_force', 'N/A')}</p>
                        <p><strong>📊 Scope:</strong> {metadata.get('scope', 'N/A')}</p>
                        <p><strong>📑 Structure:</strong> {metadata.get('total_articles', 'N/A')} Articles, {metadata.get('total_annexes', 'N/A')} Annexes</p>
                    </div>
                    """)
        
        # Event handlers
        def perform_search(query, category):
            """Handle search requests"""
            if not query.strip():
                return "<p style='color: #9ca3af;'>Please enter search terms to explore the AI Act.</p>"
            
            results = self.search_content(query, category)
            
            if not results:
                return f"<p style='color: #ef4444;'>No results found for '{query}' in {category} category.</p>"
            
            html = f"<div style='background: #1a1a1a; border-radius: 8px; padding: 1rem; color: #ffffff;'>"
            html += f"<h4 style='color: #3b82f6; margin-top: 0;'>🔍 Found {len(results)} results for '{query}'</h4>"
            
            for result in results[:10]:  # Show top 10 results
                risk_color = {"Prohibited": "#dc2626", "High Risk": "#ea580c", "Limited Risk": "#ca8a04"}.get(result.get("risk_level"), "#3b82f6")
                
                html += f"""
                <div style='border: 1px solid #3a3a3a; border-radius: 6px; padding: 1rem; margin: 0.5rem 0; background: #2a2a2a;'>
                    <h5 style='color: {risk_color}; margin: 0 0 0.5rem 0;'>{result.get('title', 'Unknown')}</h5>
                    <p style='margin: 0 0 0.5rem 0; font-size: 0.9rem; color: #cccccc;'><strong>{result.get('article', 'N/A')}</strong> | {result.get('category', 'General')}</p>
                    <p style='margin: 0; color: #e5e7eb; font-size: 0.9rem;'>{result.get('content', '')[:300]}{'...' if len(result.get('content', '')) > 300 else ''}</p>
                </div>
                """
            
            html += "</div>"
            return html
        
        def show_prohibited_practices():
            """Show prohibited AI practices"""
            if "prohibited_practices" not in self.ai_act_data:
                return "<p style='color: #ef4444;'>Prohibited practices data not available.</p>"
            
            practices = self.ai_act_data["prohibited_practices"]["article_5"]["prohibited_systems"]
            
            html = "<div style='background: #1a1a1a; border-radius: 8px; padding: 1rem; color: #ffffff;'>"
            html += "<h4 style='color: #dc2626; margin-top: 0;'>🚫 Prohibited AI Practices (Article 5)</h4>"
            
            for practice in practices:
                html += f"""
                <div style='border: 2px solid #dc2626; border-radius: 6px; padding: 1rem; margin: 0.5rem 0; background: #2a1a1a;'>
                    <h5 style='color: #fca5a5; margin: 0 0 0.5rem 0;'>{practice['id']} - {practice['risk_level']}</h5>
                    <p style='margin: 0 0 0.5rem 0; color: #e5e7eb;'>{practice['description']}</p>
                    <p style='margin: 0; color: #d1d5db; font-size: 0.85rem; font-style: italic;'><strong>Purpose:</strong> {practice.get('purpose', 'N/A')}</p>
                </div>
                """
            
            html += "</div>"
            return html
        
        def show_high_risk_systems():
            """Show high-risk AI systems from Annex III"""
            if "high_risk_systems" not in self.ai_act_data:
                return "<p style='color: #ef4444;'>High-risk systems data not available.</p>"
            
            categories = self.ai_act_data["high_risk_systems"]["annex_iii"]["categories"]
            
            html = "<div style='background: #1a1a1a; border-radius: 8px; padding: 1rem; color: #ffffff;'>"
            html += "<h4 style='color: #ea580c; margin-top: 0;'>⚠️ High-Risk AI Systems (Annex III)</h4>"
            
            for category in categories:
                html += f"""
                <div style='border: 2px solid #ea580c; border-radius: 6px; padding: 1rem; margin: 0.5rem 0; background: #2a1a1a;'>
                    <h5 style='color: #fdba74; margin: 0 0 0.5rem 0;'>{category['id']}. {category['area']}</h5>
                    <ul style='margin: 0; color: #e5e7eb; padding-left: 1.5rem;'>
                """
                
                for system in category['systems']:
                    html += f"<li style='margin: 0.25rem 0;'>{system}</li>"
                
                html += """
                    </ul>
                </div>
                """
            
            html += "</div>"
            return html
        
        def show_transparency_obligations():
            """Show transparency obligations"""
            if "transparency_obligations" not in self.ai_act_data:
                return "<p style='color: #ef4444;'>Transparency obligations data not available.</p>"
            
            requirements = self.ai_act_data["transparency_obligations"]["article_52"]["requirements"]
            
            html = "<div style='background: #1a1a1a; border-radius: 8px; padding: 1rem; color: #ffffff;'>"
            html += "<h4 style='color: #ca8a04; margin-top: 0;'>👁️ Transparency Obligations (Article 52)</h4>"
            
            for req in requirements:
                html += f"""
                <div style='border: 2px solid #ca8a04; border-radius: 6px; padding: 1rem; margin: 0.5rem 0; background: #1a1a1a;'>
                    <h5 style='color: #fbbf24; margin: 0 0 0.5rem 0;'>{req['type']}</h5>
                    <p style='margin: 0; color: #e5e7eb;'>{req['obligation']}</p>
                </div>
                """
            
            html += "</div>"
            return html
        
        def show_key_definitions():
            """Show key AI Act definitions"""
            if "key_definitions" not in self.ai_act_data:
                return "<p style='color: #ef4444;'>Definitions data not available.</p>"
            
            terms = self.ai_act_data["key_definitions"]["article_3"]["key_terms"]
            
            html = "<div style='background: #1a1a1a; border-radius: 8px; padding: 1rem; color: #ffffff;'>"
            html += "<h4 style='color: #3b82f6; margin-top: 0;'>📖 Key Definitions (Article 3)</h4>"
            
            for term, definition in terms.items():
                display_term = term.replace('_', ' ').title()
                html += f"""
                <div style='border: 2px solid #3b82f6; border-radius: 6px; padding: 1rem; margin: 0.5rem 0; background: #1a2a2a;'>
                    <h5 style='color: #60a5fa; margin: 0 0 0.5rem 0;'>{display_term}</h5>
                    <p style='margin: 0; color: #e5e7eb;'>{definition}</p>
                </div>
                """
            
            html += "</div>"
            return html
        
        def perform_risk_assessment(description):
            """Perform AI system risk assessment"""
            assessment = self.assess_ai_system_risk(description)
            
            risk_colors = {
                "Prohibited": "#dc2626",
                "High Risk": "#ea580c", 
                "Limited Risk": "#ca8a04",
                "Minimal Risk": "#16a34a",
                "Unknown": "#6b7280"
            }
            
            color = risk_colors.get(assessment["risk_level"], "#6b7280")
            
            html = f"<div style='background: #1a1a1a; border: 2px solid {color}; border-radius: 8px; padding: 1rem; color: #ffffff;'>"
            html += f"<h4 style='color: {color}; margin-top: 0;'>🎯 Risk Assessment: {assessment['risk_level']}</h4>"
            
            html += "<h5 style='color: #e5e7eb; margin: 1rem 0 0.5rem 0;'>📋 Analysis:</h5>"
            html += "<ul style='color: #d1d5db; margin: 0 0 1rem 0; padding-left: 1.5rem;'>"
            for reason in assessment["reasoning"]:
                html += f"<li>{reason}</li>"
            html += "</ul>"
            
            if assessment["applicable_articles"]:
                html += "<h5 style='color: #e5e7eb; margin: 1rem 0 0.5rem 0;'>📖 Applicable Articles:</h5>"
                html += "<ul style='color: #d1d5db; margin: 0 0 1rem 0; padding-left: 1.5rem;'>"
                for article in assessment["applicable_articles"]:
                    html += f"<li>{article}</li>"
                html += "</ul>"
            
            if assessment["next_steps"]:
                html += "<h5 style='color: #e5e7eb; margin: 1rem 0 0.5rem 0;'>🎯 Recommended Next Steps:</h5>"
                html += "<ul style='color: #d1d5db; margin: 0; padding-left: 1.5rem;'>"
                for step in assessment["next_steps"]:
                    html += f"<li>{step}</li>"
                html += "</ul>"
            
            html += "</div>"
            return html
        
        def show_implementation_timeline():
            """Show AI Act implementation timeline"""
            timeline = self.get_compliance_timeline()
            
            if not timeline:
                return "<p style='color: #ef4444;'>Timeline data not available.</p>"
            
            html = "<div style='background: #1a1a1a; border-radius: 8px; padding: 1rem; color: #ffffff;'>"
            html += "<h4 style='color: #3b82f6; margin-top: 0;'>📅 EU AI Act Implementation Timeline</h4>"
            
            for milestone in timeline:
                if "remaining" in milestone["status"]:
                    color = "#ca8a04"  # Upcoming
                elif "overdue" in milestone["status"]:
                    color = "#dc2626"  # Overdue
                else:
                    color = "#16a34a"  # Implemented
                
                html += f"""
                <div style='border-left: 4px solid {color}; padding: 1rem; margin: 0.5rem 0; background: #2a2a2a;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <h5 style='color: #e5e7eb; margin: 0;'>{milestone['date']}</h5>
                        <span style='color: {color}; font-weight: bold;'>{milestone['status']}</span>
                    </div>
                    <p style='margin: 0.5rem 0 0 0; color: #d1d5db;'>{milestone['milestone']}</p>
                </div>
                """
            
            html += "</div>"
            return html
        
        # Connect event handlers
        search_btn.click(
            fn=perform_search,
            inputs=[search_query, category_filter],
            outputs=[search_results]
        )
        
        prohibited_btn.click(
            fn=show_prohibited_practices,
            inputs=[],
            outputs=[search_results]
        )
        
        high_risk_btn.click(
            fn=show_high_risk_systems,
            inputs=[],
            outputs=[search_results]
        )
        
        transparency_btn.click(
            fn=show_transparency_obligations,
            inputs=[],
            outputs=[search_results]
        )
        
        definitions_btn.click(
            fn=show_key_definitions,
            inputs=[],
            outputs=[search_results]
        )
        
        assess_btn.click(
            fn=perform_risk_assessment,
            inputs=[system_input],
            outputs=[risk_assessment]
        )
        
        timeline_btn.click(
            fn=show_implementation_timeline,
            inputs=[],
            outputs=[timeline_display]
        ) 