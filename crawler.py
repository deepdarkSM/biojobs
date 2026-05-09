import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def crawl_samsung_careers():
    url = "https://www.samsungcareers.com/hr/list.data"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.samsungcareers.com/hr/",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    params = {
        "currentPageNo": 1,
        "intNo": 0,
        "strVal": "",
        "strTxt": "",
        "strKey": "",
        "strCompany": "DA0,DB0",
        "strType": "",
        "strOrderBy": "",
        "strEntity": ""
    }
    
    jobs = []
    
    try:
        response = requests.post(url, headers=headers, data=params, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        items = soup.select('li')
        
        for item in items:
            title_el = item.select_one('.title')
            company_el = item.select_one('.company')
            period_el = item.select_one('.period')
            tags = [t.get_text(strip=True) for t in item.select('.flag.grey')]
            link_el = item.select_one('a[data-value]')
            
            if not title_el:
                continue
            
            job_no = ""
            if link_el:
                data_val = link_el.get('data-value', '')
                job_no = data_val.replace(',', '').replace(' ', '')
            
            jobs.append({
                "company": company_el.get_text(strip=True) if company_el else "삼성",
                "title": title_el.get_text(strip=True),
                "period": period_el.get_text(strip=True) if period_el else "",
                "tags": tags,
                "link": f"https://www.samsungcareers.com/hr/?no={job_no}" if job_no else "",
                "source": "삼성채용",
                "crawled_at": datetime.now().strftime("%Y-%m-%d")
            })
        
        print(f"삼성 채용: {len(jobs)}건 수집")
        
    except Exception as e:
        print(f"오류: {e}")
    
    return jobs


def save_jobs(jobs):
    with open('jobs.json', 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"총 {len(jobs)}건 저장 → jobs.json")


import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


def crawl_samsung_careers():
    url = "https://www.samsungcareers.com/hr/list.data"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.samsungcareers.com/hr/",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    params = {
        "currentPageNo": 1,
        "intNo": 0,
        "strVal": "",
        "strTxt": "",
        "strKey": "",
        "strCompany": "DA0,DB0",
        "strType": "",
        "strOrderBy": "",
        "strEntity": ""
    }
    
    jobs = []
    
    try:
        response = requests.post(url, headers=headers, data=params, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        items = soup.select('ul li')
        
        for item in items:
            title_el = item.select_one('.title')
            company_el = item.select_one('.company')
            period_el = item.select_one('.period')
            tags = [t.get_text(strip=True) for t in item.select('.flag.grey')]
            link_el = item.select_one('a[data-value]')
            
            if not title_el:
                continue
            
            job_no = ""
            if link_el:
                data_val = link_el.get('data-value', '')
                job_no = data_val.replace(',', '').replace(' ', '')
            
            jobs.append({
                "company": company_el.get_text(strip=True) if company_el else "삼성",
                "title": title_el.get_text(strip=True),
                "period": period_el.get_text(strip=True) if period_el else "",
                "tags": tags,
                "link": f"https://www.samsungcareers.com/hr/?no={job_no}" if job_no else "",
                "source": "삼성채용",
                "crawled_at": datetime.now().strftime("%Y-%m-%d")
            })
        
        print(f"삼성 채용: {len(jobs)}건 수집")
        
    except Exception as e:
        print(f"오류: {e}")
    
    return jobs


def crawl_bric():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }

    jobs = []
    offset = 0

    while True:
        url = f"https://www.ibric.org/bric/biojob/recruit.do?mode=list&&articleLimit=20&article.offset={offset}"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            rows = soup.select('.b-title-box')

            if not rows:
                break

            for row in rows:
                title_el = row.select_one('a.b-title')
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                href = title_el.get('href', '')
                link = "https://www.ibric.org/bric/biojob/recruit.do" + href if href else ""

                # b-box02 안에서 info 찾기
                parent_box = row.find_parent(class_='b-box02')
                info_items = []
                if parent_box:
                    info_box = parent_box.select_one('.b-info-box')
                    if info_box:
                        info_items = [li.get_text(strip=True) for li in info_box.select('li') if li.get_text(strip=True)]

                # 마감일
                period = ""
                date_box = row.find_parent().find_next_sibling(class_='b-date-box')
                if date_box:
                    period = date_box.get_text(strip=True)

                jobs.append({
                    "company": info_items[0] if info_items else "",
                    "title": title,
                    "period": period,
                    "tags": info_items[1:] if len(info_items) > 1 else [],
                    "link": link,
                    "source": "BRIC",
                    "crawled_at": datetime.now().strftime("%Y-%m-%d")
                })

            print(f"BRIC offset {offset}: {len(rows)}건 수집")
            offset += 20

        except Exception as e:
            print(f"BRIC 오류 (offset {offset}): {e}")
            break

    print(f"BRIC 총 {len(jobs)}건 수집")
    return jobs


def save_jobs(jobs):
    with open('jobs.json', 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"총 {len(jobs)}건 저장 → jobs.json")


if __name__ == "__main__":
    all_jobs = []
    all_jobs += crawl_samsung_careers()
    all_jobs += crawl_bric()
    save_jobs(all_jobs)

