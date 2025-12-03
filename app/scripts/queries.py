
def query_builder(name): 
    if name == "all_posts":
       return """
        SELECT
            id,
            media_product_type
        FROM post_metadata
        WHERE post_timestamp >= NOW() - INTERVAL %s
        AND post_timestamp <= NOW() - INTERVAL %s
        ;
    """
    elif name == "post_activity":
        return """
        INSERT INTO post_activity (
            id,
            timestamp,
            views,
            reach,
            likes,
            comments,
            shares,
            saves,
            total_view_time,
            total_interactions,
            follows,
            profile_activity,
            profile_visits
        )
        VALUES (%s, NOW() , %s , %s , %s, %s , %s , %s , %s, %s , %s , %s , %s)
    """
    elif name == "new_post_data":
        return """
        INSERT INTO post_metadata (
            id,
            post_timestamp,
            media_type,
            short_caption,
            caption,
            trial_reel
        )
        VALUES (%s, %s , %s , %s , %s, %s )
        ON CONFLICT (id) DO UPDATE
        SET post_timestamp = EXCLUDED.post_timestamp,
            media_type = EXCLUDED.media_type,
            short_caption = EXCLUDED.short_caption,
            caption = EXCLUDED.caption,
            trial_reel = EXCLUDED.trial_reel
        ;
    """
    elif name == "drop_post_metadata":
        return """
        DROP TABLE IF EXISTS post_metadata CASCADE;
    """
    elif name == "populate_post_metadata":
        return """
        INSERT INTO post_metadata (
            id,
            post_timestamp,
            media_type,
            media_product_type,
            short_caption,
            caption,
            trial_reel
        )
        VALUES (%s, %s , %s , %s , %s, %s, %s )
        ON CONFLICT (id) DO UPDATE
        SET post_timestamp = EXCLUDED.post_timestamp,
            media_type = EXCLUDED.media_type,
            short_caption = EXCLUDED.short_caption,
            caption = EXCLUDED.caption,
            trial_reel = EXCLUDED.trial_reel
        ;
    """
    elif name == "follower_counts":
        return """
            INSERT INTO follower_counts (
                id,
                timestamp,
                followers
            )
            VALUES (%s, NOW(), %s)
            ;
    """



       



#     query="""
#         INSERT INTO post_metadata (
#             id,
#             post_timestamp,
#             media_type,
#             short_caption,
#             caption
#         )
#         VALUES (%s, %s , %s , %s , %s )
#         ON CONFLICT (id) DO UPDATE
#         SET post_timestamp = EXCLUDED.post_timestamp,
#             media_type = EXCLUDED.media_type,
#             short_caption = EXCLUDED.short_caption,
#             caption = EXCLUDED.caption
#         ;
#     """

# query="""
#         SELECT
#             id
#         FROM post_metadata
#         WHERE post_timestamp >= NOW() - INTERVAL %s
#         ;
#     """

#  query="""
#         SELECT
#             id
#         FROM post_metadata
#         ORDER BY post_timestamp DESC
#         LIMIT 20
#         ;
#     """

# update_query="""
#         INSERT INTO post_activity (
#             id,
#             timestamp,
#             views,
#             reach,
#             likes,
#             comments,
#             shares,
#             saves,
#             total_view_time
#         )
#         VALUES (%s, NOW() , %s , %s , %s, %s , %s , %s , %s )
#         ;
#     """