# GitHub 趋势监控爬虫

这是一个面向 Python 学习的自动化小项目：每天抓取 GitHub Trending 热门项目，提取关键信息，保存为本地 JSON，并通过邮件发送一份日报。

## 功能列表

- 抓取 GitHub Trending 日榜全站项目
- 使用 `BeautifulSoup` 解析 HTML 结构
- 使用 `re` 清洗文本、数字字段
- 使用 `urllib.parse` 将相对链接规范化为绝对链接
- 将抓取结果保存为按日期命名的 JSON 快照
- 通过 SMTP 发送 HTML 邮件日报
- 支持 Windows 任务计划程序定时执行

## 目录结构

```text
.
├── config.example.env
├── main.py
├── README.md
├── requirements.txt
├── src/
│   └── trending_monitor/
│       ├── __init__.py
│       ├── config.py
│       ├── fetcher.py
│       ├── link_utils.py
│       ├── models.py
│       ├── notifier.py
│       ├── parser.py
│       └── storage.py
└── tests/
    ├── fixtures/
    └── ...
```

## 安装依赖

如果你使用 `uv`，推荐直接创建虚拟环境并安装依赖：

```powershell
uv venv
uv pip install -r requirements.txt
```

如果你使用传统 `pip`：

```powershell
python -m pip install -r requirements.txt
```

## 配置说明

1. 将 `config.example.env` 复制为 `.env`
2. 按实际邮箱信息填写 SMTP 配置
3. 确保邮箱已开启 SMTP，并生成授权码

示例：

```env
TRENDING_URL=https://github.com/trending
FETCH_TIMEOUT=15
TOP_N=20
DATA_DIR=data
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USERNAME=your_email@qq.com
SMTP_PASSWORD=your_authorization_code
FROM_EMAIL=your_email@qq.com
TO_EMAIL=receiver@example.com
SMTP_USE_TLS=false
```

如果你的邮箱使用：

- `465`：这是 SSL 模式，程序会自动走 `SMTP_SSL`
- `587`：这是 `STARTTLS` 模式，`SMTP_USE_TLS` 保持 `true`

## 本地运行

使用 `uv` 直接运行：

```powershell
uv run --with beautifulsoup4 --with python-dotenv python main.py
```

运行成功后会：

- 在 `data/` 目录生成 `trending_YYYY-MM-DD.json`
- 向目标邮箱发送一封“GitHub 今日热门项目日报”

## 运行测试

```powershell
uv run --with pytest --with beautifulsoup4 --with python-dotenv pytest -q
```

## Windows 任务计划程序设置

1. 打开“任务计划程序”
2. 选择“创建基本任务”
3. 名称填写：`GitHub 趋势监控`
4. 触发器选择“每天”，设定你希望发送邮件的时间
5. 操作选择“启动程序”
6. 程序或脚本填写 `uv`
7. 参数填写：

```text
run --with beautifulsoup4 --with python-dotenv python C:\Users\admin\Desktop\study\py\main.py
```

8. 起始于填写项目目录：

```text
C:\Users\admin\Desktop\study\py
```

## 常见问题

### 1. GitHub 页面结构变化导致解析失败

GitHub Trending 是网页抓取，不是官方稳定 API。如果页面结构变化，需要调整 `parser.py` 中的选择器。

### 2. 邮箱账号密码正确，但仍然发送失败

很多邮箱要求使用“SMTP 授权码”，而不是网页登录密码。请到邮箱后台开启 SMTP 服务并生成授权码。

另外也要确认端口和加密方式是否匹配：

- `465` 对应 SSL
- `587` 对应 STARTTLS

### 3. 网络超时或访问失败

请检查你的网络环境、代理设置，以及是否能正常访问 GitHub。

### 4. 为什么要保存本地 JSON

本地快照除了方便调试，还能为后续扩展“只提醒新上榜项目”提供数据基础。
