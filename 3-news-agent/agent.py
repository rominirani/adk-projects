from google.adk.agents import Agent
import requests
import feedparser
import logging
from bs4 import BeautifulSoup
    
# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_rss_feed(feed_url: str) -> list[str]:
    """
    Fetches an RSS feed and extracts the URLs of its items (entries).

    Args:
        feed_url: The URL of the RSS feed to process.

    Returns:
        A list of strings, where each string is the URL of an item
        found in the feed. Returns an empty list if fetching or
        parsing fails, or if the feed contains no items with links.
    """
    item_urls = []
    logging.info(f"Attempting to fetch and parse RSS feed: {feed_url}")

    try:
        # 1. Fetch the feed content with a timeout
        # Using a reasonable user-agent is good practice
        headers = {'User-Agent': 'My RSS URL Extractor Bot (Python)'}
        response = requests.get(feed_url, timeout=15, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        logging.info(f"Successfully fetched feed (Status code: {response.status_code}). Parsing...")

        # 2. Parse the feed content
        # Pass response.content (bytes) to feedparser to let it handle encoding
        feed = feedparser.parse(response.content)

        # Check for parsing errors (optional but recommended)
        if feed.bozo:
            logging.warning(f"Feed at {feed_url} might be ill-formed. "
                            f"Bozo reason: {getattr(feed, 'bozo_exception', 'Unknown')}")
            # Decide if you want to proceed despite potential errors
            # For this function, we'll try to extract links anyway.

        # 3. Extract the item URLs
        if feed.entries:
            logging.info(f"Found {len(feed.entries)} entries in the feed. Extracting links...")
            for entry in feed.entries:
                # Entries usually have a 'link' attribute
                link = entry.get('link')
                if link:
                    item_urls.append(link)
                else:
                    logging.debug(f"Entry found without a 'link' attribute: {entry.get('title', 'N/A')}")
            logging.info(f"Extracted {len(item_urls)} valid links.")
        else:
            logging.info("No entries found in the parsed feed.")

    except requests.exceptions.Timeout:
        logging.error(f"Timeout error when trying to fetch feed: {feed_url}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching feed {feed_url}: {e}")
    except Exception as e:
        # Catch other potential errors during parsing or processing
        logging.error(f"An unexpected error occurred processing feed {feed_url}: {e}", exc_info=True) # Log traceback

    return item_urls

def get_rss_feed_article(url: str) -> str:
    """
    Fetches the content of a given URL and extracts the visible text.

    Args:
        url: The URL of the web page to fetch and parse.

    Returns:
        A string containing the extracted text content of the page,
        or None if fetching or parsing fails or the content type is not HTML.
    """
    logging.info(f"Attempting to fetch content from URL: {url}")

    try:
        # 1. Fetch the page content
        # Use headers to mimic a browser request, which can help avoid blocks
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        response = requests.get(url, headers=headers, timeout=20) # Increased timeout for potentially larger pages
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        # 2. Check if the content type is HTML
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            logging.warning(f"Content type is not HTML ('{content_type}') for URL: {url}. Skipping text extraction.")
            return "" # Or return an empty string: ""

        logging.info(f"Successfully fetched HTML content from {url}. Parsing...")

        # 3. Parse the HTML content
        # Use 'lxml' if installed for speed, otherwise default to 'html.parser'
        try:
            soup = BeautifulSoup(response.text, 'lxml')
        except ImportError:
            soup = BeautifulSoup(response.text, 'html.parser')

        # 4. Extract text
        # Basic approach: get all text, stripping tags.
        # This will include navigation, footers, ads text, etc.
        # It also strips script and style tag content by default with get_text().
        text = soup.get_text(separator=' ', strip=True)

        # Optional: More advanced cleaning (can be basic or complex)
        # - Remove excessive whitespace/newlines
        text = ' '.join(text.split())


        # --- Note on Better Extraction ---
        # For cleaner *article* text extraction (like a reader mode), libraries like
        # 'readability-lxml' or 'goose3' are generally much better than basic get_text().
        # Example with readability-lxml (requires 'pip install readability-lxml'):
        # from readability import Document
        # doc = Document(response.text)
        # title = doc.title()
        # text = BeautifulSoup(doc.summary(), 'lxml').get_text(separator=' ', strip=True)
        # --- End Note ---

        logging.info(f"Successfully extracted text content (length: {len(text)}) from {url}.")
        return text

    except requests.exceptions.Timeout:
        logging.error(f"Timeout error when trying to fetch URL: {url}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return None
    except Exception as e:
        # Catch potential errors during parsing or text extraction
        logging.error(f"An unexpected error occurred processing URL {url}: {e}", exc_info=True)
        return None

root_agent = Agent(
    name="rss_feed_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent that summarizes the news items from a RSS Feed."
    ),
    instruction=(
        "You are a helpful agent who fetches the links from a RSS Feed and summarizes them for the user. You will first get all the links for the rss feed provided by the user. Then you will extract the contents for each feed as text and summarize it. Then you will present a well formatted list of items with the title and the summary for each item."
    ),
    tools=[get_rss_feed, get_rss_feed_article],
)