import type { Task, TaskList, TaskStatus } from "./types.ts"

const baseUrl = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:3000"

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, init)
  if (!response.ok) {
    throw new Error(`${response.status} ${path}`)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}

export function listTasks(): Promise<TaskList> {
  return request<TaskList>("/tasks")
}

export function createTask(title: string): Promise<Task> {
  return request<Task>("/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  })
}

export function updateTaskStatus(id: string, status: TaskStatus): Promise<Task> {
  return request<Task>(`/tasks/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  })
}

export function deleteTask(id: string): Promise<void> {
  return request<void>(`/tasks/${id}`, { method: "DELETE" })
}
