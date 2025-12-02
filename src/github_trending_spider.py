import os
import sys

# 将项目根目录添加到Python路径中
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitHubTrendingSpider:
    """GitHub趋势项目爬虫"""
    
    def __init__(self):
        self.base_url = "https://github.com/trending"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def fetch_trending_projects(self, since: str = "weekly") -> List[Dict]:
        """
        获取GitHub趋势项目列表
        
        Args:
            since: 时间范围，可选值：daily, weekly, monthly
            
        Returns:
            趋势项目列表，每个项目包含以下字段：
            - rank: 排名
            - name: 项目名称
            - owner: 项目所有者
            - url: 项目URL
            - description: 项目描述
            - language: 主要编程语言
            - stars: 总星数
            - forks: 总分支数
            - stars_today: 今日新增星数
        """
        try:
            # 构建请求URL
            url = f"{self.base_url}?since={since}"
            
            # 发送HTTP请求（禁用SSL证书验证）
            response = requests.get(url, headers=self.headers, verify=False)
            response.raise_for_status()  # 如果请求失败，抛出HTTPError
            
            # 解析HTML内容
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 找到所有趋势项目的容器
            projects = soup.find_all("article", class_="Box-row")
            
            trending_projects = []
            
            for index, project in enumerate(projects, start=1):
                try:
                    # 提取项目所有者和名称
                    repo_info = project.find("h2").find("a")
                    repo_path = repo_info["href"].strip("/").split("/")
                    owner = repo_path[0]
                    name = repo_path[1]
                    
                    # 提取项目URL
                    url = f"https://github.com{repo_info['href']}"
                    
                    # 提取项目描述
                    description_elem = project.find("p", class_="col-9 color-fg-muted my-1 pr-4")
                    description = description_elem.text.strip() if description_elem else ""
                    
                    # 提取主要编程语言
                    language_elem = project.find("span", itemprop="programmingLanguage")
                    language = language_elem.text.strip() if language_elem else ""
                    
                    # 提取星数和分支数
                    stars_elem = project.find("a", href=f"/{owner}/{name}/stargazers")
                    forks_elem = project.find("a", href=f"/{owner}/{name}/network/members")
                    
                    stars = stars_elem.text.strip() if stars_elem else "0"
                    forks = forks_elem.text.strip() if forks_elem else "0"
                    
                    # 提取今日新增星数
                    stars_today_elem = project.find("span", class_="d-inline-block float-sm-right")
                    stars_today = stars_today_elem.text.strip().replace(" stars today", "") if stars_today_elem else "0"
                    
                    # 构建项目字典
                    project_dict = {
                        "rank": index,
                        "name": name,
                        "owner": owner,
                        "url": url,
                        "description": description,
                        "language": language,
                        "stars": stars,
                        "forks": forks,
                        "stars_today": stars_today
                    }
                    
                    trending_projects.append(project_dict)
                    
                except Exception as e:
                    logger.error(f"解析项目时出错 (索引: {index}): {str(e)}")
                    continue
            
            logger.info(f"成功获取到 {len(trending_projects)} 个趋势项目")
            return trending_projects
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求GitHub趋势页面时出错: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"处理GitHub趋势数据时出错: {str(e)}")
            return []


if __name__ == "__main__":
    # 测试爬虫功能
    spider = GitHubTrendingSpider()
    
    # 获取 weekly 趋势
    projects = spider.fetch_trending_projects(since="weekly")
    
    # 打印前5个项目
    if projects:
        print("GitHub 每周趋势项目 (前5个):")
        for project in projects[:5]:
            print(f"{project['rank']}. {project['owner']}/{project['name']}")
            print(f"   描述: {project['description']}")
            print(f"   语言: {project['language']}")
            print(f"   星数: {project['stars']} | 分支: {project['forks']} | 今日新增: {project['stars_today']}")
            print(f"   URL: {project['url']}")
            print()
    else:
        print("未能获取到趋势项目")