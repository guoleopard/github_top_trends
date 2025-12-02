# GitHub Trending Crawler

一个用于爬取GitHub Trending页面（周榜）并将项目信息保存到MySQL数据库的Python爬虫项目。

## 功能特性

- 自动爬取GitHub Trending周榜项目列表
- 提取项目名称、作者、描述、编程语言、Star数、Fork数、周增长Star数等信息
- 将数据保存到MySQL数据库，支持重复数据自动更新
- 使用虚拟环境管理依赖
- 配置文件与代码分离

## 技术栈

- Python 3.7+
- Requests: 发送HTTP请求
- BeautifulSoup4: HTML解析
- PyMySQL: MySQL数据库连接
- python-dotenv: 环境变量管理

## 项目结构

```
.
├── github_trending_crawler.py  # 主爬虫脚本
├── requirements.txt            # Python依赖列表
├── .env.example               # 环境变量配置模板
├── .env                       # 环境变量配置文件（需自行创建）
├── init_database.sql          # 数据库初始化SQL脚本
├── venv_activate.bat          # Windows虚拟环境激活脚本
└── README.md                  # 项目说明文档
```

## 安装与使用

### 1. 克隆或下载项目

### 2. 创建虚拟环境（Windows）

```bash
# 使用提供的批处理脚本创建并激活虚拟环境
venv_activate.bat

# 或者手动创建
python -m venv venv
venv\Scripts\activate.bat
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置数据库

#### 方法一：使用SQL脚本初始化

```bash
# 登录MySQL后执行SQL脚本
mysql -u root -p < init_database.sql
```

#### 方法二：手动创建

1. 创建数据库：
```sql
CREATE DATABASE github_trending CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 使用提供的`init_database.sql`脚本创建表结构

### 5. 配置环境变量

复制`.env.example`文件为`.env`并修改配置：

```bash
copy .env.example .env
```

编辑`.env`文件：

```env
# MySQL数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=github_trending
DB_USER=root
DB_PASSWORD=your_mysql_password

# 爬虫配置
GITHUB_URL=https://github.com/trending?since=weekly
REQUEST_TIMEOUT=10
```

### 6. 运行爬虫

```bash
python github_trending_crawler.py
```

## 数据库表结构

### repositories表

| 字段名         | 类型         | 说明                     |
|---------------|--------------|--------------------------|
| id            | INT          | 主键，自增               |
| repo_name     | VARCHAR(255) | 项目名称                 |
| author        | VARCHAR(255) | 作者/组织名称            |
| description   | TEXT         | 项目描述                 |
| language      | VARCHAR(100) | 主要编程语言             |
| stars         | INT          | 总Star数                 |
| forks         | INT          | Fork数                   |
| stars_weekly  | INT          | 本周增长的Star数         |
| html_url      | VARCHAR(500) | 项目GitHub地址（唯一）   |
| created_at    | TIMESTAMP    | 记录创建时间             |
| updated_at    | TIMESTAMP    | 记录最后更新时间         |

### 索引

- `unique_repo` (author, repo_name): 防止重复项目
- `idx_language`: 按语言查询优化
- `idx_stars`: 按Star数排序优化
- `idx_stars_weekly`: 按周Star增长排序优化
- `idx_created_at`: 按创建时间排序优化

## 使用示例

### 查询周榜Top 10项目

```sql
SELECT author, repo_name, description, language, stars, stars_weekly
FROM repositories
ORDER BY stars_weekly DESC
LIMIT 10;
```

### 按编程语言统计

```sql
SELECT language, COUNT(*) as repo_count, AVG(stars) as avg_stars
FROM repositories
WHERE language IS NOT NULL
GROUP BY language
ORDER BY repo_count DESC
LIMIT 10;
```

## 注意事项

1. **MySQL版本要求**: 建议使用MySQL 5.7+或MariaDB 10.2+
2. **依赖Python版本**: Python 3.7及以上
3. **网络代理**: 如果无法访问GitHub，请检查网络设置或配置代理
4. **Rate Limiting**: 请合理控制爬取频率，避免被GitHub限制访问
5. **数据更新**: 脚本使用`ON DUPLICATE KEY UPDATE`，重复运行会自动更新已有数据

## 常见问题

### Q: 运行时出现数据库连接错误

A: 检查以下几点：
- MySQL服务是否已启动
- `.env`文件中的数据库配置是否正确
- 数据库用户是否有足够的权限
- 防火墙是否允许连接

### Q: 爬取到的项目数量为0

A: 可能的原因：
- GitHub页面结构发生变化（需要更新CSS选择器）
- 网络连接问题
- IP被GitHub临时限制

### Q: 出现编码错误

A: 确保数据库和表使用`utf8mb4`字符集

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。
