# 部署指南

PaperSeek Web UI 常见部署方式有两种：

- **Docker / Docker Compose**：推荐用于完整 Web UI、长时间搜索、流式日志、引用扩展和自托管场景。
- **Vercel**：适合快速演示和轻量使用。Vercel 可以运行 FastAPI Web UI，但它是 serverless function 运行时，长搜索可能触发函数时长限制。

如果只是试用 PaperSeek，可以直接访问在线体验版：

```text
https://www.paperseek.xyz/
```

在线体验版的两种模型模式、登录权限、ModelScope 额度和历史记录说明见 [在线体验版用户手册](online-demo.md)。

## Docker

Docker 是 PaperSeek 推荐的生产式部署方式。容器中使用 Uvicorn 运行 FastAPI 应用，默认监听 `7860`；下面的本地示例把它映射到宿主机 `8765`。

### 构建并运行

```bash
docker build -t paperseek .
docker run --rm -p 8765:7860 \
  -e LLM_PROVIDER=deepseek \
  -e LLM_API_TYPE=openai_chat \
  -e LLM_MODEL=deepseek-v4-flash \
  -e LLM_BASE_URL=https://api.deepseek.com \
  -e LLM_API_KEY=your-llm-api-key \
  paperseek
```

打开：

```text
http://127.0.0.1:8765/
```

### Docker Compose

复制示例环境文件：

```bash
cp .env.example .env
```

编辑 `.env`，填入模型服务商和数据源配置。然后运行：

```bash
docker compose up --build
```

打开：

```text
http://127.0.0.1:8765/
```

后台运行：

```bash
docker compose up -d --build
```

查看日志：

```bash
docker compose logs -f
```

停止服务：

```bash
docker compose down
```

### 环境变量

Docker 镜像接受与 CLI 和 Web UI 后端相同的环境变量：

| 变量 | 示例 |
| --- | --- |
| `PORT` | `7860` |
| `DATA_SOURCE` | `openalex` |
| `LLM_PROVIDER` | `deepseek` |
| `LLM_API_TYPE` | `openai_chat` |
| `LLM_MODEL` | `deepseek-v4-flash` |
| `LLM_BASE_URL` | `https://api.deepseek.com` |
| `LLM_API_KEY` | `your-llm-api-key` |
| `OPENALEX_API_KEY` | `your-openalex-key` |
| `CROSSREF_EMAIL` | `you@example.org` |
| `WOS_API_KEY` | `your-wos-key` |

如果你不想在服务器端配置密钥，用户也可以在 Web UI 中为当前浏览器会话填写 LLM Key 和数据源 Key。PaperSeek 不会保存这些本次会话密钥。

### 反向代理

如果通过 Nginx、Caddy、Traefik 或其他反向代理公开部署，把 HTTP 流量代理到：

```text
http://127.0.0.1:8765
```

公开访问时应使用 HTTPS。Web UI 表单允许用户输入 API Key，如果实例不是面向所有人开放，建议同时加访问控制。

## ModelScope API-Inference

PaperSeek 支持把 ModelScope API-Inference 作为 OpenAI Chat Completions 兼容模型服务商：

```bash
export LLM_PROVIDER=modelscope
export LLM_API_TYPE=openai_chat
export LLM_MODEL=Qwen/Qwen3-235B-A22B-Instruct-2507
export LLM_BASE_URL=https://api-inference.modelscope.cn/v1
export LLM_API_KEY=your-modelscope-token
```

默认 Base URL 和模型可以在 Web UI 中修改，也可以通过 CLI 参数覆盖。

## Vercel

Vercel 可以通过 Python runtime 部署 PaperSeek FastAPI 应用，适合演示、快速测试和轻量 Web UI 访问。

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FMingfengHong%2Fpaperseek)

### Vercel 上可用的功能

- PaperSeek Web UI。
- `/api/*` 下的 FastAPI 路由。
- FastAPI 应用托管的静态前端文件。
- Web UI 中按会话填写 API Key。
- 函数时长允许范围内的流式搜索日志。

### Vercel 限制

Vercel 使用 serverless function 模型。PaperSeek 搜索可能包含多次 LLM 调用、数据源请求和引用扩展。长时间或高负载搜索更适合 Docker 或 VPS。

常见限制包括：

- 搜索请求受函数最大执行时长限制。
- 冷启动会增加延迟。
- 很长的引用扩展可能超时。
- Serverless function 不适合持久后台任务。
- Vercel 部署日志和函数日志与 PaperSeek 页面中的 System Dashboard 是两套日志。

PaperSeek 通过根目录 `app.py` 让 Vercel 自动识别 FastAPI 应用。启用 Fluid Compute 时，Hobby 项目的默认和最大函数时长通常是 300 秒；实际限制取决于你的 Vercel 计划和项目设置。

### 从 GitHub 部署到 Vercel

1. 把仓库推送到 GitHub。
2. 点击上方 Deploy 按钮，或在 Vercel 中导入仓库。
3. 保持默认项目设置。
4. 如果希望服务器端提供默认配置，添加环境变量：
   - `LLM_PROVIDER`
   - `LLM_API_TYPE`
   - `LLM_MODEL`
   - `LLM_BASE_URL`
   - `LLM_API_KEY`
   - `OPENALEX_API_KEY`
   - `CROSSREF_EMAIL`
   - `WOS_API_KEY`
5. 点击部署。

如果不配置服务器端密钥，用户仍可以在 Web UI 中按会话填写 API Key。

### 使用 Vercel CLI

安装 Vercel CLI 后运行：

```bash
vercel
```

生产部署：

```bash
vercel --prod
```

本地 Vercel 开发：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
vercel dev
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
vercel dev
```

### Vercel 相关文件

PaperSeek 包含：

| 文件 | 用途 |
| --- | --- |
| `app.py` | Vercel FastAPI 自动识别入口，暴露 `paperseek.web_app.app` 为 `app`。 |
| `api/index.py` | 兼容 Python 入口，同样暴露 FastAPI `app`。 |
| `vercel.json` | 最小项目配置，故意不使用 `functions` pattern，避免 Vercel 函数匹配失败。 |
| `requirements.txt` | Vercel Python 依赖。 |

## Docker 还是 Vercel

| 场景 | 推荐方式 |
| --- | --- |
| 重复研究使用的完整 Web UI | Docker |
| 长时间搜索和引用扩展 | Docker |
| 私有实验室或服务器部署 | Docker + HTTPS 反向代理 |
| 快速演示链接 | Vercel |
| 用户只在浏览器会话中输入 Key | Docker 或 Vercel |
| 需要稳定长任务行为 | Docker |

## 健康检查

部署后测试：

```bash
curl http://127.0.0.1:8765/api/sources
```

Vercel 部署请替换域名：

```bash
curl https://your-project.vercel.app/api/sources
```

应返回包含 `openalex`、`crossref` 和 `wos` 的 JSON 数据源列表。

---

# Deployment Guide (English)

PaperSeek Web UI is commonly deployed in two ways:

- **Docker / Docker Compose**: recommended for the full Web UI experience, long searches, streaming logs, citation expansion, and self-hosted control.
- **Vercel**: convenient for demos and lightweight use. It can run the FastAPI Web UI, but long searches may hit serverless function duration limits.

## Docker

Build and run:

```bash
docker build -t paperseek .
docker run --rm -p 8765:7860 \
  -e LLM_PROVIDER=deepseek \
  -e LLM_API_TYPE=openai_chat \
  -e LLM_MODEL=deepseek-v4-flash \
  -e LLM_BASE_URL=https://api.deepseek.com \
  -e LLM_API_KEY=your-llm-api-key \
  paperseek
```

Open:

```text
http://127.0.0.1:8765/
```

Docker Compose:

```bash
cp .env.example .env
docker compose up --build
```

The Docker image accepts the same environment variables as the CLI and Web UI backend. If you do not want server-side secrets, users can enter LLM and data-source keys in the Web UI for the current browser session.

## Vercel

Vercel can deploy the FastAPI app through the Python runtime:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FMingfengHong%2Fpaperseek)

Useful files:

| File | Purpose |
| --- | --- |
| `app.py` | Root FastAPI entrypoint for Vercel auto-detection. |
| `api/index.py` | Compatibility Python entrypoint. |
| `vercel.json` | Minimal Vercel configuration without fragile `functions` patterns. |
| `requirements.txt` | Python dependencies for Vercel. |

Vercel is good for demos and lightweight use. For repeated research work, long searches, or citation expansion, use Docker or a VPS.

## Health check

```bash
curl http://127.0.0.1:8765/api/sources
```

For Vercel:

```bash
curl https://your-project.vercel.app/api/sources
```
