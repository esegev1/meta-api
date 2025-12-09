import os
import requests
from dotenv import load_dotenv
load_dotenv()
import json

ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN');

ACCT_ID = os.getenv('META_IG_ACCT_ID');

BASE_URL = "https://graph.facebook.com/v24.0"

def fetch_meta_data_post(id, type, post_count=10):
    """
     Call Meta API to fetch data
     Args: edge (media or insights)
    """
    # Dict withe params tied to the edge name, this should be changed to named 
    # by use case but needs clean solution for edge variable
    requestDict = {
        "new_post_data": {
            "edge" : "",
            "params" : {
                "access_token": ACCESS_TOKEN,
                "fields": "id,timestamp,media_type,media_product_type,is_shared_to_feed,caption"

            }
            
        },
        "post_activity_data_REELS": {
            "edge" : "/insights",
            "params" : {
                "access_token": ACCESS_TOKEN,
                # "metric": "views,reach,likes,comments,shares,saved,total_interactions,ig_reels_avg_watch_time,ig_reels_video_view_total_time",
                "metric": "views,reach,likes,comments,shares,saved,ig_reels_avg_watch_time,ig_reels_video_view_total_time,total_interactions"
            }            
        },
        "post_activity_data_FEED": {
            "edge" : "/insights",
            "params" : {
                "access_token": ACCESS_TOKEN,
                # "metric": "impressions,reach,likes,comments,saved,total_interactions",
                "metric": "views,reach,likes,comments,shares,saved,follows,profile_activity,profile_visits,total_interactions"
                
            }
          } ,
        "post_activity_data_STORY": {
            "edge" : "/insights",
            "params" : {
                "access_token": ACCESS_TOKEN,
                # "metric": "impressions,reach,likes,comments,saved,total_interactions",
                "metric": "views,reach,shares,follows,navigation,profile_activity,profile_visits,replies,total_interactions"
            }            
        } ,
        "post_metadata_rebuild": {
            "edge" : "/media",
            "params" : {
                "access_token": ACCESS_TOKEN,
                "fields": "id,timestamp,media_product_type,media_type,is_shared_to_feed,caption",
                "limit": post_count
            }            
        } ,
        "follower_counts_update": {
            "edge" : "",
            "params" : {
                "access_token": ACCESS_TOKEN,
                "fields": "id,followers_count",
            }            
        } ,
    }

    edge=requestDict[type]["edge"]
    url = f"{BASE_URL}/{id if id!='' else ACCT_ID}{edge}?"
    params = requestDict[type]["params"]
    print(f"id: {id if id!='' else ACCT_ID}, edge: {edge}, url: {url}")
    print(f"params => Token ok: {True if len(ACCESS_TOKEN) > 1 else False}, fields/metrics: {params['metric'] if 'metric' in params else params['fields']}")
    results = []

    for attempt in range(3):
        try:
            while (True):
                print("attempt: ", attempt)
                # Call Meta's Api and format response data
                response = requests.get(url, params=params)
                print("response: ", response)
                
                # this will force an exception for code 4xx and 5xx
                response.raise_for_status()
                data = response.json()

                if type=="follower_counts_update":
                    records = data
                else:
                    records = data.get("data", data)
            
                results.append(records)

                paging = data.get("paging", {})
                next_url = paging.get("next")
                # print("next_url: ", next_url)

                if next_url is None:
                    # no more pages
                    break

                # use the next url in the next loop
                url = next_url
                params = None # already include in the next url    
            # Success, exit retry loop
            break  
        except Exception as e:
            error_data = response.json()
            meta_error_code = error_data.get('error', {}).get('code')
            
            if attempt == 2:
                # Last attempt  
                print(f"✗ Post {id} failed after 3 tries: {e}")
                break
            elif meta_error_code == 4 or meta_error_code == 17:
                print(f"✗ You hit rate limits, try again later")
                break
            elif meta_error_code == 100:
                print(f"✗ That post id does not exist")
                break
            else:
                print(f"error language: {error_data.get('error', {})}")
                print(f"✗ Post {id} failed with code: {meta_error_code}, error msg: {e}")
                break

    print("results data: ", results)
    return results

