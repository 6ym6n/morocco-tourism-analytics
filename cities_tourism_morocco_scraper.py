import praw
import pymongo
import json
import time
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedditTourismScraper:
    def __init__(self, credentials_path: str):
        self.credentials = self.load_credentials(credentials_path)
        self.reddit = self.get_reddit_client()
        self.mongo_collection = self.connect_mongo()
        
        # 10 touristic cities in Morocco
        # self.cities = [
        #     "Marrakech", "Fès", "Casablanca", "Rabat", "Agadir",
        #     "Chefchaouen", "Essaouira", "Ouarzazate", "Tanger", "Meknès"
        # ]

    #     self.cities = [
    #         "Imlil",
    # "Aït Ben Haddou",
    # "Tizi n’Oucheg",
    # "Tameslouht",
    # "Asni",
    # "Merzouga",
    # "M’Hamid El Ghizlane",
    # "Tamegroute",
    # "Ksar El Khorbat",
    # "Taghazout",
    # "Mirleft",
    # "Sidi Kaouki",
    # "Moulay Idriss Zerhoun",
    # "Chefchaouen",
    # "Ouirgane",
    # "Imsouane",
    # "Tafraoute",
    # "Tamnougalt",
    # "Skoura",
    # "Aguergour",
    # "Douar Samra",
    # "Aremd",
    # "Bou Tharar",
    # "Taddart",
    # "Tidli",
    # "Imilchil",
    # "Tinmel",
    # "Tizourgane",
    # "Akchour",
    # "Bhalil"
    #     ]

        self.cities = [
            "Marrakech", "Fes", "Agadir",
            "Essaouira", "El Jadida","Marrakesh",
            "Kenitra","Ifrane","Al Hoceima","Nador","Saidia","Volubilis","Taroudant","Zagora","Errachidia"
        ]        
        
        # Search query templates
        self.query_templates = [
            "visit {}", 
            "travel to {}", 
            "{} tourism", 
            "things to do in {}", 
            "is {} safe for tourists", 
            "{} travel guide", 
            "{} backpacking", 
            "must see in {}", 
            "vacation in {}", 
            "{} hotel reviews"
        ]

    def load_credentials(self, path_to_file: str) -> Dict:
        """Load credentials from JSON file"""
        try:
            with open(path_to_file) as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Credentials file not found: {path_to_file}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in credentials file: {path_to_file}")
            raise

    def connect_mongo(self, db_name: str = 'tourismDBB') -> pymongo.collection.Collection:
        """Connect to MongoDB and return collection"""
        try:
            client = pymongo.MongoClient(self.credentials['mongo_connection_string'])
            db = client[db_name]
            # Test connection
            client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            return db['tourism']
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def get_reddit_client(self) -> praw.Reddit:
        """Initialize Reddit client"""
        try:
            reddit = praw.Reddit(
                client_id=self.credentials['reddit_client_id'],
                client_secret=self.credentials['reddit_client_secret'],
                user_agent=self.credentials['reddit_user_agent']
            )
            # Test connection
            reddit.user.me()
            logger.info("Successfully connected to Reddit API")
            return reddit
        except Exception as e:
            logger.error(f"Failed to connect to Reddit API: {e}")
            raise

    def extract_city_from_query(self, query: str) -> str:
        """Extract city name from search query"""
        for city in self.cities:
            if city.lower() in query.lower():
                return city
        return "Unknown"

    def extract_comments_as_posts(self, submission, query: str) -> List[Dict]:
        """Extract comments from a submission as individual posts"""
        try:
            submission.comments.replace_more(limit=0)
            comment_posts = []

            for comment in submission.comments.list():
                # Skip deleted/removed comments
                if comment.body in ['[deleted]', '[removed]']:
                    continue
                    
                comment_post = {
                    "_id": f"{submission.id}_{comment.id}",
                    "query": query,
                    "city": self.extract_city_from_query(query),
                    "is_comment": True,
                    "parent_post_id": submission.id,
                    "text": comment.body,
                    "score": comment.score,
                    "author": str(comment.author) if comment.author else "[deleted]",
                    "created_utc": datetime.fromtimestamp(comment.created_utc, tz=timezone.utc),
                    "subreddit": submission.subreddit.display_name,
                    "url": f"https://reddit.com{comment.permalink}",
                    "scraped_at": datetime.now(tz=timezone.utc)
                }
                comment_posts.append(comment_post)
            
            return comment_posts
        except Exception as e:
            logger.warning(f"Failed to extract comments from {submission.id}: {e}")
            return []

    def search_reddit_posts(self, query: str, limit: int = 100) -> List[Dict]:
        """Search Reddit for posts matching the query"""
        logger.info(f"🔎 Searching Reddit for: '{query}'")
        all_posts = []

        try:
            for submission in self.reddit.subreddit("all").search(query, sort="new", limit=limit):
                # Skip posts without content
                if not submission.title and not submission.selftext:
                    continue

                post = {
                    "_id": submission.id,
                    "query": query,
                    "city": self.extract_city_from_query(query),
                    "title": submission.title,
                    "text": submission.selftext,
                    "score": submission.score,
                    "author": str(submission.author) if submission.author else "[deleted]",
                    "url": submission.url,
                    "created_utc": datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
                    "num_comments": submission.num_comments,
                    "subreddit": submission.subreddit.display_name,
                    "is_comment": False,
                    "scraped_at": datetime.now(tz=timezone.utc)
                }

                all_posts.append(post)

                # Add comments as independent posts
                comment_posts = self.extract_comments_as_posts(submission, query)
                all_posts.extend(comment_posts)

                # Rate limiting - be respectful to Reddit's API
                time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error searching for '{query}': {e}")

        return all_posts

    def save_to_mongo(self, posts: List[Dict]) -> int:
        """Save posts to MongoDB with deduplication"""
        if not posts:
            return 0
            
        saved = 0
        try:
            for post in posts:
                if not self.mongo_collection.find_one({"_id": post["_id"]}):
                    self.mongo_collection.insert_one(post)
                    saved += 1
                    
            logger.info(f"✅ Saved {saved} new items to MongoDB")
            return saved
        except Exception as e:
            logger.error(f"Error saving to MongoDB: {e}")
            return 0

    def run_scraper(self, posts_per_query: int = 100):
        """Main scraping function"""
        total_saved = 0
        
        for city in self.cities:
            logger.info(f"📍 Processing city: {city}")
            
            for template in self.query_templates:
                query = template.format(city)
                
                try:
                    posts = self.search_reddit_posts(query, limit=posts_per_query)
                    saved = self.save_to_mongo(posts)
                    total_saved += saved
                    
                    # Rate limiting between queries
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing query '{query}': {e}")
                    continue
        
        logger.info(f"🎉 Scraping completed! Total items saved: {total_saved}")
        return total_saved

    def get_collection_stats(self) -> Dict:
        """Get statistics about the scraped data"""
        try:
            total_posts = self.mongo_collection.count_documents({"is_comment": False})
            total_comments = self.mongo_collection.count_documents({"is_comment": True})
            
            # City distribution
            city_pipeline = [
                {"$group": {"_id": "$city", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            city_stats = list(self.mongo_collection.aggregate(city_pipeline))
            
            # Subreddit distribution
            subreddit_pipeline = [
                {"$group": {"_id": "$subreddit", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            subreddit_stats = list(self.mongo_collection.aggregate(subreddit_pipeline))
            
            return {
                "total_posts": total_posts,
                "total_comments": total_comments,
                "total_items": total_posts + total_comments,
                "cities": city_stats,
                "top_subreddits": subreddit_stats
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}

# ---------- MAIN ----------
if __name__ == '__main__':
    try:
        scraper = RedditTourismScraper("credentials.json")
        scraper.run_scraper(posts_per_query=100)
        
        # Print statistics
        stats = scraper.get_collection_stats()
        if stats:
            print("\n📊 Collection Statistics:")
            print(f"Total Posts: {stats['total_posts']}")
            print(f"Total Comments: {stats['total_comments']}")
            print(f"Total Items: {stats['total_items']}")
            
            print("\n🏙️  Top Cities:")
            for city_stat in stats['cities'][:5]:
                print(f"  {city_stat['_id']}: {city_stat['count']} items")
                
            print("\n📱 Top Subreddits:")
            for sub_stat in stats['top_subreddits']:
                print(f"  r/{sub_stat['_id']}: {sub_stat['count']} items")
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        exit(1)