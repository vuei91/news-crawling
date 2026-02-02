# -*- coding: utf-8 -*-
"""
이메일 전송 모듈
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os


class EmailSender:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def send_articles_email(self, articles, recipient_email, target_date):
        """기사 목록을 HTML 이메일로 전송"""
        try:
            # 이메일 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"한미일보 기사 모음 - {target_date.strftime('%Y년 %m월 %d일')}"
            
            # HTML 본문 생성
            html_body = self._create_html_body(articles, target_date)
            
            # HTML 파트 추가
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # SMTP 서버 연결 및 전송
            print(f"\n이메일 전송 중... ({self.smtp_server}:{self.smtp_port})")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # TLS 암호화
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✓ 이메일 전송 완료: {recipient_email}")
            return True
            
        except Exception as e:
            print(f"✗ 이메일 전송 실패: {e}")
            return False
    
    def _create_html_body(self, articles, target_date):
        """HTML 이메일 본문 생성"""
        date_str = target_date.strftime('%Y년 %m월 %d일')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: 'Malgun Gothic', '맑은 고딕', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                    margin-bottom: 30px;
                }}
                .summary {{
                    background-color: #ecf0f1;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 30px;
                }}
                .article {{
                    margin-bottom: 40px;
                    padding-bottom: 30px;
                    border-bottom: 1px solid #e0e0e0;
                }}
                .article:last-child {{
                    border-bottom: none;
                }}
                .article-number {{
                    display: inline-block;
                    background-color: #3498db;
                    color: white;
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 14px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .article-title {{
                    font-size: 22px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin: 10px 0;
                }}
                .article-meta {{
                    color: #7f8c8d;
                    font-size: 14px;
                    margin: 10px 0;
                }}
                .article-content {{
                    margin: 15px 0;
                    line-height: 1.8;
                    color: #555;
                    white-space: pre-wrap;
                }}
                .article-link {{
                    display: inline-block;
                    margin-top: 10px;
                    padding: 8px 15px;
                    background-color: #3498db;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-size: 14px;
                }}
                .article-link:hover {{
                    background-color: #2980b9;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 2px solid #e0e0e0;
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📰 한미일보 기사 모음</h1>
                
                <div class="summary">
                    <strong>날짜:</strong> {date_str}<br>
                    <strong>총 기사 수:</strong> {len(articles)}개<br>
                    <strong>수집 시간:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>
        """
        
        # 각 기사 추가
        for idx, article in enumerate(articles, 1):
            title = article.get('title', '제목 없음')
            author = article.get('author', '저자 미상')
            date = article.get('date', '날짜 미상')
            content = article.get('content', '본문 없음')
            url = article.get('url', '#')
            
            # 본문이 너무 길면 요약
            if len(content) > 500:
                content = content[:500] + '...'
            
            html += f"""
                <div class="article">
                    <span class="article-number">기사 {idx}</span>
                    <div class="article-title">{title}</div>
                    <div class="article-meta">
                        <strong>저자:</strong> {author} | <strong>등록:</strong> {date}
                    </div>
                    <div class="article-content">{content}</div>
                    <a href="{url}" class="article-link" target="_blank">전체 기사 보기 →</a>
                </div>
            """
        
        html += """
                <div class="footer">
                    이 이메일은 한미일보 기사 크롤러에 의해 자동으로 생성되었습니다.
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


# Gmail 설정 예시
GMAIL_SMTP = "smtp.gmail.com"
GMAIL_PORT = 587

# Naver 설정 예시
NAVER_SMTP = "smtp.naver.com"
NAVER_PORT = 587

# Outlook/Hotmail 설정 예시
OUTLOOK_SMTP = "smtp-mail.outlook.com"
OUTLOOK_PORT = 587
