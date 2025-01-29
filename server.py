import multiprocessing
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import json
import psutil
import time
import main
import os
from auth import verify

app = Flask(__name__, static_folder='static_ui')
CORS(app)

# Use multiprocessing Manager to share a dictionary between processes
manager = multiprocessing.Manager()
all_tasks = manager.dict()
tasks = {}  # Global tasks dictionary to hold the process instances
file_lock = multiprocessing.Lock()

# Load existing tasks from file into shared memory
with open("all_tasks.json", 'r') as fle:
    all_tasks.update(json.loads(fle.read()))

def write_tasks_to_file():
    with file_lock:
        with open("all_tasks.json", "w") as fle:
            fle.write(json.dumps(dict(all_tasks)))

def thread_samp(obj, id):
    global all_tasks
    try:
        north, east = obj['ne_lat'], obj['ne_lon']
        south, west = obj['sw_lat'], obj['sw_lon']

        # north, east = 11.07124, 77.011059 
        # south, west = 11.070540, 77.004476

        # print(obj['map_layer'])
        main.tile_renderer.render(north,east,south,west,id,obj['map_layer'])
        main.init.create_env(id)
        main.run_process(north,east,south,west,id,id,"raster_"+id,id,id)
        
        temp = dict(all_tasks)
        temp[id]["status"] = "COMPLETED"
        all_tasks.update(dict(temp))
        write_tasks_to_file()
        del tasks[id]
    except:
        temp = dict(all_tasks)
        temp[id]["status"] = "ERROR"
        all_tasks.update(dict(temp))
        write_tasks_to_file()
        del tasks[id]


def init_new_task(obj):
    global all_tasks, tasks  # Ensure tasks is global
    try:
        task_id = str((len(all_tasks)+1)) + obj['task_id']
        tasks[task_id] = multiprocessing.Process(target=thread_samp, args=(obj, task_id))
        all_tasks[task_id] = {"status": "RUNNING"}
        
        write_tasks_to_file()

        tasks[task_id].start()
        return "INITIATED"
    except Exception as e:
        return str(e)


@app.route('/')
@app.route('/<path:path>')
def serve_static_files(path='index.html'):
    return send_from_directory(app.static_folder, path)


@app.route('/api/<path:path>')
def api(path):
    if verify(request.headers.get('Auth-Token')):
        global all_tasks
        if path == "bsd":
            memory_info = psutil.virtual_memory()
            return {"ram": memory_info.used, "tasks": len(all_tasks), "tasks_list": dict(all_tasks)}
    return "not_Authorised"

@app.route('/api/logs/<path:path>')
def logs(path):
    if verify(request.headers.get('Auth-Token')):
        return send_from_directory("logs", path + ".txt")
    return "not_Authorised"

    
@app.route('/process_data', methods=['POST'])
def process_data():
    if verify(request.headers.get('Auth-Token')):
        data = request.get_json()
        return {"status": init_new_task(data)}
    return "not_Authorised"

@app.route('/api/shp/<path:path>', methods=['GET'])
def list_files(path):
    if verify(request.headers.get('Auth-Token')):
        # Normalize the path to avoid directory traversal issues
        folder_path = os.path.abspath("shp/"+path)

        print(folder_path)
        # Check if the folder exists
        if not os.path.isdir(folder_path):
            return jsonify({"error": "The specified folder does not exist."}), 400

        try:\
            # List the files in the folder
            files = os.listdir(folder_path)
            # Filter only files (ignore directories)
            files = [f for f in files if os.path.isfile(os.path.join(folder_path, f))]
            return jsonify({"files": files}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return "not_Authorised"

@app.route('/api/shp/get_file/<path:path>', methods=['GET'])
def get_files(path):
    if True:
        print(path.split('.')[0]+path)
        return send_from_directory("shp", path.split('.')[0]+"/"+path)
    return "not_Authorised"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
