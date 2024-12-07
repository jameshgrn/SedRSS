from typing import List, Dict, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from jinja2 import Template

class EmailSender:
    def __init__(self, smtp_config: Dict[str, str]):
        """Initialize email sender with SMTP configuration"""
        self.config = smtp_config
        self.logger = logging.getLogger(__name__)
        
        # Load email template
        self.template = Template("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        line-height: 1.6;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                    }
                    .header { 
                        color: #2c3e50;
                        border-bottom: 2px solid #3498db;
                        padding-bottom: 10px;
                    }
                    .article { 
                        margin: 20px 0; 
                        padding: 15px;
                        border-bottom: 1px solid #eee;
                        background-color: #f9f9f9;
                    }
                    .title { 
                        color: #2980b9;
                        text-decoration: none;
                        font-weight: bold;
                    }
                    .title:hover {
                        text-decoration: underline;
                    }
                    .journal { 
                        color: #7f8c8d;
                        font-style: italic;
                        margin: 5px 0;
                    }
                    .summary { 
                        margin: 10px 0;
                        color: #34495e;
                    }
                    .footer { 
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #eee;
                        color: #7f8c8d;
                        font-size: 0.9em;
                        text-align: center;
                    }
                    .date {
                        color: #95a5a6;
                        font-size: 0.9em;
                    }
                    .other-articles {
                        list-style-type: none;
                        padding: 0;
                    }
                    .other-articles li {
                        margin: 10px 0;
                        padding: 5px 0;
                    }
                </style>
            </head>
            <body>
                <h1 class="header">SedRSS Newsletter</h1>
                <p class="date">{{ date }}</p>
                
                <h2>Featured Articles</h2>
                {% for article in featured_articles %}
                <div class="article">
                    <h3><a href="{{ article.url }}" class="title">{{ article.title }}</a></h3>
                    <div class="journal">{{ article.journal }}</div>
                    <div class="summary">{{ article.summary }}</div>
                </div>
                {% endfor %}
                
                <h3>Other Recent Publications</h3>
                <ul class="other-articles">
                {% for article in other_articles %}
                    <li>
                        <a href="{{ article.url }}" class="title">{{ article.title }}</a>
                        <div class="journal">{{ article.journal }}</div>
                    </li>
                {% endfor %}
                </ul>
                
                <div class="footer">
                    <p>SedRSS - Keeping you updated on sedimentology and geomorphology research</p>
                    <p>To unsubscribe, reply with 'unsubscribe' in the subject line</p>
                </div>
            </body>
            </html>
        """)
    
    async def send(self, 
                  subject: str,
                  content: Dict[str, List[Dict]],
                  recipients: List[str]) -> None:
        """
        Send newsletter email
        
        Args:
            subject: Email subject
            content: Dict with 'featured_articles' and 'other_articles' lists
            recipients: List of email addresses
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config['username']
            msg['To'] = ', '.join(recipients)
            
            # Render HTML content
            html_content = self.template.render(
                date=datetime.now().strftime('%B %d, %Y'),
                **content
            )
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(self.config['host'], int(self.config['port'])) as server:
                server.starttls()
                server.login(self.config['username'], self.config['password'])
                server.send_message(msg)
                
            self.logger.info(f"Newsletter sent successfully to {len(recipients)} recipients")
            
        except Exception as e:
            self.logger.error(f"Failed to send newsletter: {str(e)}")
            raise