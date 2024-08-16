from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import json
import os
from script import *

app = Flask(__name__)

debug_mode = os.getenv("DEBUG", "False").lower() == "true"

scheduler = BackgroundScheduler()
scheduler.start()

# Path to save the configuration
CONFIG_PATH = "config.json"

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(data, f, indent=4)


def scheduled_task():
    config = load_config()
    print("Running scheduled task with config:", config)

    stashdb_url = "https://stashdb.org/graphql"
    stashdb_api_key = config['settings']["stashdbApiKey"]
    whisparr_api_key = config['settings']["whisparrApiKey"]
    whisparr_url = config['settings']["whisparrUrl"]
    rootFolderPath = config['settings']["rootFolderPath"]
    tagsToAdd = config['settings']['tagsToAdd']

    tag_ids_to_add = check_tags(tagsToAdd, whisparr_api_key, whisparr_url)

    response = graphql_query(stashdb_url, stashdb_api_key, query_actors)
    if "data" in response:
        monitored_actors = response["data"]["queryPerformers"]["performers"]
    else:
        return
    for actor in monitored_actors:
        query = query_scenes("performers", actor["id"])
        response = graphql_query(stashdb_url, stashdb_api_key, query)
        if "data" in response:
            scenes = response["data"]["queryScenes"]["scenes"]
            filtered_scenes = filter_scenes(scenes, config["performers"])
            add_scenes_to_whisparr(tag_ids_to_add, rootFolderPath, whisparr_api_key, whisparr_url, filtered_scenes)



    response = graphql_query(stashdb_url, stashdb_api_key, query_studios)
    if "data" in response:
        monitored_studios = response["data"]["queryStudios"]["studios"]
    else:
        return
    for studio in monitored_studios:
        query = query_scenes("parentStudio", studio["id"])
        response = graphql_query(stashdb_url, stashdb_api_key, query)
        if "data" in response:
            scenes = response["data"]["queryScenes"]["scenes"]
            filtered_scenes = filter_scenes(scenes, config["studios"])
            add_scenes_to_whisparr(tag_ids_to_add, rootFolderPath, whisparr_api_key, whisparr_url, filtered_scenes)


@app.route('/')
def index():
    config = load_config()

    # Ensure that config contains default values if keys are missing
    config.setdefault('performers', {})
    config.setdefault('studios', {})
    config.setdefault('settings', {})

    return render_template('index.html', config=config)



@app.route('/process', methods=['POST'])
def process():
    data = request.json
    cron_expression = data['settings']['cronExpression'].split()

    print(data)
    save_config(data)

    # Remove existing job if it exists
    scheduler.remove_all_jobs()

    # Schedule the new job with the validated cron expression
    cron_trigger = CronTrigger(
        minute=cron_expression[0],
        hour=cron_expression[1],
        day=cron_expression[2],
        month=cron_expression[3],
        day_of_week=cron_expression[4]
    )
    scheduler.add_job(scheduled_task, trigger=cron_trigger)

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=debug_mode)
