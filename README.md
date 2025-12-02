# GitHub Trending 爬虫项目

一个用于爬取GitHub每周热门趋势项目并保存到MySQL数据库的Python爬虫项目。

## 功能特性

1.  自动爬取GitHub每周热门趋势项目
2.  解析项目的所有者、名称、描述、星标数、复刻数、本周新增星标、编程语言等信息
3.  将数据存储到MySQL数据库中
4.  支持已存在项目的更新
5.  使用虚拟环境进行项目隔离

## 环境要求

- Python 3.8+
- MySQL 5.7+

## 安装与使用

### 1. 创建并激活虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

1.  创建MySQL数据库
```sql
CREATE DATABASE github_trends CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2.  修改 `.env` 文件中的数据库连接信息
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_actual_password
DB_DATABASE=github_trends
```

### 4. 初始化数据库表

```bash
python -c "from database import init_database; init_database()"
```

### 5. 运行爬虫

```bash
python crawler.py
```

## 项目结构

```
├── .env                    # 环境配置文件
├── requirements.txt        # 项目依赖
├── models.py              # 数据库模型
├── database.py            # 数据库连接与初始化
├── crawler.py             # 主爬虫程序
└── README.md              # 项目说明文档
```

## 数据库表结构

### github_trends 表

| 字段名        | 类型         | 描述           |
|--------------|--------------|----------------|
| id           | INT          | 主键，自增     |
| repo_owner   | VARCHAR(100) | 仓库所有者     |
| repo_name    | VARCHAR(100) | 仓库名称       |
| repo_desc    | TEXT         | 仓库描述       |
| repo_url     | VARCHAR(255) | 仓库URL（唯一）|
| stars        | INT          | 星标数量       |
| forks        | INT          | 复刻数量       |
| stars_weekly | INT          | 本周新增星标数 |
| language     | VARCHAR(50)  | 主要编程语言   |
| created_at   | DATETIME     | 爬取时间       |

## 注意事项

1.  请确保您的MySQL服务已正常启动
2.  请合理设置爬取频率，避免给GitHub服务器造成过大压力
3.  如果遇到请求失败，可以适当调整 `crawler.py` 中的请求头或增加重试机制
4.  虚拟环境激活后，终端提示符会出现 `(venv)` 前缀表示已激活

## 退出虚拟环境

```bash
deactivate
```