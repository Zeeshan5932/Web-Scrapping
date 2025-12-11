import argparse
import sys
from main import run_scraper

def parse_arguments():
    """Parse command line arguments for profile search"""
    parser = argparse.ArgumentParser(description="Instagram Profile Scraper")
    
    parser.add_argument(
        "username", 
        nargs="?",
        type=str, 
        help="Instagram username to search"
    )
    
    parser.add_argument(
        "-n", "--num-posts", 
        type=int, 
        default=20, 
        help="Maximum number of posts to collect (default: 20)"
    )
    
    parser.add_argument(
        "--headless", 
        action="store_true", 
        help="Run Chrome in headless mode"
    )
    
    parser.add_argument(
        "--batch", 
        type=str, 
        help="File with usernames, one per line"
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Process usernames
    if args.batch:
        try:
            with open(args.batch, "r", encoding="utf-8") as batch_file:
                usernames = [line.strip() for line in batch_file if line.strip()]
                
            print(f"Loaded {len(usernames)} usernames")
            
            for i, username in enumerate(usernames):
                # Clean username format
                clean_username = username.replace("@", "").strip()
                print(f"\nProcessing {i+1}/{len(usernames)}: {clean_username}")
                
                run_scraper(
                    search_query=clean_username,
                    max_posts=args.num_posts,
                    max_details=args.num_posts,  # Use same value for simplicity
                    headless=args.headless
                )
                
                if i < len(usernames) - 1:
                    print("Waiting 60 seconds before next profile...")
                    import time
                    time.sleep(60)
        except Exception as e:
            print(f"Error processing batch: {e}")
            sys.exit(1)
    
    elif args.username:
        clean_username = args.username.replace("@", "").strip()
        run_scraper(
            search_query=clean_username,
            max_posts=args.num_posts,
            max_details=args.num_posts,  # Use same value for simplicity
            headless=args.headless
        )
    
    else:
        print("Error: No username provided. Use --help for usage information.")
        parser = argparse.ArgumentParser(description="Instagram Profile Scraper")
        parser.print_help()
        sys.exit(1)
