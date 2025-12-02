import os
import sys

# 将项目根目录添加到Python路径中
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from github_trending_spider import GitHubTrendingSpider
from data_manager import DataManager
import logging
import argparse

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main(since: str = "weekly", save_to_db: bool = True):
    """
    主程序入口，用于运行GitHub趋势爬虫并保存数据到数据库
    
    Args:
        since: 时间范围，可选值：daily, weekly, monthly
        save_to_db: 是否将数据保存到数据库，默认True
    """
    logger.info("开始运行GitHub趋势爬虫")
    
    try:
        # 1. 初始化爬虫
        spider = GitHubTrendingSpider()
        
        # 2. 爬取GitHub趋势项目
        logger.info(f"正在爬取GitHub {since} 趋势项目...")
        projects = spider.fetch_trending_projects(since=since)
        
        if not projects:
            logger.warning("未能获取到任何趋势项目")
            return
        
        logger.info(f"成功爬取到 {len(projects)} 个趋势项目")
        
        # 3. 保存数据到数据库
        if save_to_db:
            logger.info("正在将数据保存到数据库...")
            data_manager = DataManager()
            
            if data_manager.save_projects(projects):
                logger.info("数据保存到数据库成功")
            else:
                logger.error("数据保存到数据库失败")
        else:
            logger.info("跳过数据保存到数据库步骤")
        
        # 4. 打印爬取结果摘要
        print("\n" + "="*80)
        print(f"GitHub {since.title()} 趋势项目摘要")
        print("="*80)
        print(f"共获取到 {len(projects)} 个趋势项目")
        print()
        
        # 打印前10个项目
        print("前10个趋势项目:")
        for i, project in enumerate(projects[:10], start=1):
            print(f"{i}. {project['owner']}/{project['name']}")
            print(f"   描述: {project['description']}")
            print(f"   语言: {project['language']}")
            print(f"   星数: {project['stars']} | 分支: {project['forks']} | 今日新增: {project['stars_today']}")
            print(f"   URL: {project['url']}")
            if i < 10:
                print()
        
        print("\n" + "="*80)
        logger.info("GitHub趋势爬虫运行完成")
        
    except KeyboardInterrupt:
        logger.info("用户中断了爬虫运行")
    except Exception as e:
        logger.error(f"爬虫运行过程中发生错误: {str(e)}")


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="GitHub趋势项目爬虫")
    parser.add_argument("--since", type=str, choices=["daily", "weekly", "monthly"], 
                        default="weekly", help="时间范围 (default: weekly)")
    parser.add_argument("--no-save", action="store_true", help="不将数据保存到数据库")
    
    args = parser.parse_args()
    
    # 运行主程序
    main(since=args.since, save_to_db=not args.no_save)