# GitHub 趋势项目爬虫

一个用于爬取 GitHub 趋势项目并将结果保存到 MySQL 数据库的 Python 爬虫项目。

## 项目结构

```
github_top_trends/
├─ src/
│  ├─ github_trending_spider.py  # GitHub 趋势项目爬虫
│  ├─ data_manager.py              # 数据管理器，负责将数据保存到数据库
│  └─ main.py                      # 主程序入口
├─ config/
│  └─ database.py                  # 数据库配置和管理
├─ tests/                           # 测试文件目录
├─ venv/                            # Python 虚拟环境
├─ .env                             # 环境变量文件，存储数据库敏感信息
└─ README.md                        # 项目说明文档
```

## 功能特性

1. **GitHub 趋势项目爬取**：支持按 daily、weekly、monthly 三个时间范围爬取 GitHub 趋势项目
2. **详细项目信息提取**：提取项目的排名、名称、所有者、URL、描述、编程语言、星数、分支数和今日新增星数等详细信息
3. **MySQL 数据库存储**：支持将爬取到的项目数据保存到 MySQL 数据库，实现数据的持久化存储
4. **数据更新机制**：对于已存在的项目，会更新其最新的信息，确保数据的时效性
5. **命令行参数支持**：支持通过命令行参数指定时间范围和是否保存到数据库

## 技术栈

- **Python 3.7+**：项目开发语言
- **Requests**：用于发送 HTTP 请求，获取 GitHub 网页内容
- **Beautiful Soup 4**：用于解析 HTML 网页内容，提取项目信息
- **PyMySQL**：用于连接和操作 MySQL 数据库
- **python-dotenv**：用于加载环境变量，管理数据库敏感信息

## 环境配置

### 1. 安装 Python

确保你的系统已经安装了 Python 3.7 或更高版本。你可以从 [Python 官方网站](https://www.python.org/) 下载并安装。

### 2. 创建虚拟环境

在项目根目录下，运行以下命令创建 Python 虚拟环境：

```bash
python -m venv venv
```

### 3. 激活虚拟环境

- **Windows 系统**：
  ```bash
  venv\Scripts\activate
  ```

- **Linux/macOS 系统**：
  ```bash
  source venv/bin/activate
  ```

### 4. 安装依赖包

在虚拟环境中，运行以下命令安装项目所需的所有依赖包：

```bash
pip install requests beautifulsoup4 pymysql python-dotenv
```

### 5. 配置 MySQL 数据库

1. **安装 MySQL**：确保你的系统已经安装了 MySQL 数据库。你可以从 [MySQL 官方网站](https://www.mysql.com/) 下载并安装。

2. **创建数据库**：打开 MySQL 命令行工具，运行以下命令创建一个名为 `github_trending` 的数据库：
   ```sql
   CREATE DATABASE IF NOT EXISTS github_trending DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **配置数据库连接**：编辑项目根目录下的 `.env` 文件，配置你的 MySQL 数据库连接信息：
   ```env
   # MySQL数据库配置
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password  # 替换为你的MySQL密码
   DB_NAME=github_trending
   
   # GitHub爬虫配置
   GITHUB_TRENDING_URL=https://github.com/trending
   SINCE=weekly
   USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
   ```

## 使用方法

### 运行爬虫

在项目根目录下，运行以下命令启动 GitHub 趋势项目爬虫：

```bash
python src/main.py
```

### 命令行参数

爬虫支持以下命令行参数：

- **--since**：指定爬取的时间范围，可选值为 `daily`、`weekly`、`monthly`，默认值为 `weekly`
- **--no-save**：指定不将数据保存到数据库，仅打印爬取结果

### 示例

1. **爬取 weekly 趋势项目并保存到数据库**（默认行为）：
   ```bash
   python src/main.py
   ```

2. **爬取 daily 趋势项目并保存到数据库**：
   ```bash
   python src/main.py --since daily
   ```

3. **爬取 monthly 趋势项目但不保存到数据库**：
   ```bash
   python src/main.py --since monthly --no-save
   ```

## 项目测试

在项目根目录下，运行以下命令测试项目的功能：

1. **测试爬虫功能**：
   ```bash
   python src/github_trending_spider.py
   ```

2. **测试数据库连接和表创建**：
   ```bash
   python config/database.py
   ```

3. **测试数据保存和获取功能**：
   ```bash
   python src/data_manager.py
   ```

## 注意事项

1. **GitHub API 限制**：由于该项目是基于网页抓取的方式获取 GitHub 趋势项目信息，而非使用 GitHub API，因此可能会受到 GitHub 的访问限制。建议不要过于频繁地运行爬虫，以免触发 GitHub 的反爬机制。

2. **数据库连接**：确保你的 MySQL 数据库服务已经启动，并且 `.env` 文件中的数据库连接信息是正确的。

3. **虚拟环境**：建议在虚拟环境中运行项目，以避免依赖包的版本冲突。

4. **环境变量**：不要将 `.env` 文件提交到版本控制系统中，以免泄露数据库的敏感信息。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。