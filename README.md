# Introduction
This agent can be used to run commands in a host server and upload/fetch file in this server. 

# Agent API Example

##  Post File
```bash
curl -L '127.0.0.1:5000/api/v1/file' \
-H 'Content-Type: application/x-www-form-urlencoded' \
-F 'target_path="/tmp/aaa.yaml"' \
-F 'file=@"/Users/chuanhaoq/a.yaml"'
```
response:
```json
{
    "message": "Upload file successfully"
}
```

## Get File

```bash
curl -L '127.0.0.1:5000/api/v1/file?file_path=%2Ftmp%2Faaa.yaml' \
-H 'Content-Type: application/x-www-form-urlencoded'
```

response:
```json
<file content>
```

## Post Command Request Task

```bash
curl -L '127.0.0.1:5000/api/v1/tasks' \
-H 'Content-Type: application/json' \
-d '{
    "command": "date; sleep 5; date",
    "timeout_seconds": 6
}'
```

response:
```json
{
    "task_id": 1,
    "command": "date; sleep 5; date",
    "timeout_seconds": 6,
    "retry_count": 0,
    "extra": "",
    "key": "",
    "callback_url": "",
    "status": "doing",
    "return_code": 0,
    "error_msg": "",
    "start_time": "0001-01-01T00:00:00Z",
    "end_time": "0001-01-01T00:00:00Z",
    "duration": 0,
    "log_redis_key": "",
    "log_redis_url": "",
    "thread_name": "",
    "stdout": ""
}
```

## List Tasks

```bash
curl -L '127.0.0.1:5000/api/v1/tasks'
```

response:
```json
{
    "1": {
        "task_id": 1,
        "command": "date; sleep 5; date",
        "timeout_seconds": 6,
        "retry_count": 0,
        "extra": "",
        "key": "",
        "callback_url": "",
        "status": "done",
        "return_code": 0,
        "error_msg": "",
        "start_time": "2023-11-13T11:06:50.863401+08:00",
        "end_time": "2023-11-13T11:06:55.971313+08:00",
        "duration": 5,
        "log_redis_key": "",
        "log_redis_url": "",
        "thread_name": "",
        "stdout": "Mon Nov 13 11:06:50 CST 2023\nMon Nov 13 11:06:55 CST 2023\n"
    }
}
```

## Get Task by ID
```bash
curl -L '127.0.0.1:5000/api/v1/tasks?task_id=1'
```

response:
```json
{
    "1": {
        "task_id": 1,
        "command": "date; sleep 5; date",
        "timeout_seconds": 6,
        "retry_count": 0,
        "extra": "",
        "key": "",
        "callback_url": "",
        "status": "done",
        "return_code": 0,
        "error_msg": "",
        "start_time": "2023-11-13T11:06:50.863401+08:00",
        "end_time": "2023-11-13T11:06:55.971313+08:00",
        "duration": 5,
        "log_redis_key": "",
        "log_redis_url": "",
        "thread_name": "",
        "stdout": "Mon Nov 13 11:06:50 CST 2023\nMon Nov 13 11:06:55 CST 2023\n"
    }
}
```
