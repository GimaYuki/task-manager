"""Task API for API Gateway HTTP API and DynamoDB."""

import base64
import json
import os
import time
from uuid import uuid4

import boto3

STATUSES = {"todo", "doing", "done"}
table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    route = event.get("routeKey", "")
    task_id = (event.get("pathParameters") or {}).get("id")

    if route == "GET /tasks":
        return _list_tasks()
    if route == "POST /tasks":
        return _create_task(event)
    if route == "PATCH /tasks/{id}" and task_id:
        return _update_task(task_id, event)
    if route == "DELETE /tasks/{id}" and task_id:
        return _delete_task(task_id)
    return _send(404, {"error": "not found"})


def _list_tasks():
    items = []
    response = table.scan()
    items.extend(response.get("Items", []))
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))
    items.sort(key=lambda item: item.get("created_at", 0))
    return _send(200, {"tasks": [_task_view(item) for item in items]})


def _create_task(event):
    try:
        body = _read_json(event)
    except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
        return _send(400, {"error": "invalid json"})
    title = body.get("title")
    if not isinstance(title, str) or not title.strip():
        return _send(400, {"error": "title is required"})
    task = {
        "id": str(uuid4()),
        "title": title.strip(),
        "status": "todo",
        "created_at": int(time.time() * 1000),
    }
    table.put_item(Item=task)
    return _send(201, _task_view(task))


def _update_task(task_id, event):
    try:
        body = _read_json(event)
    except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
        return _send(400, {"error": "invalid json"})
    status = body.get("status")
    if status not in STATUSES:
        return _send(400, {"error": "invalid status"})
    existing = table.get_item(Key={"id": task_id}).get("Item")
    if existing is None:
        return _send(404, {"error": "not found"})
    table.update_item(
        Key={"id": task_id},
        UpdateExpression="SET #status = :status",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={":status": status},
    )
    existing["status"] = status
    return _send(200, _task_view(existing))


def _delete_task(task_id):
    existing = table.get_item(Key={"id": task_id}).get("Item")
    if existing is None:
        return _send(404, {"error": "not found"})
    table.delete_item(Key={"id": task_id})
    return _send(204)


def _task_view(item):
    return {"id": item["id"], "title": item["title"], "status": item["status"]}


def _read_json(event):
    raw = event.get("body") or ""
    if event.get("isBase64Encoded"):
        raw = base64.b64decode(raw).decode()
    if raw == "":
        return {}
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("object required")
    return value


def _send(status, body=None):
    if body is None:
        return {"statusCode": status}
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json; charset=utf-8"},
        "body": json.dumps(body, ensure_ascii=False),
    }
