import os
import requests
from dotenv import load_dotenv
load_dotenv()
import json
print(f"Access Token loaded: {bool(os.getenv('META_ACCESS_TOKEN'))}")
print(f"Access Token (first 20 chars): {os.getenv('META_ACCESS_TOKEN')[:20] if os.getenv('META_ACCESS_TOKEN') else 'None'}")

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
                "fields": "id,timestamp,media_product_type,is_shared_to_feed,caption"

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


        # "media": {
        #     "access_token": ACCESS_TOKEN,
        #     "fields": "id,timestamp,media_type,caption"
        # },
        # "insights": {
        #     "access_token": ACCESS_TOKEN,
        #     "metric": "views,reach,likes,comments,shares,saved,total_interactions,ig_reels_avg_watch_time,ig_reels_video_view_total_time"
        # }
    }

    edge=requestDict[type]["edge"]
    url = f"{BASE_URL}/{id if id!='' else ACCT_ID}{edge}?"
    params = requestDict[type]["params"]
    print(f"id: {id if id!='' else ACCT_ID}, edge: {edge}, url: {url}")
   

    print(f"params: {params}")

    all_posts=[]

    while len(all_posts) < post_count:
        """Loop through results until no more data pages available (pagination)"""

        response = requests.get(url, params=params)
        # print("url: ", url)

        if response.status_code == 200:
            data = response.json()
            if type=="follower_counts_update":
                all_posts=data
                break
            # print("data: ", data)
            # line below is for some of the calls so may need to use it later
            posts = data.get("data", data) 
            # print("posts: ", posts)
            all_posts.extend(posts)
            # print("all_posts: ", all_posts)            
            # Check if there is a next page
            paging = data.get("paging", {})
            next_url = paging.get("next")
            # print("next_url: ", next_url)

            if next_url == None:
                # no more pages
                break

            # use the next url in the next loop
            url = next_url
            params = None # already include in the next url
        else:
            print(f"Error {response.status_code}: {response.json()}")

    return all_posts
# data_to_print = fetch_meta_data(ACCT_ID,"media")
# print(data_to_print[0])
