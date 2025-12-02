from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class GitHubTrend(Base):
    __tablename__ = 'github_trends'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    repo_owner = Column(String(100), nullable=False, comment='仓库所有者')
    repo_name = Column(String(100), nullable=False, comment='仓库名称')
    repo_desc = Column(Text, comment='仓库描述')
    repo_url = Column(String(255), nullable=False, unique=True, comment='仓库URL')
    stars = Column(Integer, comment='星标数量')
    forks = Column(Integer, comment='复刻数量')
    stars_weekly = Column(Integer, comment='本周新增星标数')
    language = Column(String(50), comment='主要编程语言')
    created_at = Column(DateTime, default=datetime.now, comment='爬取时间')
    
    def __repr__(self):
        return f"<GitHubTrend {self.repo_owner}/{self.repo_name}>"