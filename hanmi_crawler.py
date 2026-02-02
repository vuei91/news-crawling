# -*- coding: utf-8 -*-
"""
한미일보 기사 크롤러
"""
import asyncio
import json
from datetime import datetime, date
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re
import pandas as pd
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

from openpyxl.styles import Alignment, Font


class HanmiCrawler:
    def __init__(self, target_date=None):
        self.base_url = "https://www.hanmiilbo.kr"
        self.articles = []
        # 타겟 날짜 설정 (기본값: 오늘)
        self.target_date = target_date if target_date else date.today()
        print(f"크롤링 대상 날짜: {self.target_date.strftime('%Y-%m-%d')}")
    
    def _get_browser_path(self):
        """Playwright 브라우저 경로 찾기 (PyInstaller 환경 지원)"""
        try:
            # PyInstaller로 패키징된 경우
            if getattr(sys, 'frozen', False):
                # EXE 실행 시 임시 폴더에서 브라우저 찾기
                base_path = sys._MEIPASS
                
                # ms-playwright 폴더 찾기
                ms_playwright = os.path.join(base_path, 'ms-playwright')
                if os.path.exists(ms_playwright):
                    for item in os.listdir(ms_playwright):
                        if 'chromium' in item.lower():
                            browser_path = os.path.join(ms_playwright, item)
                            print(f"✓ 패키징된 Chromium 발견: {browser_path}")
                            return browser_path
                
                # playwright/driver 폴더 찾기
                driver_path = os.path.join(base_path, 'playwright', 'driver')
                if os.path.exists(driver_path):
                    print(f"✓ Playwright 드라이버 발견: {driver_path}")
                    # 환경 변수 설정
                    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.join(base_path, 'ms-playwright')
            
            # 일반 실행 환경
            else:
                # 기본 Playwright 브라우저 경로 사용
                pass
            
            return None
        except Exception as e:
            print(f"브라우저 경로 확인 중 오류: {e}")
            return None
    
    async def crawl_list_page(self, page, list_url, max_articles=10):
        """카테고리 목록 페이지에서 기사 목록 수집 (날짜 필터링 포함)"""
        print(f"\n목록 페이지 접속 중: {list_url}")
        await page.goto(list_url, wait_until="networkidle")
        await asyncio.sleep(2)
        
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        article_links = []
        target_date_str = self.target_date.strftime('%Y-%m-%d')
        
        # li 태그 안에 링크와 날짜가 함께 있음
        for li in soup.find_all('li'):
            # 링크 찾기
            link = li.find('a', href=True)
            if not link:
                continue
            
            href = link['href']
            if 'view.php' not in href or 'idx=' not in href:
                continue
            
            # 같은 li 안에서 날짜 찾기 (dd.registDate)
            date_dd = li.find('dd', class_=lambda x: x and 'registDate' in x)
            if date_dd:
                date_str = date_dd.get_text(strip=True)
                
                # 타겟 날짜와 일치하는 경우만 수집
                if date_str == target_date_str:
                    # 상대 경로를 절대 경로로 변환
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('/'):
                        full_url = self.base_url + href
                    else:
                        full_url = self.base_url + '/' + href
                    
                    # mcode 파라미터 제거 (중복 방지)
                    if '&mcode=' in full_url:
                        full_url = full_url.split('&mcode=')[0]
                    
                    if full_url not in article_links:
                        # 제목 추출
                        title_dt = li.find('dt', class_=lambda x: x and 'title' in x)
                        if title_dt:
                            title_link = title_dt.find('a')
                            title = title_link.get_text(strip=True) if title_link else "제목 없음"
                        else:
                            title = "제목 없음"
                        
                        print(f"  ✓ 오늘 날짜 기사 발견: {title[:50]}... (날짜: {date_str})")
                        article_links.append(full_url)
                        
                        if len(article_links) >= max_articles:
                            break
        
        return article_links
    
    async def crawl_article_list(self, page, max_articles=10):
        """메인 페이지에서 기사 목록 수집 (날짜 필터링 포함)"""
        print(f"메인 페이지 접속 중: {self.base_url}")
        await page.goto(self.base_url, wait_until="networkidle")
        await asyncio.sleep(2)  # 페이지 로딩 대기
        
        # 페이지 HTML 가져오기
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # 기사 링크와 날짜 정보를 함께 수집
        article_links = []
        target_date_str = self.target_date.strftime('%Y-%m-%d')
        
        # tab_item 클래스를 가진 li 태그 찾기
        for li in soup.find_all('li', class_=lambda x: x and 'tab_item' in x):
            # 링크 찾기
            link = li.find('a', href=True)
            if not link:
                continue
            
            href = link['href']
            if 'view.php' not in href or 'idx=' not in href:
                continue
            
            # 같은 li 안에서 날짜 찾기 (span.tab_data > time.time)
            time_tag = li.find('time', class_=lambda x: x and 'time' in x)
            if time_tag:
                date_str = time_tag.get_text(strip=True)
                
                # 타겟 날짜와 일치하는 경우만 수집
                if date_str == target_date_str:
                    # 상대 경로를 절대 경로로 변환
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('/'):
                        full_url = self.base_url + href
                    else:
                        full_url = self.base_url + '/' + href
                    
                    if full_url not in article_links:
                        # 제목 추출
                        title_tag = li.find('strong', class_=lambda x: x and 'headline' in x)
                        title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
                        print(f"  ✓ 오늘 날짜 기사 발견: {title[:50]}... (날짜: {date_str})")
                        article_links.append(full_url)
                        
                        if len(article_links) >= max_articles:
                            break
        
        print(f"\n오늘 날짜({target_date_str}) 기사 {len(article_links)}개 발견")
        return article_links
    
    def _is_target_date(self, article_date_str):
        """기사 날짜가 타겟 날짜인지 확인"""
        if not article_date_str:
            return False
        
        try:
            # "2026-02-01 14:14:16" 형식에서 날짜 부분만 추출
            date_part = article_date_str.split()[0]
            article_date = datetime.strptime(date_part, '%Y-%m-%d').date()
            return article_date == self.target_date
        except:
            return False
    
    async def crawl_article_detail(self, page, url):
        """개별 기사 상세 정보 수집"""
        try:
            print(f"\n기사 크롤링 중: {url}")
            await page.goto(url, wait_until="networkidle")
            await asyncio.sleep(1)
            
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # 기사 정보 추출
            article = {
                'url': url,
                'title': self._extract_title(soup),
                'content': self._extract_content(soup),
                'date': self._extract_date(soup),
                'author': self._extract_author(soup),
                'crawled_at': datetime.now().isoformat()
            }
            
            print(f"  ✓ 수집 완료: {article['title'][:50]}")
            return article
        except Exception as e:
            print(f"  ✗ 크롤링 실패: {e}")
            return None
    
    def _extract_title(self, soup):
        """제목 추출"""
        # og:title 메타 태그에서 추출
        meta_title = soup.find('meta', {'property': 'og:title'})
        if meta_title and meta_title.get('content'):
            return meta_title['content']
        
        # title 태그에서 추출
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        return "제목 없음"
    
    def _extract_content(self, soup):
        """본문 추출"""
        # fr-view 클래스에서 본문 추출
        content_div = soup.find('div', {'class': 'fr-view'})
        if content_div:
            # 스크립트, 스타일 태그 제거
            for script in content_div(['script', 'style', 'img']):
                script.decompose()
            return content_div.get_text(strip=True, separator='\n')
        
        # viewContent 클래스 시도
        content_div = soup.find('div', {'class': 'viewContent'})
        if content_div:
            for script in content_div(['script', 'style']):
                script.decompose()
            return content_div.get_text(strip=True, separator='\n')
        
        return "본문 없음"
    
    def _extract_date(self, soup):
        """날짜 추출"""
        # 기사 정보 영역에서 "등록 YYYY-MM-DD HH:MM:SS" 형식 찾기
        info_list = soup.find('ul', class_=lambda x: x and 'info-text' in x)
        if info_list:
            for li in info_list.find_all('li'):
                text = li.get_text(strip=True)
                # "등록 2026-02-01 14:14:16" 형식 파싱
                match = re.search(r'등록\s+(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})', text)
                if match:
                    return f"{match.group(1)} {match.group(2)}"
        
        # article:published_time 메타 태그
        meta_date = soup.find('meta', {'property': 'article:published_time'})
        if meta_date and meta_date.get('content'):
            return meta_date['content']
        
        # time 태그
        time_tag = soup.find('time')
        if time_tag:
            return time_tag.get_text(strip=True)
        
        return None
    
    def _extract_author(self, soup):
        """저자 추출"""
        # 기사 정보 영역에서 기자 이름 찾기 (info-text 클래스)
        info_list = soup.find('ul', class_=lambda x: x and 'info-text' in x)
        if info_list:
            for li in info_list.find_all('li'):
                text = li.get_text(strip=True)
                # "김영 기자" 형식 찾기
                if '기자' in text and '등록' not in text:
                    return text
        
        # 기사 하단의 프로필 영역에서 찾기
        writer_strong = soup.find('strong', class_=lambda x: x and 'writer' in x)
        if writer_strong:
            return writer_strong.get_text(strip=True)
        
        # author 메타 태그
        meta_author = soup.find('meta', {'name': 'author'})
        if meta_author and meta_author.get('content'):
            return meta_author['content']
        
        # 일반적인 저자 표시 영역
        author_span = soup.find('span', {'class': ['author', 'reporter', 'writer']})
        if author_span:
            return author_span.get_text(strip=True)
        
        return None
    
    async def run(self, max_articles=10, use_list_page=True, email_config=None):
        """크롤러 실행"""
        # PyInstaller 환경에서 브라우저 경로 설정
        self._get_browser_path()
        
        async with async_playwright() as p:
            # 브라우저 실행
            try:
                browser = await p.chromium.launch(headless=True)
            except Exception as e:
                error_msg = str(e)
                if "Executable doesn't exist" in error_msg or "browser" in error_msg.lower():
                    raise Exception(
                        "Playwright 브라우저가 설치되어 있지 않습니다.\n\n"
                        "설치 방법:\n"
                        "1. 명령 프롬프트(cmd)를 관리자 권한으로 실행\n"
                        "2. 다음 명령어 입력:\n"
                        "   playwright install chromium\n\n"
                        "또는 install_browser.bat 파일을 실행하세요."
                    )
                else:
                    raise e
            
            page = await browser.new_page()
            
            try:
                article_urls = []
                
                if use_list_page:
                    # 카테고리 목록 페이지에서 수집 (더 많은 기사 확인 가능)
                    list_url = f"{self.base_url}/news/list.php?mcode=m93atmw"
                    article_urls = await self.crawl_list_page(page, list_url, max_articles)
                else:
                    # 메인 페이지에서 수집
                    article_urls = await self.crawl_article_list(page, max_articles)
                
                if not article_urls:
                    print(f"\n오늘 날짜({self.target_date.strftime('%Y-%m-%d')})의 기사를 찾지 못했습니다.")
                    return
                
                # 각 기사 상세 정보 수집
                print(f"\n기사 상세 정보 수집 시작... (총 {len(article_urls)}개)")
                for url in article_urls:
                    article = await self.crawl_article_detail(page, url)
                    if article:
                        self.articles.append(article)
                    await asyncio.sleep(1)  # 서버 부하 방지
                
                # 결과 저장 또는 이메일 전송
                if self.articles:
                    if email_config:
                        self.send_email(email_config)
                    else:
                        self.save_results()
                
            finally:
                await browser.close()
    
    def save_results(self):
        """결과를 JSON과 엑셀 파일로 저장"""
        date_str = self.target_date.strftime('%Y%m%d')
        timestamp = datetime.now().strftime('%H%M%S')
        
        # JSON 파일 저장
        json_filename = f"hanmi_articles_{date_str}_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=2)
        print(f"\n✓ JSON 파일 저장 완료: {json_filename}")
        
        # 엑셀 파일 저장
        excel_filename = f"hanmi_articles_{date_str}_{timestamp}.xlsx"
        self._save_to_excel(excel_filename)
        print(f"✓ 엑셀 파일 저장 완료: {excel_filename}")
        print(f"\n총 {len(self.articles)}개 기사 저장됨")
    
    def _save_to_excel(self, filename):
        """엑셀 파일로 저장"""
        # 데이터프레임 생성
        df = pd.DataFrame(self.articles)
        
        # 열 순서 재정렬
        df = df[['title', 'author', 'date', 'content', 'url', 'crawled_at']]
        
        # 열 이름 한글로 변경
        df.columns = ['제목', '저자', '등록일시', '본문', 'URL', '크롤링일시']
        
        # 엑셀 writer 생성
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='기사목록', index=False)
            
            # 워크시트 가져오기
            worksheet = writer.sheets['기사목록']
            
            # 헤더 스타일 적용
            header_font = Font(bold=True, size=11)
            for cell in worksheet[1]:
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # 열 너비 조정
            worksheet.column_dimensions['A'].width = 50  # 제목
            worksheet.column_dimensions['B'].width = 25  # 저자
            worksheet.column_dimensions['C'].width = 20  # 등록일시
            worksheet.column_dimensions['D'].width = 120 # 본문
            worksheet.column_dimensions['E'].width = 60  # URL
            worksheet.column_dimensions['F'].width = 20  # 크롤링일시
            
            # 모든 셀에 텍스트 줄바꿈 적용
            for row in worksheet.iter_rows(min_row=2, max_row=len(df)+1):
                for cell in row:
                    # 텍스트 줄바꿈 활성화
                    cell.alignment = Alignment(
                        wrap_text=True,
                        vertical='top',
                        horizontal='left'
                    )
                
                # 행 높이를 본문 길이에 따라 조정
                content_cell = row[3]  # 본문 셀 (D열)
                if content_cell.value:
                    # 본문 길이에 따라 행 높이 계산
                    content_length = len(str(content_cell.value))
                    estimated_lines = max(3, content_length // 120)
                    worksheet.row_dimensions[cell.row].height = min(estimated_lines * 15, 400)
    
    def send_email(self, email_config):
        """이메일로 기사 전송"""
        from email_sender import EmailSender
        
        try:
            sender = EmailSender(
                smtp_server=email_config['smtp_server'],
                smtp_port=email_config['smtp_port'],
                sender_email=email_config['sender_email'],
                sender_password=email_config['sender_password']
            )
            
            success = sender.send_articles_email(
                articles=self.articles,
                recipient_email=email_config['recipient_email'],
                target_date=self.target_date
            )
            
            if success:
                print(f"\n✓ 총 {len(self.articles)}개 기사를 이메일로 전송했습니다.")
            else:
                print("\n✗ 이메일 전송에 실패했습니다.")
                
        except Exception as e:
            print(f"\n✗ 이메일 전송 중 오류: {e}")


async def main():
    # 오늘 날짜 기준으로 크롤링 (목록 페이지 사용)
    crawler = HanmiCrawler()  # target_date 생략 시 오늘 날짜
    await crawler.run(max_articles=10, use_list_page=True)  # 목록 페이지에서 수집
    
    # 메인 페이지에서 크롤링하려면:
    # await crawler.run(max_articles=10, use_list_page=False)
    
    # 특정 날짜로 크롤링하려면:
    # from datetime import date
    # crawler = HanmiCrawler(target_date=date(2026, 2, 1))
    # await crawler.run(max_articles=10)


if __name__ == "__main__":
    asyncio.run(main())
