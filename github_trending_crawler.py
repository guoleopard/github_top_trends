import os
import sys
import time
import requests
from bs4 import BeautifulSoup
import pymysql
from dotenv import load_dotenv
from typing import List, Dict

class GitHubTrendingCrawler:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Database configuration
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = int(os.getenv('DB_PORT', 3306))
        self.db_name = os.getenv('DB_NAME', 'github_trending')
        self.db_user = os.getenv('DB_USER', 'root')
        self.db_password = os.getenv('DB_PASSWORD', '')
        
        # Crawler configuration
        self.github_url = os.getenv('GITHUB_URL', 'https://github.com/trending?since=weekly')
        self.timeout = int(os.getenv('REQUEST_TIMEOUT', 10))
        self.verify_ssl = os.getenv('VERIFY_SSL', 'True').lower() == 'true'
        
        # Headers to mimic a browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        self.conn = None
        self.cursor = None
        
    def connect_db(self):
        """Connect to MySQL database"""
        try:
            self.conn = pymysql.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name,
                charset='utf8mb4'
            )
            self.cursor = self.conn.cursor()
            print("Connected to MySQL database successfully")
        except pymysql.Error as e:
            print(f"Error connecting to MySQL: {e}")
            sys.exit(1)
            
    def create_table(self):
        """Create repositories table if it doesn't exist"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS repositories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            repo_name VARCHAR(255) NOT NULL,
            author VARCHAR(255) NOT NULL,
            description TEXT,
            language VARCHAR(100),
            stars INT DEFAULT 0,
            forks INT DEFAULT 0,
            stars_weekly INT DEFAULT 0,
            html_url VARCHAR(500) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_repo (author, repo_name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        
        try:
            self.cursor.execute(create_table_sql)
            self.conn.commit()
            print("Table 'repositories' is ready")
        except pymysql.Error as e:
            print(f"Error creating table: {e}")
            self.conn.rollback()
            
    def fetch_trending_repos(self) -> List[Dict]:
        """Fetch trending repositories from GitHub"""
        repositories = []
        
        try:
            response = requests.get(self.github_url, headers=self.headers, timeout=self.timeout, verify=self.verify_ssl)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            repo_cards = soup.find_all('article', class_='Box-row')
            
            for card in repo_cards:
                repo = self.parse_repo_card(card)
                if repo:
                    repositories.append(repo)
            
            print(f"Successfully fetched {len(repositories)} trending repositories")
            return repositories
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching GitHub trending page: {e}")
            sys.exit(1)
            
    def parse_repo_card(self, card) -> Dict:
        """Parse repository information from HTML card"""
        try:
            # Repo name and author
            title_element = card.find('h2', class_='h3 lh-condensed')
            if not title_element:
                return None
                
            title_link = title_element.find('a')
            repo_full_name = title_link.text.strip()
            author, repo_name = repo_full_name.split('/')
            html_url = f"https://github.com{title_link['href']}"
            
            # Description
            description_element = card.find('p', class_='col-9 color-fg-muted my-1 pr-4')
            description = description_element.text.strip() if description_element else None
            
            # Language
            language_element = card.find('span', itemprop='programmingLanguage')
            language = language_element.text.strip() if language_element else None
            
            # Stars and forks
            stars = 0
            forks = 0
            stars_weekly = 0
            
            # Get all stat numbers
            stat_elements = card.find_all('a', class_='Link--muted d-inline-block mr-3')
            for stat in stat_elements:
                if 'stars' in stat['href']:
                    stars_text = stat.text.strip().replace(',', '')
                    if stars_text.isdigit():
                        stars = int(stars_text)
                elif 'forks' in stat['href']:
                    forks_text = stat.text.strip().replace(',', '')
                    if forks_text.isdigit():
                        forks = int(forks_text)
            
            # Weekly stars
            weekly_stars_element = card.find('span', class_='d-inline-block float-sm-right')
            if weekly_stars_element:
                weekly_stars_text = weekly_stars_element.text.strip()
                # Extract number from text like "12,345 stars this week"
                import re
                match = re.search(r'(\d[\d,]*)', weekly_stars_text)
                if match:
                    stars_weekly = int(match.group(1).replace(',', ''))
            
            return {
                'repo_name': repo_name.strip(),
                'author': author.strip(),
                'description': description,
                'language': language,
                'stars': stars,
                'forks': forks,
                'stars_weekly': stars_weekly,
                'html_url': html_url
            }
            
        except Exception as e:
            print(f"Error parsing repository card: {e}")
            return None
            
    def save_repositories(self, repositories: List[Dict]):
        """Save repositories to MySQL database"""
        if not repositories:
            print("No repositories to save")
            return
            
        insert_sql = """
        INSERT INTO repositories 
        (repo_name, author, description, language, stars, forks, stars_weekly, html_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            description = VALUES(description),
            language = VALUES(language),
            stars = VALUES(stars),
            forks = VALUES(forks),
            stars_weekly = VALUES(stars_weekly),
            updated_at = CURRENT_TIMESTAMP
        """
        
        try:
            count = 0
            for repo in repositories:
                values = (
                    repo['repo_name'],
                    repo['author'],
                    repo['description'],
                    repo['language'],
                    repo['stars'],
                    repo['forks'],
                    repo['stars_weekly'],
                    repo['html_url']
                )
                
                self.cursor.execute(insert_sql, values)
                count += 1
            
            self.conn.commit()
            print(f"Successfully saved/updated {count} repositories to database")
            
        except pymysql.Error as e:
            print(f"Error saving repositories: {e}")
            self.conn.rollback()
            
    def close_db(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed")
        
    def run(self):
        """Main crawler execution flow"""
        print("Starting GitHub Trending Crawler...")
        
        # Connect to database
        self.connect_db()
        
        # Create table if not exists
        self.create_table()
        
        # Fetch trending repositories
        repositories = self.fetch_trending_repos()
        
        # Save to database
        self.save_repositories(repositories)
        
        # Close database connection
        self.close_db()
        
        print("Crawling completed successfully!")

if __name__ == "__main__":
    crawler = GitHubTrendingCrawler()
    crawler.run()