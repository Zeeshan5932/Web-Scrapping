import os
import json
import time
import statistics
from datetime import datetime
from collections import Counter

def generate_search_report(folder_path):
    """
    Generate a detailed summary report for a search query folder
    
    Args:
        folder_path: Path to the search query folder
        
    Returns:
        dict: Report data
    """
    # Initialize report data
    report = {
        "report_generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "search_query": os.path.basename(folder_path),
        "scrape_sessions": [],
        "total_posts_found": 0,
        "summary": {
            "top_users": [],
            "top_hashtags": [],
            "top_mentions": [],
            "post_types": {},
            "avg_likes": 0,
            "avg_comments": 0,
            "most_engaged_posts": [],
            "engagement_by_time": {}
        }
    }
    
    # Track all hashtags and mentions across all sessions
    all_hashtags = []
    all_mentions = []
    all_users = []
    all_post_types = []
    like_counts = []
    comment_counts = []
    
    # Process each session folder
    session_folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    
    for session_folder in session_folders:
        session_path = os.path.join(folder_path, session_folder)
        
        # Check for summary file
        summary_path = os.path.join(session_path, "summary.json")
        if not os.path.exists(summary_path):
            continue
            
        # Load summary data
        with open(summary_path, "r", encoding="utf-8") as summary_file:
            summary_data = json.load(summary_file)
            
        session_info = {
            "timestamp": summary_data.get("scrape_timestamp", session_folder),
            "posts_found": summary_data.get("total_posts_found", 0),
            "posts_extracted": summary_data.get("posts_extracted", 0)
        }
        
        report["scrape_sessions"].append(session_info)
        report["total_posts_found"] += session_info["posts_found"]
        
        # Get all posts file
        all_posts_path = os.path.join(session_path, "all_posts.json")
        if os.path.exists(all_posts_path):
            with open(all_posts_path, "r", encoding="utf-8") as posts_file:
                posts_data = json.load(posts_file)
                post_data = posts_data.get("post_data", [])
                
                # Process each post
                for post in post_data:
                    # Collect user
                    username = post.get("username")
                    if username and username != "Not found":
                        all_users.append(username)
                        
                    # Collect hashtags
                    hashtags = post.get("hashtags", [])
                    all_hashtags.extend(hashtags)
                    
                    # Collect mentions
                    mentions = post.get("mentions", [])
                    all_mentions.extend(mentions)
                    
                    # Collect post type
                    post_type = post.get("post_type", "Unknown")
                    all_post_types.append(post_type)
                    
                    # Collect engagement metrics
                    try:
                        likes_text = post.get("likes_count", "0")
                        # Clean up the text and convert to integer
                        if likes_text != "Not available":
                            likes = int(''.join(c for c in str(likes_text) if c.isdigit()))
                            like_counts.append(likes)
                    except:
                        pass
                        
                    try:
                        comments_text = post.get("comments_count", "0")
                        # Clean up the text and convert to integer
                        if comments_text != "Not available":
                            comments = int(''.join(c for c in str(comments_text) if c.isdigit()))
                            comment_counts.append(comments)
                    except:
                        pass
                        
        # Process individual post files as well to ensure we get all data
        post_files = [f for f in os.listdir(session_path) if f.startswith("post_") and f.endswith(".json")]
        
        for post_file in post_files:
            post_path = os.path.join(session_path, post_file)
            try:
                with open(post_path, "r", encoding="utf-8") as file:
                    post = json.load(file)
                    
                    # Collect data only if not already processed from all_posts.json
                    if post.get("url") not in [p.get("url") for p in post_data]:
                        # Collect user
                        username = post.get("username")
                        if username and username != "Not found":
                            all_users.append(username)
                            
                        # Collect hashtags
                        hashtags = post.get("hashtags", [])
                        all_hashtags.extend(hashtags)
                        
                        # Collect mentions
                        mentions = post.get("mentions", [])
                        all_mentions.extend(mentions)
                        
                        # Collect post type
                        post_type = post.get("post_type", "Unknown")
                        all_post_types.append(post_type)
                        
                        # Collect engagement metrics (same as above)
                        try:
                            likes_text = post.get("likes_count", "0")
                            if likes_text != "Not available":
                                likes = int(''.join(c for c in str(likes_text) if c.isdigit()))
                                like_counts.append(likes)
                        except:
                            pass
                            
                        try:
                            comments_text = post.get("comments_count", "0")
                            if comments_text != "Not available":
                                comments = int(''.join(c for c in str(comments_text) if c.isdigit()))
                                comment_counts.append(comments)
                        except:
                            pass
            except Exception as e:
                print(f"Error processing post file {post_file}: {e}")
    
    # Compute summary statistics
    # Top users
    user_counter = Counter(all_users)
    report["summary"]["top_users"] = [{"username": user, "posts": count} 
                                     for user, count in user_counter.most_common(10)]
                                     
    # Top hashtags
    hashtag_counter = Counter(all_hashtags)
    report["summary"]["top_hashtags"] = [{"hashtag": tag, "occurrences": count} 
                                        for tag, count in hashtag_counter.most_common(20)]
                                        
    # Top mentions
    mention_counter = Counter(all_mentions)
    report["summary"]["top_mentions"] = [{"mention": mention, "occurrences": count} 
                                        for mention, count in mention_counter.most_common(10)]
                                        
    # Post types distribution
    post_type_counter = Counter(all_post_types)
    report["summary"]["post_types"] = {post_type: count for post_type, count in post_type_counter.items()}
    
    # Average engagement
    if like_counts:
        report["summary"]["avg_likes"] = sum(like_counts) / len(like_counts)
        
    if comment_counts:
        report["summary"]["avg_comments"] = sum(comment_counts) / len(comment_counts)
        
    # Generate report file
    report_path = os.path.join(folder_path, f"report_{int(time.time())}.json")
    with open(report_path, "w", encoding="utf-8") as report_file:
        json.dump(report, report_file, indent=4, ensure_ascii=False)
        
    print(f"Generated report at {report_path}")
    return report

def generate_html_report(report_data, output_path=None):
    """
    Generate an HTML report from the report data
    
    Args:
        report_data: Dictionary containing report data
        output_path: Path to save HTML report (optional)
        
    Returns:
        str: HTML content
    """
    search_query = report_data["search_query"]
    
    if not output_path:
        # Generate default output path
        timestamp = int(time.time())
        output_path = f"data/{search_query}/report_{timestamp}.html"
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Instagram Scraper Report: {search_query}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            h1, h2, h3 {{
                color: #2a5885;
            }}
            .report-header {{
                background-color: #2a5885;
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                margin-bottom: 30px;
            }}
            .report-section {{
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }}
            .stats-container {{
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                justify-content: space-between;
            }}
            .stat-card {{
                background-color: #f0f7ff;
                border-left: 5px solid #2a5885;
                padding: 15px;
                border-radius: 5px;
                flex: 1;
                min-width: 200px;
            }}
            .stat-value {{
                font-size: 1.8rem;
                font-weight: bold;
                color: #2a5885;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            th, td {{
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f2f7fc;
                font-weight: bold;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
        </style>
    </head>
    <body>
        <div class="report-header">
            <h1>Instagram Scraper Report</h1>
            <p>Search Query: <strong>{search_query}</strong></p>
            <p>Report Generated: {report_data["report_generated_at"]}</p>
        </div>
        
        <div class="report-section">
            <h2>Overview</h2>
            <div class="stats-container">
                <div class="stat-card">
                    <h3>Total Posts</h3>
                    <div class="stat-value">{report_data["total_posts_found"]}</div>
                </div>
                <div class="stat-card">
                    <h3>Avg. Likes</h3>
                    <div class="stat-value">{int(report_data["summary"]["avg_likes"])}</div>
                </div>
                <div class="stat-card">
                    <h3>Avg. Comments</h3>
                    <div class="stat-value">{int(report_data["summary"]["avg_comments"])}</div>
                </div>
                <div class="stat-card">
                    <h3>Total Sessions</h3>
                    <div class="stat-value">{len(report_data["scrape_sessions"])}</div>
                </div>
            </div>
        </div>
        
        <div class="report-section">
            <h2>Top Users</h2>
            <table>
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Posts</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add top users
    for user in report_data["summary"]["top_users"]:
        html_content += f"""
                    <tr>
                        <td>{user["username"]}</td>
                        <td>{user["posts"]}</td>
                    </tr>
        """
    
    html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="report-section">
            <h2>Top Hashtags</h2>
            <table>
                <thead>
                    <tr>
                        <th>Hashtag</th>
                        <th>Occurrences</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add top hashtags
    for tag in report_data["summary"]["top_hashtags"]:
        html_content += f"""
                    <tr>
                        <td>{tag["hashtag"]}</td>
                        <td>{tag["occurrences"]}</td>
                    </tr>
        """
    
    html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="report-section">
            <h2>Post Types Distribution</h2>
            <table>
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>Count</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add post types
    for post_type, count in report_data["summary"]["post_types"].items():
        html_content += f"""
                    <tr>
                        <td>{post_type}</td>
                        <td>{count}</td>
                    </tr>
        """
    
    html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="report-section">
            <h2>Scrape Sessions</h2>
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Posts Found</th>
                        <th>Posts Extracted</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add scrape sessions
    for session in report_data["scrape_sessions"]:
        html_content += f"""
                    <tr>
                        <td>{session["timestamp"]}</td>
                        <td>{session["posts_found"]}</td>
                        <td>{session["posts_extracted"]}</td>
                    </tr>
        """
    
    html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="report-section">
            <h2>Top Mentions</h2>
            <table>
                <thead>
                    <tr>
                        <th>Mention</th>
                        <th>Occurrences</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add top mentions
    for mention in report_data["summary"]["top_mentions"]:
        html_content += f"""
                    <tr>
                        <td>{mention["mention"]}</td>
                        <td>{mention["occurrences"]}</td>
                    </tr>
        """
    
    html_content += """
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>Generated by Instagram Scraper</p>
        </footer>
    </body>
    </html>
    """
    
    # Write HTML to file
    with open(output_path, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)
        
    print(f"HTML report saved to {output_path}")
    return html_content
