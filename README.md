# task-manager

タスク管理アプリ

**React + TypeScript + Python Lambda + API Gateway (HTTP API) + DynamoDB**

## 構成

```
backend/          Python Lambda (GET /hello)
frontend/         React + TypeScript (Vite) — Hello World 表示
template.yaml     SAM (HTTP API + S3 + CloudFront)
samconfig.toml    stack: task-manager
.cursor/mcp.json  AWS Serverless MCP (profile=deploy)
```

### 構成図

![AWS architecture](docs/images/hello-architecture.png)

1. ブラウザが CloudFront → S3 のフロントを取得する  
2. 画面に載った React（TypeScript）が表示される  
3. その画面が API Gateway の `/hello` を呼ぶ  
4. Lambda が JSON を返す  

## 前提

```powershell
aws sso login --profile deploy
aws sts get-caller-identity --profile deploy
```

Docker Desktop（`sam local` 用）:

```powershell
winget install -e --id Docker.DockerDesktop
```

## デプロイ

```powershell
sam build
sam deploy --profile deploy
```

`frontend/.env.production`:

```env
VITE_API_URL=http://127.0.0.1:3000
```

```powershell
cd frontend
npm ci
npm run build
aws s3 sync dist/ s3://<FrontendBucketName>/ --delete --profile deploy
aws cloudfront create-invalidation --distribution-id <CloudFrontDistributionId> --paths "/*" --profile deploy
```

## ローカル確認

```powershell
sam build
sam local start-api
```

API だけ:

```powershell
curl http://127.0.0.1:3000/hello
```

フロント:

```powershell
cd frontend
npm ci
# .env.local に VITE_API_URL=http://127.0.0.1:3000
npm run dev
```
