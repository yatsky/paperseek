# PaperSeek 在线体验版使用说明

PaperSeek 在线体验版用于快速试用完整 Web UI，不需要自己部署服务，也不需要准备 OpenAlex Key。页面支持 `EN` / `中文` 语言切换，选择会保存在当前浏览器。

在线体验：

```text
https://www.paperseek.xyz/
```

## 两种使用模式

在线体验版的配置区提供两种模型调用方式。

### Use ModelScope service

`Use ModelScope service` 使用 ModelScope API-Inference。这个模式需要点击右上角或配置区中的登录按钮，并使用 ModelScope 账号授权登录。登录后：

- PaperSeek 使用登录用户授权的 ModelScope API-Inference token 调用模型。
- 模型调用消耗登录用户自己的 ModelScope API-Inference 免费额度。
- PaperSeek 不会把 ModelScope API-Inference token 保存到数据库；token 只随当前登录会话用于发起模型请求。
- 数据源默认使用站点服务端 OpenAlex key 池，OpenAlex 引用扩展默认开启。
- `History` 页面会显示当前登录账号的云端历史记录。

ModelScope 模型路由默认是 `Automatic`。自动模式会在一组已测试的 API-Inference 模型之间尝试可用模型，不在前端展示具体轮询顺序。也可以选择 `Custom model` 并填写自定义 ModelScope model ID。

### Use your own API

`Use your own API` 适合已经有模型服务 API Key 的用户。这个模式不要求登录：

- 默认 provider 是 `OpenAI`。
- API Key、Base URL、模型和运行参数只用于当前浏览器会话。
- 如果 provider 选择 `Ollama`，API Key 可留空，用于本地兼容端点。
- ModelScope API-Inference 也可以作为自带 API 的 provider 使用，但不作为默认选项。
- PaperSeek 仍默认使用站点 OpenAlex key 池；只有在高级设置中填写自己的 OpenAlex Key 或其它数据源 Key 时才会覆盖。
- 未登录时不能使用托管服务的云端历史记录。

## 推荐流程

1. 进入 [paperseek.xyz](https://www.paperseek.xyz/)。
2. 如需中文界面，点击顶部状态条中的 `中文`。
3. 选择模型模式：
   - 想使用 ModelScope 免费 API-Inference 额度：选择 `Use ModelScope service` 并登录。
   - 想使用自己的模型服务：选择 `Use your own API`，填写 API Key。
4. 输入研究问题。
5. 保持默认 OpenAlex 数据源，或在配置区切换到 Crossref；自带 API 模式的高级设置中还可配置 Web of Science Starter。
6. 点击 `Check Config` 检查配置。失败时页面会弹出问题列表，并提示需要修复的字段。
7. 点击 `Run Search` 开始检索。
8. 在 `Results` 查看、筛选和勾选论文，并导出 CSV。
9. 在 `Citation Map` 查看 OpenAlex 引用扩展形成的引用关系图。
10. 登录用户可在 `History` 回看云端历史检索记录。

## 账号与权限

在线体验版不强制所有用户登录。登录与未登录的主要差异是：

| 功能 | 未登录 | 已登录 ModelScope |
| --- | --- | --- |
| 使用自己的模型 API | 支持 | 支持 |
| 使用站点 OpenAlex key 池 | 支持 | 支持 |
| 使用 ModelScope service | 不支持 | 支持，使用登录账号 API-Inference 额度 |
| 云端 History | 不支持 | 支持，按登录账号隔离 |

公共电脑或共享浏览器使用后请退出登录。历史记录按登录账号隔离，不按 IP 地址隔离。

## 使用前检查

使用 `Use ModelScope service` 前，请确认：

- ModelScope 账号已经绑定阿里云账号。
- 绑定的阿里云账号已完成实名认证。
- 如果使用 RAM 账号，需要按官方教程完成对应的绑定与授权。
- 授权登录 PaperSeek 时允许 `api-inference` 范围，否则无法代表当前用户调用模型。

如果登录成功但模型调用失败，请先检查 ModelScope 账号的阿里云绑定、实名认证和授权状态。完成绑定或授权后，建议退出 PaperSeek 并重新登录一次。

ModelScope API-Inference 的官方限制请以文档为准：

- [API-Inference 使用限制](https://modelscope.cn/docs/model-service/API-Inference/limits)
- [阿里云账号绑定与授权教程](https://modelscope.cn/docs/accounts/aliyun-binding-and-authorization)

## API-Inference 稳定性与额度

ModelScope API-Inference 不是商业 SLA 服务，而是面向开发者的免费体验能力。它可能受到用户总额度、单模型额度、动态并发限制和平台资源压力影响：

- 每位 ModelScope 注册用户当前每天有一个总调用额度，官方文档示例为所有模型合计每天 2000 次。
- 每个模型还有独立的单模型每日额度，额度会随资源和使用情况动态调整，最高不超过 200 次，也可能远低于 200 次。
- 如果某个模型返回空响应、`429` 或额度不足，在线版会尽量通过自动路由尝试其它可用模型；仍失败时可稍后重试，或改用 `Use your own API`。
- 平台会根据实时资源压力动态调整并发和速率限制，在线体验版更适合单人、低并发、轻量检索。
- 较早模型可能会逐步降低额度或下架，模型列表和可用额度以 ModelScope 实际页面和接口返回为准。

PaperSeek 会读取 ModelScope 响应头中的额度信息，并在日志里显示用户总额度和当前模型额度的剩余情况。ModelScope 文档列出的相关响应头包括：

| 响应头 | 含义 |
| --- | --- |
| `modelscope-ratelimit-requests-limit` | 用户当天总额度 |
| `modelscope-ratelimit-requests-remaining` | 用户当天剩余额度 |
| `modelscope-ratelimit-model-requests-limit` | 当前模型当天额度 |
| `modelscope-ratelimit-model-requests-remaining` | 当前模型当天剩余额度 |

## 历史记录

在线体验版会保存已登录账号的检索历史，包括：

- 检索问题和运行配置。
- 工作流日志。
- 数据源返回的候选论文。
- 最终排序结果。

历史记录按登录账号隔离。不同浏览器、不同设备或不同网络环境中，只要登录的是同一个账号，就能看到同一账号的历史记录；不同账号之间不会共享历史记录。未登录用户可以运行检索，但不能使用云端历史记录。

## 与开源自托管版的区别

| 项目 | 在线体验版 | 开源自托管版 |
| --- | --- | --- |
| 登录 | 使用自己的 API 时不需要登录；ModelScope service 和 History 需要登录 | 默认不需要登录 |
| 模型调用 | 可使用登录用户的 ModelScope API-Inference 额度，或填写自己的模型 API | 使用你自己配置的 LLM API Key |
| OpenAlex Key | 默认使用站点服务端 key 池，可在高级设置中覆盖 | 可匿名访问或自己配置 key |
| 历史记录 | 登录后保存到托管服务数据库 | 默认保存到本地 SQLite |
| 适用场景 | 快速体验、轻量检索、临时试用 | 私有部署、长期使用、可控配置 |

## 隐私提示

不要在研究问题中输入不应上传到第三方模型服务的敏感内容。在线体验版会把检索问题、候选论文元数据和排序提示发送给所选模型服务，以完成检索式生成和结果排序。

如果需要长期使用、私有部署、稳定额度或完全控制 API Key 与数据存储，请使用开源自托管版本，并配置自己的模型服务和数据源。

## English

The hosted PaperSeek demo lets you try the full Web UI without deploying your own server or preparing an OpenAlex key. The UI can switch between `EN` and `中文`, and the choice is saved in the current browser.

URL:

```text
https://www.paperseek.xyz/
```

The hosted configuration panel has two model modes:

- `Use ModelScope service`: requires ModelScope sign-in. Model calls use the signed-in user's API-Inference quota, OpenAlex uses the hosted site key pool by default, and hosted history is available for the signed-in account. Model routing defaults to `Automatic`, which tries a tested pool of API-Inference models; advanced users can provide a custom ModelScope model ID.
- `Use your own API`: does not require sign-in. The default provider is OpenAI, and API key, base URL, model, and run settings are used only for the current browser session. The site OpenAlex key pool is still used unless you override source credentials in Advanced settings.

Signing in only affects the ModelScope service mode and hosted history. Users who provide their own model API key can run searches without signing in, but they will not have hosted history.

Before using API-Inference, make sure the ModelScope account is linked to an Alibaba Cloud account, has completed real-name verification, and has granted the `api-inference` OAuth scope. For RAM accounts, follow the official binding and authorization guide.

Official ModelScope references:

- [API Inference usage limits](https://modelscope.cn/docs/model-service/API-Inference/limits)
- [Alibaba Cloud account binding and authorization](https://modelscope.cn/docs/accounts/aliyun-binding-and-authorization)

ModelScope API-Inference is a free developer-oriented service rather than a production SLA service. It is subject to a daily per-user quota, separate per-model quotas, transient empty responses, and dynamic rate limits. If automatic routing cannot complete a request, retry later or use your own model API.

PaperSeek reads ModelScope quota headers when available and shows remaining user/model quota in the run log. History is isolated by the authenticated account, not by IP address. Sign out after using PaperSeek on a shared computer. For private deployment, long-term use, or full control over API keys and storage, use the open-source self-hosted version instead.
