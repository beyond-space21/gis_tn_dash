import multiprocessing
from flask import Flask, send_from_directory, request
from flask_cors import CORS
import json
import psutil
import time
import main

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

        main.tile_renderer.render(north,east,south,west,id)
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
        task_id = obj['task_id']
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
    global all_tasks
    if path == "bsd":
        memory_info = psutil.virtual_memory()
        return {"ram": memory_info.used, "tasks": len(all_tasks), "tasks_list": dict(all_tasks)}

@app.route('/api/logs/<path:path>')
def logs(path):
    return send_from_directory("logs", path + ".html")
    
@app.route('/process_data', methods=['POST'])
def process_data():
    data = request.get_json()
    return {"status": init_new_task(data)}
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
