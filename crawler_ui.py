# -*- coding: utf-8 -*-
"""
한미일보 크롤러 GUI
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import date, datetime
import threading
import asyncio
import sys
import platform
import os

# 윈도우 콘솔 UTF-8 인코딩 설정 (PyInstaller 호환)
if platform.system() == "Windows":
    try:
        if sys.stdout is not None and hasattr(sys.stdout, 'encoding') and sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stderr is not None and hasattr(sys.stderr, 'encoding') and sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass  # PyInstaller 환경에서는 무시

from hanmi_crawler import HanmiCrawler


class CrawlerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("한미일보 기사 크롤러")
        self.root.geometry("800x750")
        self.root.resizable(False, False)
        
        # 크롤링 중 플래그
        self.is_crawling = False
        
        # 플랫폼별 폰트 설정
        self.font_family = self._get_platform_font()
        
        self._create_widgets()
    
    def _get_platform_font(self):
        """플랫폼에 맞는 폰트 반환"""
        system = platform.system()
        if system == "Darwin":  # macOS
            return "AppleGothic"
        elif system == "Windows":
            return "맑은 고딕"
        else:  # Linux
            return "NanumGothic"
    
    def _create_widgets(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(
            main_frame, 
            text="한미일보 기사 크롤러",
            font=(self.font_family, 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 날짜 선택 프레임
        date_frame = ttk.LabelFrame(main_frame, text="크롤링 설정", padding="10")
        date_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 날짜 선택
        ttk.Label(date_frame, text="날짜:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.date_var = tk.StringVar(value="오늘")
        date_radio_frame = ttk.Frame(date_frame)
        date_radio_frame.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Radiobutton(
            date_radio_frame, 
            text="오늘", 
            variable=self.date_var, 
            value="오늘"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            date_radio_frame, 
            text="어제", 
            variable=self.date_var, 
            value="어제"
        ).pack(side=tk.LEFT)
        
        # 기사 개수
        ttk.Label(date_frame, text="최대 기사 수:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        self.max_articles_var = tk.StringVar(value="10")
        max_articles_spinbox = ttk.Spinbox(
            date_frame,
            from_=1,
            to=50,
            textvariable=self.max_articles_var,
            width=10
        )
        max_articles_spinbox.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # 이메일 설정 프레임
        email_frame = ttk.LabelFrame(main_frame, text="이메일 설정", padding="10")
        email_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 이메일 전송 여부
        self.send_email_var = tk.BooleanVar(value=False)
        email_check = ttk.Checkbutton(
            email_frame,
            text="이메일로 전송",
            variable=self.send_email_var,
            command=self.toggle_email_fields
        )
        email_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # SMTP 서버
        ttk.Label(email_frame, text="SMTP 서버:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.smtp_server_var = tk.StringVar(value="smtp.gmail.com")
        self.smtp_server_entry = ttk.Entry(email_frame, textvariable=self.smtp_server_var, width=30, state=tk.DISABLED)
        self.smtp_server_entry.grid(row=1, column=1, sticky=tk.W)
        
        # SMTP 포트
        ttk.Label(email_frame, text="SMTP 포트:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.smtp_port_var = tk.StringVar(value="587")
        self.smtp_port_entry = ttk.Entry(email_frame, textvariable=self.smtp_port_var, width=30, state=tk.DISABLED)
        self.smtp_port_entry.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        
        # 발신 이메일
        ttk.Label(email_frame, text="발신 이메일:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.sender_email_var = tk.StringVar()
        self.sender_email_entry = ttk.Entry(email_frame, textvariable=self.sender_email_var, width=30, state=tk.DISABLED)
        self.sender_email_entry.grid(row=3, column=1, sticky=tk.W, pady=(5, 0))
        
        # 발신 비밀번호
        ttk.Label(email_frame, text="앱 비밀번호:").grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.sender_password_var = tk.StringVar()
        self.sender_password_entry = ttk.Entry(email_frame, textvariable=self.sender_password_var, width=30, show="*", state=tk.DISABLED)
        self.sender_password_entry.grid(row=4, column=1, sticky=tk.W, pady=(5, 0))
        
        # 수신 이메일
        ttk.Label(email_frame, text="수신 이메일:").grid(row=5, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.recipient_email_var = tk.StringVar()
        self.recipient_email_entry = ttk.Entry(email_frame, textvariable=self.recipient_email_var, width=30, state=tk.DISABLED)
        self.recipient_email_entry.grid(row=5, column=1, sticky=tk.W, pady=(5, 0))
        
        # 도움말 레이블
        help_label = ttk.Label(
            email_frame,
            text="※ Gmail 사용 시 '앱 비밀번호'를 생성해야 합니다 (2단계 인증 필요)",
            font=(self.font_family, 8),
            foreground="gray"
        )
        help_label.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # 크롤링 버튼
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(
            button_frame,
            text="크롤링 시작",
            command=self.start_crawling,
            width=20
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="중지",
            command=self.stop_crawling,
            state=tk.DISABLED,
            width=20
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 진행 상황 표시
        progress_frame = ttk.LabelFrame(main_frame, text="진행 상황", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 로그 텍스트 영역
        self.log_text = scrolledtext.ScrolledText(
            progress_frame,
            width=80,
            height=15,
            wrap=tk.WORD,
            font=(self.font_family, 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 상태 표시
        self.status_label = ttk.Label(
            main_frame,
            text="대기 중...",
            font=(self.font_family, 10)
        )
        self.status_label.grid(row=5, column=0, columnspan=2, pady=(10, 0))
    
    def toggle_email_fields(self):
        """이메일 필드 활성화/비활성화"""
        if self.send_email_var.get():
            self.smtp_server_entry.config(state=tk.NORMAL)
            self.smtp_port_entry.config(state=tk.NORMAL)
            self.sender_email_entry.config(state=tk.NORMAL)
            self.sender_password_entry.config(state=tk.NORMAL)
            self.recipient_email_entry.config(state=tk.NORMAL)
        else:
            self.smtp_server_entry.config(state=tk.DISABLED)
            self.smtp_port_entry.config(state=tk.DISABLED)
            self.sender_email_entry.config(state=tk.DISABLED)
            self.sender_password_entry.config(state=tk.DISABLED)
            self.recipient_email_entry.config(state=tk.DISABLED)
    
    def log(self, message):
        """로그 메시지 추가"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def start_crawling(self):
        """크롤링 시작"""
        if self.is_crawling:
            return
        
        # 이메일 전송 시 필수 필드 검증
        if self.send_email_var.get():
            if not all([
                self.smtp_server_var.get(),
                self.smtp_port_var.get(),
                self.sender_email_var.get(),
                self.sender_password_var.get(),
                self.recipient_email_var.get()
            ]):
                messagebox.showerror("오류", "이메일 설정의 모든 필드를 입력해주세요.")
                return
        
        # 버튼 상태 변경
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_crawling = True
        
        # 로그 초기화
        self.log_text.delete(1.0, tk.END)
        self.status_label.config(text="크롤링 중...")
        
        # 날짜 설정
        if self.date_var.get() == "오늘":
            target_date = date.today()
        else:  # 어제
            from datetime import timedelta
            target_date = date.today() - timedelta(days=1)
        
        # 최대 기사 수
        try:
            max_articles = int(self.max_articles_var.get())
        except:
            max_articles = 10
        
        # 이메일 설정
        email_config = None
        if self.send_email_var.get():
            email_config = {
                'smtp_server': self.smtp_server_var.get(),
                'smtp_port': int(self.smtp_port_var.get()),
                'sender_email': self.sender_email_var.get(),
                'sender_password': self.sender_password_var.get(),
                'recipient_email': self.recipient_email_var.get()
            }
        
        # 별도 스레드에서 크롤링 실행
        thread = threading.Thread(
            target=self.run_crawler,
            args=(target_date, max_articles, email_config),
            daemon=True
        )
        thread.start()
    
    def run_crawler(self, target_date, max_articles, email_config=None):
        """크롤러 실행 (별도 스레드)"""
        try:
            # 새로운 이벤트 루프 생성
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            self.log(f"크롤링 시작: {target_date.strftime('%Y-%m-%d')}")
            self.log(f"최대 기사 수: {max_articles}개")
            if email_config:
                self.log(f"이메일 전송: {email_config['recipient_email']}\n")
            else:
                self.log("파일 저장 모드\n")
            
            # 크롤러 실행
            crawler = HanmiCrawler(target_date=target_date)
            
            # 크롤러의 print를 로그로 리다이렉트
            import sys
            from io import StringIO
            
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            loop.run_until_complete(crawler.run(max_articles=max_articles, use_list_page=True, email_config=email_config))
            
            # 출력 내용 가져오기
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            # 로그에 출력
            for line in output.split('\n'):
                if line.strip():
                    self.log(line)
            
            self.log("\n✅ 크롤링 완료!")
            self.status_label.config(text="완료!")
            
            if email_config:
                messagebox.showinfo(
                    "완료",
                    f"크롤링이 완료되었습니다!\n수집된 기사: {len(crawler.articles)}개\n이메일 전송: {email_config['recipient_email']}"
                )
            else:
                messagebox.showinfo(
                    "완료",
                    f"크롤링이 완료되었습니다!\n수집된 기사: {len(crawler.articles)}개"
                )
            
        except Exception as e:
            self.log(f"\n❌ 오류 발생: {str(e)}")
            self.status_label.config(text="오류 발생")
            messagebox.showerror("오류", f"크롤링 중 오류가 발생했습니다:\n{str(e)}")
        
        finally:
            # 버튼 상태 복원
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.is_crawling = False
            loop.close()
    
    def stop_crawling(self):
        """크롤링 중지"""
        if self.is_crawling:
            self.log("\n⚠️ 크롤링 중지 요청...")
            self.status_label.config(text="중지 중...")
            # 실제 중지는 구현하지 않음 (복잡도 증가)
            messagebox.showinfo("알림", "현재 진행 중인 작업이 완료될 때까지 기다려주세요.")


def main():
    # PyInstaller 멀티프로세싱 지원
    import multiprocessing
    multiprocessing.freeze_support()
    
    root = tk.Tk()
    app = CrawlerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
