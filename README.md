# task-manager

タスク管理アプリ

**React + TypeScript（Vite） + Python（Lambda）**

## 構成

```
template.yaml     SAM（Lambda、API Gateway HTTP API、DynamoDB、S3、CloudFront）
backend/app.py    Lambda ハンドラ（/tasks）
frontend/         React + TypeScript（Vite）— タスクの追加・状態変更・削除
scripts/          画面のビルドと S3 への配置
```

1. API Gateway が `/tasks` を Lambda に渡す
2. 画面のファイルは S3 にあり、CloudFront が HTTPS で配る
3. 画面が一覧を出し、追加・状態変更・削除を送る
4. データは DynamoDB に残る。Lambda の再実行後も消えない

## 前提

Python 3、Node.js（`npm` が使えること）、AWS CLI、SAM CLI、デプロイできる AWS 認証情報。

## デプロイ

```powershell
sam build
sam deploy --guided
```

初回の `--guided` でスタック名、リージョン、変更の確認を聞かれる。CloudFront の作成に十数分かかることがある。出力の `ApiUrl` と `FrontendUrl` を控える。

`sam deploy` を実行する IAM には、Lambda、API Gateway、DynamoDB、CloudFormation、IAM に加え、S3 バケットとバケットポリシー、CloudFront のディストリビューションとオリジンアクセスコントロールを作る権限が要る。

## フロント

### ローカル

別のターミナルで起動し、表示された URL を開く。既定は `http://127.0.0.1:5173`。

```powershell
cd frontend
npm ci
npm run dev
```

`frontend/.env.local` に、出力の API URL を書く。末尾に `/` は付けない。

```env
VITE_API_URL=https://xxxx.execute-api.ap-northeast-1.amazonaws.com
```

未設定時の接続先は `http://127.0.0.1:3000` なので、デプロイした API を使うときはこのファイルが必要。

### 本番

画面は非公開の S3 に置き、CloudFront（`FrontendUrl`）から HTTPS で配信する。API は API Gateway のまま。配置する IAM には、そのバケットへの `s3:ListBucket`、`s3:GetObject`、`s3:PutObject`、`s3:DeleteObject` と、`cloudfront:CreateInvalidation` が要る。AWS CLI の既定リージョンを、スタックを作ったリージョンに合わせる。

```powershell
.\scripts\deploy-frontend.ps1 -StackName スタック名
```

スクリプトはスタック出力から `ApiUrl` を読んで本番ビルドし、`FrontendBucketName` へ `dist/` を同期し、`FrontendDistributionId` を無効化する。終わったら `FrontendUrl` を開く。

## 確認

`ApiUrl` に対して一覧を取る。`{"tasks":[]}` が返る。

```powershell
curl.exe https://xxxx.execute-api.ap-northeast-1.amazonaws.com/tasks
```

本番では `FrontendUrl` を開き、タスクを追加し、状態を変え、削除する。再読込しても、削除していないタスクは残る。
