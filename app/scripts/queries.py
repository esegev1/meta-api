
def query_builder(name): 
    if name == "all_posts":
       return """
        SELECT
            id,
            media_product_type
        FROM post_metadata
        WHERE (post_timestamp >= NOW() AT TIME ZONE 'UTC' - INTERVAL %s
        AND post_timestamp <= NOW() AT TIME ZONE 'UTC' - INTERVAL %s)
        OR id IN ('17953889028024104', '18104525737534644', '18078184946041891')
        ;
    """
    elif name == "post_list":
        return """
            Select
                id,
                post_timestamp,
                media_product_type,
                trial_reel,
                short_caption
            FROM post_metadata
            ORDER BY post_timestamp DESC

        """
    elif name == "all_post_activity":
        return "SELECT * FROM post_activity"
    elif name == "activity_by_id":
        return """
            SELECT
                a.id,
                TO_CHAR(a.timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'America/New_York', 'MM/DD HH24:MI')  AS local_time,
                a.views,
                a.views - LAG(a.views, 1) OVER (ORDER BY a.timestamp) AS delta_views,
                a.reach,
                a.reach - LAG(a.reach, 1) OVER (ORDER BY a.timestamp) AS delta_reach,
                a.likes,
                a.likes - LAG(a.likes, 1) OVER (ORDER BY a.timestamp) AS delta_likes,
                a.comments,
                a.comments - LAG(a.comments, 1) OVER (ORDER BY a.timestamp) AS delta_comments,
                a.saves,
                a.saves - LAG(a.saves, 1) OVER (ORDER BY a.timestamp) AS delta_saves,
                a.shares,
                a.shares - LAG(a.shares, 1) OVER (ORDER BY a.timestamp) AS delta_shares
            FROM
                post_activity a
            WHERE
                a.id = %s
            ORDER BY
                a.timestamp DESC;
        """
    elif name == "latest_post_activity":
        return """
            WITH last_x_posts AS (
                SELECT
                    id,
                    post_timestamp,
                    short_caption,
                trial_reel
                FROM post_metadata
                ORDER BY 
                    post_timestamp DESC
                LIMIT 15
            ), 
            latest_post_activity AS (
                SELECT DISTINCT ON (a.id)               
                    a.id,                   
                    a.timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'America/New_York'  AS localized_timestamp,
                    a.views,
                    a.views - LAG(a.views, 1) OVER (ORDER BY a.timestamp) AS delta_views,
                    a.reach,
                    a.reach - LAG(a.reach, 1) OVER (ORDER BY a.timestamp) AS delta_reach,
                    a.likes,                       
                    a.likes - LAG(a.likes, 1) OVER (ORDER BY a.timestamp) AS delta_likes,
                    a.comments,
                    a.comments - LAG(a.comments, 1) OVER (ORDER BY a.timestamp) AS delta_comments,
                    a.saves,
                    a.saves - LAG(a.saves, 1) OVER (ORDER BY a.timestamp) AS delta_saves,
                    a.shares,
                    a.shares - LAG(a.shares, 1) OVER (ORDER BY a.timestamp) AS delta_shares
                FROM
                    post_activity a
                LEFT JOIN post_metadata b
                ON a.id = b.id
                    ORDER BY a.id,
                        a.timestamp DESC
            )
            SELECT
            c.*,
            d.*
            FROM last_x_posts c
            LEFT JOIN latest_post_activity d
            ON c.id=d.id
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
        VALUES (%s, NOW() AT TIME ZONE 'UTC', %s , %s , %s, %s , %s , %s , %s, %s , %s , %s , %s)
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
            VALUES (%s, NOW() AT TIME ZONE 'UTC', %s)
            ;
    """
    elif name == "post_performance_w_delta":
        return """
            SELECT
                a.id,
                a.timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'America/New_York'  AS localized_timestamp,
                b.followers,
                b.timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'America/New_York'  AS metadata_timestamp,
                a.views,
                a.views - LAG(a.views, 1) OVER (ORDER BY a.timestamp) AS delta_views,
                a.reach,
                a.reach - LAG(a.reach, 1) OVER (ORDER BY a.timestamp) AS delta_reach,
                a.likes,
                a.likes - LAG(a.likes, 1) OVER (ORDER BY a.timestamp) AS delta_likes,
                a.comments,
                a.comments - LAG(a.comments, 1) OVER (ORDER BY a.timestamp) AS delta_comments,
                a.saves,
                a.saves - LAG(a.saves, 1) OVER (ORDER BY a.timestamp) AS delta_saves,
                a.shares,
                a.shares - LAG(a.shares, 1) OVER (ORDER BY a.timestamp) AS delta_shares
            FROM
                post_activity a
            LEFT JOIN (
                SELECT 
                    id,
                    timestamp,
                    followers,
                    LAG(timestamp, 1) OVER (ORDER BY timestamp) AS prev_timestamp
                FROM 
                    follower_counts
            ) b
            ON a.timestamp < b.timestamp
            AND (b.prev_timestamp IS NULL OR a.timestamp >= b.prev_timestamp)
            WHERE
                a.id = '17953889028024104'
            ORDER BY
                a.timestamp DESC;
        ;
        """
    elif name == "exec_summary_data":
        return """
            WITH latest_activity AS (
                SELECT DISTINCT ON (id) 
                    id, timestamp, views, likes, comments 
                FROM post_activity 
                ORDER BY id, timestamp DESC
            ),
            activity_totals AS (
                SELECT 
                    SUM(views) as total_views, 
                    SUM(likes) as total_likes, 
                    SUM(comments) AS total_comments 
                FROM latest_activity
            ),
            latest_followers AS (
                SELECT followers 
                FROM follower_counts 
                ORDER BY timestamp DESC 
                LIMIT 1
            )
            SELECT 
                at.total_views,
                at.total_likes,
                at.total_comments,
                lf.followers
            FROM activity_totals at
            CROSS JOIN latest_followers lf
    """
    elif name == "last_x_posts":
        return """
            WITH last_x_posts AS (
                SELECT
                    Id,
                    post_timestamp,
                    short_caption,
                    trial_reel
                FROM post_metadata
                ORDER BY 
                    post_timestamp DESC
                LIMIT 15
            ), 
            latest_post_activity AS (
                SELECT DISTINCT ON (a.id)               
                            a.id,                   
                            a.timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'America/New_York'  AS localized_timestamp,
                            a.views,
                            a.views - LAG(a.views, 1) OVER (ORDER BY a.timestamp) AS delta_views,
                            a.reach,
                            a.reach - LAG(a.reach, 1) OVER (ORDER BY a.timestamp) AS delta_reach,
                            a.likes,                       
                            a.likes - LAG(a.likes, 1) OVER (ORDER BY a.timestamp) AS delta_likes,
                            a.comments,
                            a.comments - LAG(a.comments, 1) OVER (ORDER BY a.timestamp) AS delta_comments,
                            a.saves,
                            a.saves - LAG(a.saves, 1) OVER (ORDER BY a.timestamp) AS delta_saves,
                            a.shares,
                            a.shares - LAG(a.shares, 1) OVER (ORDER BY a.timestamp) AS delta_shares
                        FROM
                            post_activity a
                    LEFT JOIN post_metadata b
                    ON a.id = b.id
                        ORDER BY a.id,
                            a.timestamp DESC
            )
            SELECT
            c.*,
            d.*
            FROM last_x_posts c
            LEFT JOIN latest_post_activity d
            ON c.id=d.id
            ;
        """