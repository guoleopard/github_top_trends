import requests
from bs4 import BeautifulSoup
import re
from database import get_db_session
from models import GitHubTrend
from datetime import datetime

def get_github_trending(url='https://github.com/trending?since=weekly'):
    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    # 禁用不安全请求警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    try:
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        return response.text
    except requests.exceptions.SSLError as e:
        print(f"SSL证书验证失败: {e}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"网络连接失败，请检查网络连接或代理设置: {e}")
        return None
    except Exception as e:
        print(f"请求GitHub趋势页面失败: {e}")
        return None

def parse_trending_page(html_content):
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, 'lxml')
    repo_list = []
    
    # 找到所有仓库卡片
    repo_cards = soup.find_all('article', class_='Box-row')
    
    for card in repo_cards:
        try:
            repo_data = {}
            
            # 获取仓库所有者和名称
            repo_header = card.find('h2', class_='h3 lh-condensed')
            if repo_header:
                repo_link = repo_header.find('a')
                if repo_link:
                    repo_path = repo_link.get('href').strip('/')
                    repo_owner, repo_name = repo_path.split('/')
                    repo_data['repo_owner'] = repo_owner
                    repo_data['repo_name'] = repo_name
                    repo_data['repo_url'] = f'https://github.com{repo_link.get("href")}'
            
            # 获取仓库描述
            desc_elem = card.find('p', class_='col-9 color-fg-muted my-1 pr-4')
            if desc_elem:
                repo_data['repo_desc'] = desc_elem.get_text(strip=True)
            
            # 获取编程语言
            lang_elem = card.find('span', itemprop='programmingLanguage')
            if lang_elem:
                repo_data['language'] = lang_elem.get_text(strip=True)
            
            # 获取星标数、复刻数
            stars_elem = card.find('a', href=re.compile('/stargazers'))
            if stars_elem:
                stars_text = stars_elem.get_text(strip=True)
                repo_data['stars'] = convert_to_number(stars_text)
            
            forks_elem = card.find('a', href=re.compile('/forks'))
            if forks_elem:
                forks_text = forks_elem.get_text(strip=True)
                repo_data['forks'] = convert_to_number(forks_text)
            
            # 获取本周新增星标数
            stars_weekly_elem = card.find('span', class_='d-inline-block float-sm-right')
            if stars_weekly_elem:
                stars_weekly_text = stars_weekly_elem.get_text(strip=True)
                match = re.search(r'(\d+[\.,]?\d*)', stars_weekly_text)
                if match:
                    repo_data['stars_weekly'] = convert_to_number(match.group(1))
            
            repo_list.append(repo_data)
            
        except Exception as e:
            print(f"解析仓库卡片失败: {e}")
            continue
    
    return repo_list

def convert_to_number(num_str):
    """将带K/M的数字字符串转换为整数"""
    if not num_str:
        return 0
    
    num_str = num_str.replace(',', '')
    
    if num_str.endswith('K'):
        return int(float(num_str[:-1]) * 1000)
    elif num_str.endswith('M'):
        return int(float(num_str[:-1]) * 1000000)
    else:
        try:
            return int(num_str)
        except ValueError:
            return 0

def save_to_database(repo_list):
    if not repo_list:
        print("没有可保存的数据")
        return
    
    session = get_db_session()
    
    try:
        saved_count = 0
        updated_count = 0
        
        for repo in repo_list:
            # 检查是否已存在该仓库
            existing_repo = session.query(GitHubTrend).filter_by(repo_url=repo['repo_url']).first()
            
            if existing_repo:
                # 更新已有仓库信息
                existing_repo.stars = repo.get('stars', existing_repo.stars)
                existing_repo.forks = repo.get('forks', existing_repo.forks)
                existing_repo.stars_weekly = repo.get('stars_weekly', existing_repo.stars_weekly)
                existing_repo.created_at = datetime.now()
                updated_count += 1
            else:
                # 创建新仓库记录
                new_repo = GitHubTrend(
                    repo_owner=repo['repo_owner'],
                    repo_name=repo['repo_name'],
                    repo_desc=repo.get('repo_desc'),
                    repo_url=repo['repo_url'],
                    stars=repo.get('stars'),
                    forks=repo.get('forks'),
                    stars_weekly=repo.get('stars_weekly'),
                    language=repo.get('language')
                )
                session.add(new_repo)
                saved_count += 1
        
        session.commit()
        print(f"数据保存完成！新增 {saved_count} 条记录，更新 {updated_count} 条记录")
        
    except Exception as e:
        session.rollback()
        print(f"保存数据失败: {e}")
    finally:
        session.close()

def main():
    print("开始爬取GitHub每周热门趋势项目...")
    html_content = get_github_trending()
    repo_list = parse_trending_page(html_content)
    
    print(f"共解析到 {len(repo_list)} 个项目")
    
    if repo_list:
        save_to_database(repo_list)
    
    print("爬取任务完成！")

if __name__ == "__main__":
    main()