import sys
from agent import app

Usage = '''
    Usage: 
        python manage.py run/api-doc
        
'''

Api_doc = '''
{
	"info": {
		"name": "Agent API",
		"schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
	},
	"item": [
		{
			"name": "get tasks",
			"request": {
				"method": "GET",
				"header": [],
				"body": {
					"mode": "raw",
					"raw": ""
				},
				"url": {
					"raw": "127.0.0.1:5000/api/v1/tasks",
					"host": [
						"127",
						"0",
						"0",
						"1"
					],
					"port": "5000",
					"path": [
						"api",
						"v1",
						"tasks"
					]
				}
			},
			"response": []
		},
		{
			"name": "get tasks 1",
			"request": {
				"method": "GET",
				"header": [],
				"body": {
					"mode": "raw",
					"raw": ""
				},
				"url": {
					"raw": "127.0.0.1:5000/api/v1/tasks?task_id=1",
					"host": [
						"127",
						"0",
						"0",
						"1"
					],
					"port": "5000",
					"path": [
						"api",
						"v1",
						"tasks"
					],
					"query": [
						{
							"key": "task_id",
							"value": "1"
						}
					]
				}
			},
			"response": []
		},
		{
			"name": "post  tasks",
			"request": {
				"method": "POST",
				"header": [
					{
						"key": "Content-Type",
						"name": "Content-Type",
						"value": "application/json",
						"type": "text"
					}
				],
				"body": {
					"mode": "raw",
					"raw": "{\n    \"command\": \"ls -l\"\n}"
				},
				"url": {
					"raw": "127.0.0.1:5000/api/v1/tasks",
					"host": [
						"127",
						"0",
						"0",
						"1"
					],
					"port": "5000",
					"path": [
						"api",
						"v1",
						"tasks"
					]
				}
			},
			"response": []
		},
		{
			"name": "post file",
			"request": {
				"method": "POST",
				"header": [
					{
						"key": "Content-Type",
						"name": "Content-Type",
						"value": "application/x-www-form-urlencoded",
						"type": "text"
					}
				],
				"body": {
					"mode": "formdata",
					"formdata": [
						{
							"key": "target_path",
							"value": "aaa.json",
							"type": "text"
						},
						{
							"key": "file",
							"type": "file",
							"src": ""
						}
					]
				},
				"url": {
					"raw": "127.0.0.1:5000/api/v1/file",
					"host": [
						"127",
						"0",
						"0",
						"1"
					],
					"port": "5000",
					"path": [
						"api",
						"v1",
						"file"
					]
				}
			},
			"response": []
		},
		{
			"name": "get file",
			"protocolProfileBehavior": {
				"disableBodyPruning": true
			},
			"request": {
				"method": "GET",
				"header": [
					{
						"key": "Content-Type",
						"name": "Content-Type",
						"type": "text",
						"value": "application/x-www-form-urlencoded"
					}
				],
				"body": {
					"mode": "formdata",
					"formdata": [
						{
							"key": "",
							"value": "",
							"type": "text",
							"disabled": true
						}
					]
				},
				"url": {
					"raw": "127.0.0.1:5000/api/v1/file?file_path=aaa.json",
					"host": [
						"127",
						"0",
						"0",
						"1"
					],
					"port": "5000",
					"path": [
						"api",
						"v1",
						"file"
					],
					"query": [
						{
							"key": "file_path",
							"value": "aaa.json"
						}
					]
				}
			},
			"response": []
		}
	]
}
'''


def main():
    if len(sys.argv) == 1:
        print(Usage)
        sys.exit(1)
    else:
        param = sys.argv[1]

    if param == 'run':
        app.run(host="0.0.0.0", port=5000, debug=False)
    elif param == 'api-doc':
        with open('agent-api-postman-collection.json', 'w') as fd:
            fd.write(Api_doc)
        print("Postman collection json file has been saved in file agent-api-postman-collection.json")
        sys.exit(0)
    else:
        print('Unresolved Parameter: ', param)
        print(Usage)
        sys.exit(1)


if __name__ == '__main__':
    main()
