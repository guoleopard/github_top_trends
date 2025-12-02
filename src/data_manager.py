import os
import sys

# 将项目根目录添加到Python路径中
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from config.database import DatabaseManager
import logging
from typing import List, Dict

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataManager:
    """数据管理器类，负责将爬取到的数据保存到数据库"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def save_projects(self, projects: List[Dict]) -> bool:
        """
        将GitHub趋势项目列表保存到数据库
        
        Args:
            projects: 要保存的项目列表
            
        Returns:
            保存成功返回True，否则返回False
        """
        if not projects:
            logger.warning("没有要保存的项目数据")
            return True
        
        # 建立数据库连接
        if not self.db_manager.connect():
            logger.error("无法建立数据库连接，保存失败")
            return False
        
        try:
            # 确保表存在
            if not self.db_manager.create_table():
                logger.error("无法创建表，保存失败")
                return False
            
            cursor = self.db_manager.connection.cursor()
            
            # 批量插入或更新项目数据
            inserted_count = 0
            updated_count = 0
            
            for project in projects:
                try:
                    # 检查项目是否已存在
                    check_sql = "SELECT id FROM github_trending_projects WHERE owner = %s AND name = %s"
                    cursor.execute(check_sql, (project['owner'], project['name']))
                    existing_project = cursor.fetchone()
                    
                    if existing_project:
                        # 项目已存在，更新数据
                        update_sql = """ 
                            UPDATE github_trending_projects 
                            SET rank = %s, url = %s, description = %s, language = %s, 
                                stars = %s, forks = %s, stars_today = %s, fetched_at = CURRENT_TIMESTAMP 
                            WHERE id = %s 
                        """
                        cursor.execute(update_sql, (
                            project['rank'],
                            project['url'],
                            project['description'],
                            project['language'],
                            project['stars'],
                            project['forks'],
                            project['stars_today'],
                            existing_project['id']
                        ))
                        updated_count += 1
                    else:
                        # 项目不存在，插入新数据
                        insert_sql = """ 
                            INSERT INTO github_trending_projects 
                            (rank, name, owner, url, description, language, stars, forks, stars_today) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
                        """
                        cursor.execute(insert_sql, (
                            project['rank'],
                            project['name'],
                            project['owner'],
                            project['url'],
                            project['description'],
                            project['language'],
                            project['stars'],
                            project['forks'],
                            project['stars_today']
                        ))
                        inserted_count += 1
                    
                except Exception as e:
                    logger.error(f"保存项目 {project['owner']}/{project['name']} 时出错: {str(e)}")
                    continue
            
            # 提交事务
            self.db_manager.connection.commit()
            
            logger.info(f"数据保存完成: 插入 {inserted_count} 个项目，更新 {updated_count} 个项目")
            return True
            
        except Exception as e:
            logger.error(f"批量保存项目时出错: {str(e)}")
            # 回滚事务
            self.db_manager.connection.rollback()
            return False
        finally:
            cursor.close()
            self.db_manager.disconnect()
    
    def get_projects(self, limit: int = 100) -> List[Dict]:
        """
        从数据库中获取GitHub趋势项目
        
        Args:
            limit: 要获取的项目数量限制，默认100
            
        Returns:
            项目列表
        """
        if not self.db_manager.connect():
            logger.error("无法建立数据库连接，获取数据失败")
            return []
        
        try:
            cursor = self.db_manager.connection.cursor()
            
            # 获取最新的项目数据
            select_sql = """ 
                SELECT id, rank, name, owner, url, description, language, stars, forks, stars_today, fetched_at 
                FROM github_trending_projects 
                ORDER BY fetched_at DESC, rank ASC 
                LIMIT %s 
            """
            cursor.execute(select_sql, (limit,))
            
            projects = cursor.fetchall()
            logger.info(f"成功从数据库中获取到 {len(projects)} 个项目")
            
            return projects
            
        except Exception as e:
            logger.error(f"从数据库中获取项目时出错: {str(e)}")
            return []
        finally:
            cursor.close()
            self.db_manager.disconnect()


if __name__ == "__main__":
    # 测试数据保存功能
    data_manager = DataManager()
    
    # 模拟爬取到的项目数据
    test_projects = [
        {
            "rank": 1,
            "name": "example1",
            "owner": "test_owner1",
            "url": "https://github.com/test_owner1/example1",
            "description": "这是一个示例项目1",
            "language": "Python",
            "stars": "1000",
            "forks": "200",
            "stars_today": "50"
        },
        {
            "rank": 2,
            "name": "example2",
            "owner": "test_owner2",
            "url": "https://github.com/test_owner2/example2",
            "description": "这是一个示例项目2",
            "language": "JavaScript",
            "stars": "2000",
            "forks": "300",
            "stars_today": "60"
        }
    ]
    
    print("测试数据保存功能...")
    if data_manager.save_projects(test_projects):
        print("数据保存成功")
        
        # 测试数据获取功能
        print("\n测试数据获取功能...")
        projects = data_manager.get_projects()
        if projects:
            print(f"成功获取到 {len(projects)} 个项目:")
            for project in projects:
                print(f"  {project['rank']}. {project['owner']}/{project['name']} ({project['language']})")
        else:
            print("数据获取失败")
    else:
        print("数据保存失败")