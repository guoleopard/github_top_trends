from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from models import Base

# 加载环境变量
load_dotenv()

def get_db_engine():
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_database = os.getenv('DB_DATABASE')
    
    # 创建数据库连接URL
    db_url = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}?charset=utf8mb4'
    
    try:
        engine = create_engine(db_url, echo=False)
        return engine
    except Exception as e:
        print(f"数据库连接失败: {e}")
        raise

def init_database():
    """初始化数据库，创建表"""
    engine = get_db_engine()
    Base.metadata.create_all(engine)
    print("数据库表创建成功！")

def get_db_session():
    """获取数据库会话"""
    engine = get_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()