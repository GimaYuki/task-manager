import { useEffect, useState, type FormEvent } from "react"
import { createTask, deleteTask, listTasks, updateTaskStatus } from "./api.ts"
import type { Task, TaskStatus } from "./types.ts"

const statusLabel: Record<TaskStatus, string> = {
  todo: "未着手",
  doing: "着手中",
  done: "完了",
}

const statuses = Object.keys(statusLabel) as TaskStatus[]

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [title, setTitle] = useState("")
  const [loaded, setLoaded] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function refresh() {
    const data = await listTasks()
    setTasks(data.tasks)
  }

  useEffect(() => {
    refresh()
      .catch(() => setError("一覧の取得に失敗しました"))
      .finally(() => setLoaded(true))
  }, [])

  async function onAdd(event: FormEvent) {
    event.preventDefault()
    const next = title.trim()
    if (!next) return
    setError(null)
    try {
      await createTask(next)
      setTitle("")
      await refresh()
    } catch {
      setError("追加に失敗しました")
    }
  }

  async function onStatus(id: string, status: TaskStatus) {
    setError(null)
    try {
      await updateTaskStatus(id, status)
      await refresh()
    } catch {
      setError("状態の更新に失敗しました")
    }
  }

  async function onDelete(id: string) {
    setError(null)
    try {
      await deleteTask(id)
      await refresh()
    } catch {
      setError("削除に失敗しました")
    }
  }

  return (
    <>
      <style>{css}</style>
      <main>
        <h1>タスク管理</h1>
        <form onSubmit={onAdd}>
          <input
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="新しいタスク"
            aria-label="タスク名"
          />
          <button type="submit">追加</button>
        </form>
        {error ? <p role="alert">{error}</p> : null}
        {!loaded ? (
          <p>読み込み中</p>
        ) : tasks.length === 0 ? (
          <p>タスクはまだありません</p>
        ) : (
          <ul>
            {tasks.map((task) => (
              <li key={task.id}>
                <span>{task.title}</span>
                <select
                  aria-label={`${task.title}の状態`}
                  value={task.status}
                  onChange={(event) =>
                    onStatus(task.id, event.target.value as TaskStatus)
                  }
                >
                  {statuses.map((status) => (
                    <option key={status} value={status}>
                      {statusLabel[status]}
                    </option>
                  ))}
                </select>
                <button type="button" onClick={() => onDelete(task.id)}>
                  削除
                </button>
              </li>
            ))}
          </ul>
        )}
      </main>
    </>
  )
}

const css = `
#root {
  width: min(40rem, 100%);
  text-align: left;
  padding: 2rem 1.25rem;
}
h1 {
  font-size: 1.75rem;
  margin: 0 0 1rem;
}
form {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
input, select, button {
  font: inherit;
  padding: 0.4rem 0.6rem;
}
input {
  flex: 1;
}
ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0;
  border-top: 1px solid var(--border);
}
li span {
  flex: 1;
  color: var(--text-h);
}
[role="alert"] {
  color: #b42318;
}
`
