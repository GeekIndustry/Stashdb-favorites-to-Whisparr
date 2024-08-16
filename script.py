import requests


# Requête GraphQL pour obtenir les acteurs favoris
query_actors = """
query {
  queryPerformers(input: {is_favorite: true}) {
    performers {
      id
      name
    }
  }
}
"""

query_studios = """
query {
  queryStudios(input: {is_favorite: true}) {
    studios {
      id
      name
    }
  }
}
"""

# Requête GraphQL pour obtenir les scènes d'un acteur
def query_scenes(type, id):
    if type == "parentStudio":
        input_structure = f'{type}: "{id}"'
    else:
        input_structure = f"""
        {type}: {{
            value: ["{id}"],
            modifier: INCLUDES
        }}"""

    return f"""
    query {{
      queryScenes(
        input: {{
          {input_structure}
        }}
      ) {{
        scenes {{
          id
          title
          performers {{
            performer {{
              id
              name
              gender
            }}
          }}
          studio {{
            name
            parent {{
              name
            }}
          }}
          tags {{
            name
            aliases       
          }}
        }}
      }}
    }}
    """



# Fonction pour effectuer une requête GraphQL
def graphql_query(stashdb_url, stashdb_api_key, query):
    headers = {
        "ApiKey": stashdb_api_key, 
        "Content-Type": "application/json"
    }
    response = requests.post(
        stashdb_url,
        json={'query': query},
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur lors de la requête GraphQL : {response.status_code} - {response.content}")
        return None

# Ajouter les scènes à Whisparr
def add_scenes_to_whisparr(tagsToAdd, rootFolderPath, whisparr_api_key, whisparr_url, scenes):
    for scene in scenes:
        print(f"Processing scene: {scene['title']}")  

        stash_id = str(scene["id"]) 
        
        data = {
            "addOptions": {
                "monitor": "movieOnly",
                "searchForMovie": True,
            },
            "foreignId": stash_id,  
            "stashId": stash_id,  
            "titleSlug": stash_id,
            "monitored": True,
            "qualityProfileId": 1, 
            "title": scene["title"],  
            "itemType": "scene",
            "rootFolderPath": rootFolderPath,
            'tags': tagsToAdd
        }
        
        headers = {
            "X-Api-Key": whisparr_api_key,
            "Content-Type": "application/json"
        }

        print(f"ForeignId utilisé : {stash_id}")  
        response = requests.post(f"{whisparr_url}/api/v3/movie", json=data, headers=headers)
        
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 201:
            print(f"Ajouté scène : {scene['title']}")
        else:
            print(f"Échec de l'ajout de la scène : {scene['title']} - {response.content}")


def filter_scenes(scenes, config):
    # Get the criteria from the config
    excluded_genders = set(config.get('excludeGender', []))
    excluded_tags = set(config.get('tags', []))
    excluded_studios = set(config.get('studios', []))

    filtered_scenes = []
    
    for scene in scenes:
        # Filter by performers' gender
        if any(performer['performer']['gender'] in excluded_genders for performer in scene['performers']):
            continue
        

        # Filter by tags and their aliases
        if excluded_tags:
            scene_tags = set()
            for tag in scene['tags']:
                scene_tags.add(tag['name'])
                scene_tags.update(tag['aliases'])

            # If there's no intersection, skip this scene
            if scene_tags.intersection(excluded_tags):
                continue
            

        # Filter by studios
        studio_name = scene['studio']['name']
        parent_studio_name = scene['studio']['parent']['name'] if scene['studio']['parent'] else None
        if excluded_studios and studio_name in excluded_studios or parent_studio_name in excluded_studios:
            continue
        

        # If the scene passes all filters, add it to the list
        filtered_scenes.append(scene)
    
    return filtered_scenes


def check_tags(tags, whisparr_api_key, whisparr_url):
    headers = {
        "X-Api-Key": whisparr_api_key,
    }

    # Correctly use the GET method to retrieve existing tags
    response = requests.get(f"{whisparr_url}/api/v3/tag", headers=headers)
    print(f"Response status code: {response.status_code}")
    
    if response.status_code == 200:
        existing_tags = response.json()
        existing_tag_map = {tag['label']: tag['id'] for tag in existing_tags}

        tag_ids_to_add = []

        for tag_to_check in tags:
            if tag_to_check in existing_tag_map:
                print(f"{tag_to_check} is already present!")
                tag_ids_to_add.append(existing_tag_map[tag_to_check])
            else:
                print(f"{tag_to_check} is not present!")
                new_tag_id = create_tags(tag_to_check, whisparr_api_key, whisparr_url)
                if new_tag_id:
                    tag_ids_to_add.append(new_tag_id)

        return tag_ids_to_add  # Return the list of tag IDs to be used in the POST request
    else:
        print(f"Failed to retrieve tags: {response.content}")
        return []

def create_tags(tag, whisparr_api_key, whisparr_url):
    print(f"Creating tag: {tag}")  

    data = {
        "label": tag
    }
    
    headers = {
        "X-Api-Key": whisparr_api_key,
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{whisparr_url}/api/v3/tag", json=data, headers=headers)
    print(f"Response status code: {response.status_code}")
    
    if response.status_code == 201:
        tag_id = response.json().get('id')
        print(f"Tag added with ID: {tag_id}")
        return tag_id
    else:
        print(f"Failed to add tag: {tag} - {response.content}")
        return None

