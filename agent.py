from flask import Flask, jsonify, request
from flask import send_file, send_from_directory
import json
import subprocess
from subprocess import PIPE, STDOUT
import threading
import requests
import os
import time
import copy
import redis
import re

app = Flask(__name__)

BASE_URL = '/api/v1/'

agent_finish_flag = "Agent Command Execution Finished"

base_dir = os.path.dirname(__file__)
stdout_log_file_pattern = os.path.join(base_dir, "log", "{}-out.log")

global_task_id = 0
task_list = dict()


class RealTimeLog:
    def __init__(self, log_file_fd, redis_url=None, log_key=None, skip_if_matchs=None):
        '''
         set skip_if_match = ["^Progress \(\d\):"] if run mvn command
        '''

        self._client = None
        self.skip_if_matchs = list()
        for mat in self.skip_if_matchs:
            self.skip_if_matchs.append(re.compile(mat))

        if redis_url and log_key:
            self.redis_url = redis_url
            if log_key.find("agent_log:") == -1:
                log_key = "agent_log:{}".format(log_key)
            self.log_key = log_key
            self._ttl = 12 * 60 * 60
            # self._pool = redis.ConnectionPool.from_url(redis_url)
            # self._client = redis.StrictRedis(connection_pool=self._pool)
            self._client = redis.from_url(redis_url)
            try:
                self._client.ping()
            except:
                print("Redis is unreachable!! Redis real-time log is disabled!!")
                self._client = None
        self.log_file_fd = log_file_fd

        if self._client:
            self._client.rpush(self.log_key, "Start")
        self.log_file_fd.write("Start\n")

    def refresh_expire_time(self):
        if self._client:
            self._client.expire(self.log_key, self._ttl)

    def write_redis(self, line):
        if self._client:
            self._client.rpush(self.log_key, line)

    def write_log(self, lines):
        try:
            if not isinstance(lines, list):
                lines = [lines]
            for line in lines:
                if isinstance(line, bytes):
                    line = line.decode()
                line = line.strip()
                skip = False
                for re_mat in self.skip_if_matchs:
                    if re_mat.match(line):
                        skip = True
                        break
                if skip is True:
                    continue
                self.write_redis(line)
                self.log_file_fd.write(line+"\n")
        except Exception as e:
            print(e)


def callback(task_id, url, body, retry=True):
    headers = {'Content-Type': 'application/json'}
    count_left = 20
    interval = 6
    while True:
        stop = False
        try:
            _response = requests.post(url, json=body, headers=headers, timeout=10)
            task_list[task_id]["callback_status"] = _response.status_code
            if _response.status_code / 100 == 2:
                stop = True
            elif _response.status_code / 100 == 4:
                stop = True
        except Exception as e:
            print("Can not send call back: {}".format(e))
            task_list[task_id]["callback_status"] = str(e)
        finally:
            if not retry:
                break
            if stop:
                break
            if count_left <= 0:
                break
            count_left -= 1
            time.sleep(interval)


def read_log_file(path, offset=0, count=None):
    file_size = os.path.getsize(path)
    if isinstance(offset, bytes):
        offset = int(offset.decode())
    elif isinstance(offset, str):
        offset = int(offset)
    if not count:
        count = file_size - offset
    elif isinstance(count, bytes):
        count = int(count.decode())
    elif isinstance(count, str):
        count = int(count)

    log_list = list()
    recv_size = 0

    with open(path, 'r') as o:
        if offset:
            o.seek(offset)
        unit_size = 1024 if count > 1024 else count
        d = o.read(unit_size)
        while d:
            if isinstance(d, bytes):
                d = d.decode()
            log_list.append(d)
            recv_size += len(d)
            if recv_size >= count:
                break
            d = o.read(unit_size)
    return "".join(log_list)


def run_thread(task_id, command, callback_url):
    log_redis_key = task_list[task_id].get("log_redis_key", None)
    log_redis_url = task_list[task_id].get("log_redis_url", None)
    stdout_log_file = stdout_log_file_pattern.format(task_id)
    task_list[task_id]["stdout_file"] = stdout_log_file
    outfile = open(stdout_log_file, 'w')
    realtime_logger = RealTimeLog(outfile, log_redis_url, log_redis_key)

    process = subprocess.Popen(command, stdin=PIPE, stdout=PIPE,
                             stderr=STDOUT, shell=True, bufsize=0,
                             universal_newlines=True)
    # return_code = child.wait(timeout=12*60*60)

    while True:
        output = process.stdout.readline()
        if not output and process.poll() is not None:
            break
        if output:
            # print("{} stdout: {}".format(time.time(), output))
            realtime_logger.write_log(output)

    return_code = process.wait()

    realtime_logger.write_log(agent_finish_flag)
    realtime_logger.refresh_expire_time()
    outfile.flush()
    outfile.close()

    print("Command return code: {}".format(return_code))
    task_list[task_id]["status"] = "done"
    task_list[task_id]["return_code"] = return_code
    task_list[task_id]["finish_time"] = time.time()
    task_list[task_id]["duration"] = task_list[task_id]["finish_time"] - \
                                     task_list[task_id]["start_time"]

    out_log = read_log_file(stdout_log_file)
    if return_code != 0:
        out_log = out_log[-4000:]
    else:
        out_log = out_log[-1000:]

    if callback_url:
        cb_body = {
            "return_code": return_code,
            "stdout": out_log,
            "extra": task_list[task_id]["extra"],
            "key": task_list[task_id]["key"],
            "duration": task_list[task_id]["duration"]
        }
        if realtime_logger:
            cb_body["log_key"] = log_redis_key
        callback(task_id, callback_url, cb_body)


def handle_task(command, callback_url, extra, key,
                log_redis_key, log_redis_url):
    global global_task_id
    global_task_id += 1
    t_id = global_task_id
    task_list[t_id] = dict()
    task_list[t_id]["task_id"] = t_id
    task_list[t_id]["command"] = command
    task_list[t_id]["extra"] = extra
    task_list[t_id]["key"] = key
    task_list[t_id]["callback_url"] = callback_url
    task_list[t_id]["status"] = "doing"
    task_list[t_id]["start_time"] = time.time()
    if log_redis_key and log_redis_url:
        task_list[t_id]["log_redis_key"] = log_redis_key
        task_list[t_id]["log_redis_url"] = log_redis_url

    t = threading.Thread(target=run_thread,
                         args=(t_id, command, callback_url))
    t.start()
    t.setName("Handle_task_{}".format(t_id))
    print(t.getName())
    task_list[t_id]["thread_name"] = t.getName()
    return t_id


@app.route(BASE_URL + 'tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'GET':
        global task_list
        t_id = request.args.get("task_id", None)
        offset = request.args.get("offset", 0)
        count = request.args.get("count", None)
        if t_id:
            t_id = int(t_id)
            info = copy.deepcopy(task_list[t_id])
            info["stdout"] = read_log_file(info["stdout_file"],
                                           offset, count)
            resp = {t_id: info}
        else:
            resp = task_list
        return jsonify(resp), 200

    elif request.method == 'POST':
        body = request.json
        if not body and request.data:
            print(request.data)
            body = json.loads(request.data)
        print(body)
        if not body:
            resp = {
                "status": "error",
                "info": "No request body!!"
            }
            return jsonify(resp), 400

        callback_url = body.get("callback_url", None)
        command = body.get("command", None)
        key = body.get("key", None)
        extra = body.get("extra", None)
        log_redis_key = body.get("log_redis_key", key)
        log_redis_url = body.get("log_redis_url", None)

        if not command:
            resp = {
                "status": "error",
                "info": "No command!!"
            }
            return jsonify(resp), 400

        t_id = handle_task(command, callback_url, extra, key,
                           log_redis_key, log_redis_url)
        resp = {
            "status": "created",
            "task_id": t_id
        }
        return jsonify(resp), 201


@app.route(BASE_URL + 'file', methods=['GET', 'POST'])
def file():
    if request.method == 'GET':
        file_path = request.args.get("file_path", None)
        if not file_path:
            resp = {
                "status": "error",
                "info": "No file_path!!"
            }
            return jsonify(resp), 400
        if not os.path.isfile(file_path):
            resp = {
                "status": "error",
                "info": "file {} not found in agent fs!!".format(file_path)
            }
            return jsonify(resp), 404


        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        return send_from_directory(file_dir, file_name, as_attachment=True)

    elif request.method == 'POST':
        file = request.files['file']
        target_path = request.form.get("target_path", None)
        if not target_path:
            resp = {
                "status": "error",
                "info": "No target_path!!"
            }
            return jsonify(resp), 400

        print(request.files)
        file.save(target_path)
        resp = {
            "status": "success"
        }
        return jsonify(resp), 201


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)
