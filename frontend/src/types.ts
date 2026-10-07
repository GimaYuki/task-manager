export type TaskStatus = "todo" | "doing" | "done"

export type Task = {
  id: string
  title: string
  status: TaskStatus
}

export type TaskList = {
  tasks: Task[]
}

declare global {
  interface ImportMetaEnv {
    readonly VITE_API_URL?: string
  }
}
