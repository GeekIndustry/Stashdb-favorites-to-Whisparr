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


def scheduled_sync():
    config = load_config()
    print("Running scheduled sync with config:", config)

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


def scheduled_scan():
    config = load_config()
    print("Running scheduled Stash library scan.")

    stashApp_url = config['settings']["stashAppUrl"]
    stashApp_api_key = config['settings']["stashAppApiKey"]

    defaults_settings_response = graphql_query(stashApp_url, stashApp_api_key, query_defaults_scan_settings)


    if defaults_settings_response and "data" in defaults_settings_response:
        defaults_settings = defaults_settings_response.get("data", {}).get("configuration", {}).get("defaults", {}).get("scan", {})

        scan_input = {
            "scanGenerateCovers": defaults_settings.get("scanGenerateCovers", False),
            "scanGeneratePreviews": defaults_settings.get("scanGeneratePreviews", False),
            "scanGenerateImagePreviews": defaults_settings.get("scanGenerateImagePreviews", False),
            "scanGenerateSprites": defaults_settings.get("scanGenerateSprites", False),
            "scanGeneratePhashes": defaults_settings.get("scanGeneratePhashes", False),
            "scanGenerateThumbnails": defaults_settings.get("scanGenerateThumbnails", False),
            "scanGenerateClipPreviews": defaults_settings.get("scanGenerateClipPreviews", False)
        }

        print(scan_input)
        
        mutation_response = graphql_query(
            stashApp_url,
            stashApp_api_key,
            mutation_library_scan,
            variables={"input": scan_input}
        )

        if mutation_response:
            print(json.dumps(mutation_response, indent=2))
            print("Scan performed successfully.")
        else:
            print("Failed to perform scan.")
    else:
        print("Failed to retrieve default settings.")



    return



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
    print(data)
    save_config(data)

    # Remove existing jobs if it exists
    scheduler.remove_all_jobs()

    # Schedule the new jobs with the validated cron expression
    sync_cron_expression = data['settings']['cronExpressionSyncer'].split()
    cron_trigger = CronTrigger(
        minute=sync_cron_expression[0],
        hour=sync_cron_expression[1],
        day=sync_cron_expression[2],
        month=sync_cron_expression[3],
        day_of_week=sync_cron_expression[4]
    )
    scheduler.add_job(scheduled_sync, trigger=cron_trigger)

    scan_cron_expression = data['settings']['cronExpressionScan'].split()
    cron_trigger = CronTrigger(
        minute=scan_cron_expression[0],
        hour=scan_cron_expression[1],
        day=scan_cron_expression[2],
        month=scan_cron_expression[3],
        day_of_week=scan_cron_expression[4]
    )
    scheduler.add_job(scheduled_scan, trigger=cron_trigger)

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=debug_mode)
