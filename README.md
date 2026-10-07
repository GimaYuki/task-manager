# task-manager

タスク管理アプリ

**React + TypeScript（Vite） + Python（ローカル API）**

## 構成

```
backend/app.py    インメモリ API（127.0.0.1:3000、/tasks）
frontend/         React + TypeScript（Vite）— タスクの追加・状態変更・削除
```

1. `python backend/app.py` が `/tasks` を受け付ける
2. 画面が一覧を出し、追加・状態変更・削除を送る
3. データはプロセスのメモリだけ。停止すると消える

## 前提

Python 3 と Node.js（`npm` が使えること）。

## ローカル確認

先に API を起動し、このターミナルは開いたままにする。

```powershell
python backend/app.py
```

別のターミナルで確認する。`{"tasks":[]}` が返る。

```powershell
curl.exe http://127.0.0.1:3000/tasks
```

そのターミナルでフロントを起動し、表示された URL を開く。既定は `http://127.0.0.1:5173`。

```powershell
cd frontend
npm ci
npm run dev
```

API の URL を変えるときだけ、`frontend/.env.local` に書く。未設定時は `http://127.0.0.1:3000`。

```env
VITE_API_URL=http://127.0.0.1:3000
```

