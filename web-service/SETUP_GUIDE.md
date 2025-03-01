# 科研学习助手配置指南

## 环境要求

### 基本环境
- Python 3.8+
- Node.js 16+
- MySQL 8.0+

### 数据库要求
- MySQL服务已启动
- 创建名为`ai`的数据库

## 安装步骤

### 1. 克隆项目
```bash
git clone <项目地址>
cd InternetDatabaseDevelopment-main
```

### 2. 后端配置（FastAPI）

1. 进入FastAPI后端目录：
```bash
cd backend_fastapi
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv venv

# Windows激活虚拟环境
venv\Scripts\activate

# macOS/Linux激活虚拟环境
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置数据库连接：
编辑 `database.py` 文件中的数据库连接信息：
```python
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://用户名:密码@localhost/ai"
```

5. 启动FastAPI服务：
```bash
python main.py
```
服务将在 http://localhost:8000 运行

### 3. 前端配置

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```
前端将在 http://localhost:5173 运行

## 数据库初始化

1. 导入数据库文件：
```bash
mysql -u 用户名 -p ai < data/MySQL/AI.sql
```

## 启动项目

### Windows用户（使用批处理脚本）

直接运行根目录下的启动脚本：
```bash
start.bat
```

### 手动启动

1. 启动FastAPI后端：
```bash
cd backend_fastapi
python main.py
```

2. 新开终端，启动前端：
```bash
cd frontend
npm run dev
```

## 访问项目

- 前端页面：http://localhost:5173
- API文档：http://localhost:8000/docs

## 常见问题

1. 数据库连接失败
- 检查MySQL服务是否启动
- 验证数据库用户名和密码是否正确
- 确认数据库`ai`是否创建

2. 依赖安装失败
- 确保使用了正确的Python版本
- 尝试使用国内镜像源：
  ```bash
  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```

3. 前端启动失败
- 确保Node.js版本符合要求
- 删除node_modules目录后重新安装依赖

## 注意事项

1. 项目已不再使用Yii2后端，所有后端服务都迁移到了FastAPI
2. 确保所有服务的端口（8000、5173）未被占用
3. 在生产环境部署时，建议配置反向代理和HTTPS