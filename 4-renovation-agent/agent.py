import os
from google.adk.agents import Agent
from google.genai import types
import warnings
from google.cloud import storage
import logging
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

warnings.filterwarnings("ignore")
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
STORAGE_BUCKET = os.environ["STORAGE_BUCKET"]
GOOGLE_CLOUD_PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
GOOGLE_CLOUD_LOCATION = os.environ["GOOGLE_CLOUD_LOCATION"]
GOOGLE_GENAI_USE_VERTEXAI=os.environ["GOOGLE_GENAI_USE_VERTEXAI"]
STAGING_BUCKET = "gs://" + STORAGE_BUCKET
ROOT_AGENT_NAME = "adk_renovation_agent"
PROJECT_ID = GOOGLE_CLOUD_PROJECT
staging_bucket = STAGING_BUCKET
logger = logging.getLogger(__name__)

PROPOSAL_DOCUMENT_FILE_NAME =  "proposal_document_for_user.pdf"
MODEL_NAME = "gemini-2.5-pro-preview-03-25"

'''
Tools Definition Starts:
'''

def store_pdf(pdf_text: str) -> str:
    """Writes text to a PDF file, then uploads it to Google Cloud Storage.
    Args:
        text: The text to write to the PDF.
        bucket_name: The name of the GCS bucket.
        file_name: The name to give the PDF file in the bucket.
    """
    try:
        # Use reportlab to create a PDF from the text, as pdfplumber is better for reading PDFs

        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        textobject = c.beginText()
        textobject.setTextOrigin(10, 730)  # Adjust coordinates as needed
        textobject.setFont("Helvetica", 12)

        # Add the text, line by line, to the PDF
        for line in pdf_text.splitlines():
            textobject.textLine(line)

        c.drawText(textobject)
        c.save()

        pdf_buffer.seek(0)  # Reset buffer to start

        # Upload the PDF to GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(STORAGE_BUCKET)
        blob = bucket.blob(PROPOSAL_DOCUMENT_FILE_NAME)

        blob.upload_from_file(pdf_buffer, content_type="application/pdf")

        logger.info(f"Successfully uploaded PDF to gs://{STORAGE_BUCKET}/{PROPOSAL_DOCUMENT_FILE_NAME}")

    except Exception as e:
        logger.error(f"Error writing text to PDF and uploading: {e}")
        raise
    finally:
        if 'pdf_buffer' in locals():
            pdf_buffer.close() #Close the buffer
    return "Successfully uploaded PDF to GCS!!"


'''
Tools Definition Ends
'''

sample_proposal = """
*****************************Sample Proposal Document Template***********
PROPOSAL DOCUMENT 
This proposal is made and entered into this 16th day of March, 2025, by and between:
Homeowner: Alice Smith, residing at 123 Main Street, Anytown, CA 91234
Contractor: Bob's Renovations, Inc., a California corporation, with its principal place of
business at 456 Oak Avenue, Anytown, CA 91235 (License #1234567)
1. Scope of Work:
Contractor agrees to perform the following work:
Kitchen Remodel
Demolition of existing kitchen cabinets, countertops, and flooring.
Installation of new custom cabinets (specified in Exhibit A – Cabinet Design).
Installation of granite countertops (specified in Exhibit B – Countertop Selection).
Installation of tile backsplash (specified in Exhibit C – Backsplash Tile).
Installation of new stainless steel sink and faucet.
Installation of new recessed lighting (6 fixtures).
Installation of new flooring (specified in Exhibit D – Flooring Selection).
Painting of walls and ceiling (2 coats, color specified in Exhibit E – Paint Color).
Plumbing work necessary for sink and dishwasher connections.
Electrical work necessary for lighting and appliance connections (GFCI outlets).
All work will be performed in a professional and workmanlike manner in accordance with local
building codes.
2. Proposal Price:
The total contract price for the work described above is $30,000.00 (Thirty Thousand Dollars).
3. Payment Schedule:
Deposit: $10,000.00 due upon signing of this proposal.

Phase 1 (Demolition & Rough-in): $5,000.00 due upon completion of demolition and
rough-in plumbing and electrical.
Phase 2 (Cabinet & Countertop Installation): $10,000.00 due upon completion of cabinet
and countertop installation.
Final Payment: $5,000.00 due upon final inspection and completion of all work.
4. Change Orders:
Any changes to the scope of work must be agreed upon in writing and signed by both parties.
Changes may result in adjustments to the contract price and schedule. 
5. Timeline:
The work shall commence on May 22, 2025, and be substantially completed within 6 weeks.
This timeline is subject to change due to unforeseen circumstances (e.g., material delays,
weather).

6. Permits:
Contractor is responsible for obtaining all necessary permits for the work.
7. Insurance:
Contractor shall maintain general liability insurance and workers' compensation insurance. Proof
of insurance will be provided upon request.
8. Warranty:
Contractor warrants all labor for a period of one (1) year from the date of completion.
Manufacturer warranties apply to materials.
9. Dispute Resolution:
Any disputes arising out of this contract shall be resolved through mediation. If mediation fails,
the parties agree to binding arbitration.
10. Termination:
This proposal may be terminated by either party with written notice if the other party breaches
the proposal.
11. Entire Agreement:
This proposal constitutes the entire agreement between the parties and supersedes all prior
discussions and agreements.
IN WITNESS WHEREOF, the parties have executed this contract as of the date first written
above.

____________Alice Smith________________
Alice Smith (Homeowner)
_____________Bob_______________
Bob Johnson (Contractor, Bob's Renovations, Inc.)
Exhibits:
Exhibit A: Cabinet Design (detailed drawings, specifications)

Image of the design goes here.

I. Overall Style and Design
Style: Modern, European-style, minimalist.
Layout: Wall cabinets, base cabinets, and a tall pantry-style cabinet. An island is visible but not
fully detailed in the image.
Color Palette: Primarily white cabinets with a dark countertop. Walls are a neutral grey/beige.
II. Cabinet Construction Specifications
Cabinet Type: Frameless (European-style). This means the doors and drawers attach directly to
the cabinet boxes, without a face frame.
Box Material: Likely constructed from particleboard or MDF (Medium-Density Fiberboard). The
interior finish is not visible.
Door and Drawer Front Material: High-gloss white finish. Likely acrylic, laminate, or a high-gloss
lacquer applied to an MDF core.
Edge Banding: Color-matched to the door/drawer front, likely a thin PVC or ABS edge banding.
Hardware:
Pulls: Long, horizontal, stainless steel or brushed nickel finish pulls. Appear to be mounted on
the center of the drawers and doors.
Hinges: Concealed, European-style hinges (soft-close likely).
Drawer Slides: Full-extension, soft-close drawer slides.
Toe Kick: Recessed, likely white to match cabinets.
III. Cabinet Dimensions (Estimated).

Wall Cabinet Height: Appears to be close to ceiling height, perhaps 30-36" high depending on
ceiling height.
Wall Cabinet Depth: Standard depth, likely 12-14".
Base Cabinet Height: Standard counter height, approximately 36" including countertop.
Base Cabinet Depth: Standard depth, approximately 24".
Pantry Cabinet Height: Floor to ceiling.
Pantry Cabinet Depth: Likely 24".
IV. Cabinet Breakdown
Wall Cabinets:
Several cabinets above the countertop, configured to fit the available space.
The cabinet directly above the cooktop is likely shallower to accommodate the range hood.
Under-cabinet lighting is present (LED strip lights).
Base Cabinets:
One cabinet to the left of the tall cabinet.
Multiple drawers, including one directly under the cooktop.
A cabinet at the very end of the counter next to the right wall.
Tall Cabinet:
Full-height pantry-style cabinet.
Two doors, one above the other.
Island:
Dark countertop matching the perimeter countertops.
Cabinets on the visible side are white.

V. Countertop Specifications
Material: Dark solid surface or stone countertop. Could be quartz, granite, or a similar
engineered stone.
Edge Profile: Slightly eased edge, possibly a small radius.
Thickness: Likely 1 1/4" (3cm).
VI. Appliance Considerations
Cooktop: Integrated, flat, black cooktop (likely induction or electric).
Range Hood: Stainless steel, integrated into the wall cabinets.
Outlets: Outlets are present on the back splash.
VII. Additional Details
Backsplash: Rectangular tile with a horizontal orientation, likely ceramic or glass, in a light color
with some variation.
Lighting: Recessed ceiling lights and under-cabinet lighting.
   *************************************************************************

   """

root_agent_system_instruction = """
    You are a proposal , permits and ordering agent for executing and managing the kitchen renovation proposal for a home owner. 
    You are tasked with:

    1. Creating Proposal Document if the user doesn't have one already.
    2. Creating permits and compliance documentation.
    3. Creating a material list for ordering along with quality control checklists.
    4. Placing orders and tracking the status of materials delivery.

    Here's how you should operate:

    - First, greet the user and ask them what they need help with. Provide a brief overview of your capabilities.
    - Clarify the user's intent. If the user is unclear, ask clarifying questions.
    - The user will ask you to create a proposal document or will directly provide the proposal document. 
    - If the user provides the proposal document, using the corresponding subagent you will be able to extract the doc and its content.
    - If the user asks you to create a proposal document then you need to go to the corresponding sub-agent to create proposal document.
    - Based on the user's intent, determine which sub-agent is best suited to handle the request.
    - Then follow the instructions below. Ultimately your goal is to route the user's request to the appropriate sub-agent and 
      ensure that the task is completed successfully.
    """



'''
# Proposal Agent Definition
'''
root_agent = Agent(
   model=MODEL_NAME,
   name="proposal_agent",
   description="Agent that creates the kitchen renovation proposal pdf for the customer based on a few details that the user provides about the renovation request.",
   instruction= f"""
   You are a home renovation proposal document  generator agent that helps with creating 
   the renovation proposal document with the following details from the user:
   1) the necessary renovation requirement from the user
   2) preference for contractor location (optional)
   3) budget constraints (optional)
   Do not ask any other questions to the user. Use the infomration in the template for filling details taht you don't know.
   After clarifiying the user's intent on the options, generate the PDF file content for the renovation proposal. 
   Then upload the content as a pdf file in a Cloud Storage Bucket using the tool "store_pdf"  
   Once the proposal document pdf content is created and uploaded in the Cloud Storage Bucket,
   confirm to the user that the proposal document has been created and uploaded to the Cloud Storage Bucket defined.
   Here is a sample content for the proposal document, use this as a reference and create the one 
   that matches the user requirements : {sample_proposal}
   """,
   generate_content_config=types.GenerateContentConfig(temperature=0.2),
   tools=[store_pdf],
)