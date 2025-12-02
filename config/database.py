import pymysql
from dotenv import load_dotenv
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", 3306))
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = os.getenv("DB_NAME", "github_trending")
    
    def get_connection(self):
        """获取数据库连接"""
        try:
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info("成功连接到数据库")
            return connection
        except pymysql.MySQLError as e:
            logger.error(f"连接数据库时出错: {str(e)}")
            return None


class DatabaseManager:
    """数据库管理器类"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self.connection = None
    
    def connect(self):
        """建立数据库连接"""
        self.connection = self.config.get_connection()
        return self.connection is not None
    
    def disconnect(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("数据库连接已关闭")
    
    def create_table(self):
        """创建GitHub趋势项目表"""
        if not self.connection:
            logger.error("未建立数据库连接")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # 创建表的SQL语句
            create_table_sql = """ 
                CREATE TABLE IF NOT EXISTS github_trending_projects ( 
                    id INT AUTO_INCREMENT PRIMARY KEY, 
                    rank INT NOT NULL, 
                    name VARCHAR(255) NOT NULL, 
                    owner VARCHAR(255) NOT NULL, 
                    url VARCHAR(500) NOT NULL, 
                    description TEXT, 
                    language VARCHAR(100), 
                    stars VARCHAR(50), 
                    forks VARCHAR(50), 
                    stars_today VARCHAR(50), 
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                    UNIQUE KEY unique_project (owner, name) 
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; 
            """
            
            cursor.execute(create_table_sql)
            self.connection.commit()
            
            logger.info("GitHub趋势项目表创建成功")
            return True
            
        except pymysql.MySQLError as e:
            logger.error(f"创建表时出错: {str(e)}")
            return False
        finally:
            cursor.close()


if __name__ == "__main__":
    # 测试数据库连接和表创建
    db_manager = DatabaseManager()
    
    if db_manager.connect():
        print("数据库连接成功")
        
        if db_manager.create_table():
            print("表创建成功")
        else:
            print("表创建失败")
        
        db_manager.disconnect()
    else:
        print("数据库连接失败")