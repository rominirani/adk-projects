# Import necessary libraries for agent creation, web requests, feed parsing, and HTML parsing.
import logging
import os


from google.adk.agents import Agent
from google.cloud import storage
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

def write_text_to_pdf_to_gcs(text_content: str) -> str:
    """
    Writes text content to a PDF file and uploads it to a Google Cloud Storage bucket.

    Args:
        text_content: The string content to write into the PDF.

    Returns:
        The GCS URI of the uploaded PDF file, or None if an error occurs.
    """

    bucket_name = os.environ.get('GOOGLE_CLOUD_STORAGE_BUCKET', 'news-feed-pdfs')
    news_feed_pdf_file = os.environ.get('NEWS_FEED_PDF_FILE', 'latest-news.pdf')

    # Log the attempt to write the PDF to GCS.
    logging.info(f"Attempting to write PDF to GCS bucket '{bucket_name}' as '{news_feed_pdf_file}'")

    # Create a PDF in memory
    try:
        # Use BytesIO to handle the PDF content in memory.
        from io import BytesIO
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Add text to the PDF
        # Need to handle text wrapping and pagination for long text
        # This is a basic implementation; for production, consider more robust text flow
        # Begin a new text object at the specified coordinates.
        textobject = c.beginText(40, 750) # Start position
        textobject.setFont("Times-Roman", 12)

        # Simple line splitting (doesn't handle words splitting across lines)
        lines = text_content.split('\n')
        # Iterate over each line of the text content.
        for line in lines:
            # Basic wrapping: split line if it's too long (approximate)
            while len(line) > 80: # Approximate character limit per line
                split_point = line[:80].rfind(' ') # Find last space before limit
                if split_point == -1: # No space found, force split
                    split_point = 80
                textobject.textLine(line[:split_point])
                # Update the line to the remaining part.
                line = line[split_point:].lstrip() # Remove leading space from next line
            textobject.textLine(line)

        # Draw the text object onto the canvas.
        c.drawText(textobject)
        # Save the PDF to the buffer.
        c.save()

        # Get the PDF content from the buffer
        buffer.seek(0)
        pdf_content = buffer.getvalue()
        buffer.close()
        # Log successful creation of PDF content.
        logging.info("PDF content created successfully.")
    except Exception as e:
        # Log an error if PDF creation fails.
        logging.error(f"Error creating PDF content: {e}", exc_info=True)
        return None
    # Upload the PDF to Google Cloud Storage
    try:
        # Initialize the Google Cloud Storage client.
        storage_client = storage.Client()
        # Get the target bucket.
        bucket = storage_client.bucket(bucket_name)
        # Create a new blob (file) in the bucket.
        blob = bucket.blob(news_feed_pdf_file)
        # Upload the PDF content from the string.
        blob.upload_from_string(pdf_content, content_type='application/pdf')
        # Construct the GCS URI of the uploaded PDF.
        pdf_uri = f"gs://{bucket_name}/{news_feed_pdf_file}"
        # Log the successful upload to GCS.
        logging.info(f"PDF successfully uploaded to GCS: {pdf_uri}")
        return pdf_uri
    except Exception as e:
        logging.error(f"Error uploading PDF to GCS: {e}", exc_info=True)
        return None

root_agent = Agent(
    name="travel_planner_pdf_agent",
    model="gemini-2.0-flash",
    instruction=(
        """
        You are a helpful agent who assist users with their travel planning. 
        Help them plan their trips, find travel information, and provide recommendations.
        If there is no more information needed, you can write the trip planning details to a PDF file.
        Use the `write_text_to_pdf_to_gcs` tool to write the trip planning details to a PDF file.
        """
    ),
    tools=[write_text_to_pdf_to_gcs],
)
