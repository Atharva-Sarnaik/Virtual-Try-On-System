import os
import aiofiles
import replicate
import base64
import logging
from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Changed to DEBUG level for more details
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Virtual Try-On System")

# Set Replicate API token directly
os.environ["REPLICATE_API_TOKEN"] = "REPLICATE_API_TOKEN"
client = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])

# Create directories if they don't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Configure static files
app.mount("/static", StaticFiles(directory="static"), name="static")

async def save_upload_file(upload_file: UploadFile) -> Path:
    """Save an uploaded file to disk and return its path."""
    try:
        file_path = UPLOAD_DIR / upload_file.filename
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await upload_file.read()
            await out_file.write(content)
        logger.debug(f"Successfully saved file to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving file {upload_file.filename}: {e}")
        raise

async def cleanup_file(file_path: Path):
    """Remove a temporary file."""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            logger.debug(f"Successfully cleaned up file {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up file {file_path}: {e}")

def encode_image_to_base64(image_path):
    """Convert image file to base64 string."""
    try:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            logger.debug(f"Successfully encoded image {image_path}")
            return encoded
    except Exception as e:
        logger.error(f"Error encoding image {image_path}: {e}")
        raise

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page with upload form."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/tryon")
async def try_on(
    person_img: UploadFile = File(...),
    cloth_img: UploadFile = File(...)
):
    """
    Process virtual try-on request using Replicate's IDM-VTON model.
    """
    person_path = None
    cloth_path = None

    try:
        # Log incoming request
        logger.info(f"Processing try-on request with images: {person_img.filename}, {cloth_img.filename}")
        logger.debug(f"Content types - Person: {person_img.content_type}, Cloth: {cloth_img.content_type}")
        
        # Validate file types
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if person_img.content_type not in allowed_types:
            return {"status": "error", "message": "Person image must be JPEG, PNG, or WebP format"}
        if cloth_img.content_type not in allowed_types:
            return {"status": "error", "message": "Clothing image must be JPEG, PNG, or WebP format"}

        # Save uploaded files temporarily
        person_path = await save_upload_file(person_img)
        cloth_path = await save_upload_file(cloth_img)
        logger.info(f"Saved uploaded files: {person_path}, {cloth_path}")

        try:
            # Convert images to base64
            person_base64 = encode_image_to_base64(person_path)
            cloth_base64 = encode_image_to_base64(cloth_path)
            logger.debug("Successfully converted images to base64")

            # Add data URI prefix
            person_data_uri = f"data:image/jpeg;base64,{person_base64}"
            cloth_data_uri = f"data:image/jpeg;base64,{cloth_base64}"

            # Run the model with base64 encoded images
            logger.info("Calling Replicate API...")
            
            # Create prediction
            prediction = client.run(
                "cuuupid/idm-vton:0513734a452173b8173e907e3a59d19a36266e55b48528559432bd21c7d7e985",
                input={
                    "crop": False,
                    "seed": 42,
                    "steps": 30,
                    "category": "upper_body",
                    "force_dc": False,
                    "garm_img": cloth_data_uri,
                    "human_img": person_data_uri,
                    "mask_only": False,
                    "garment_des": "clothing item"
                }
            )
            
            # Add detailed logging of the response
            logger.info(f"Raw API response type: {type(prediction)}")
            logger.info(f"Raw API response: {prediction}")
            
            if prediction is None:
                raise Exception("No response from Replicate API")

            # Handle different response formats
            if isinstance(prediction, str):
                logger.info("Received string response (direct URL)")
                return {"status": "success", "result_url": prediction}
            elif isinstance(prediction, list):
                logger.info(f"Received list response with {len(prediction)} items")
                if len(prediction) > 0:
                    return {"status": "success", "result_url": prediction[0]}
                else:
                    raise Exception("Empty list response from model")
            elif isinstance(prediction, dict):
                logger.info(f"Received dictionary response with keys: {list(prediction.keys())}")
                # Try different possible keys that might contain the URL
                for key in ['output', 'url', 'image', 'result']:
                    if key in prediction:
                        logger.info(f"Found URL in dictionary key: {key}")
                        return {"status": "success", "result_url": prediction[key]}
                logger.error(f"Dictionary response missing expected keys. Available keys: {list(prediction.keys())}")
                raise Exception("Dictionary response missing expected URL key")
            elif hasattr(prediction, 'url'):  # Handle FileOutput type
                logger.info("Received FileOutput response")
                return {"status": "success", "result_url": prediction.url}
            else:
                logger.error(f"Unexpected response type: {type(prediction)}")
                raise Exception(f"Invalid response format from model: {type(prediction)}")
            
        except replicate.exceptions.ReplicateError as e:
            logger.error(f"Replicate API error: {str(e)}")
            return {"status": "error", "message": f"Replicate API error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error during model prediction: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            # Cleanup temporary files
            if person_path:
                await cleanup_file(person_path)
            if cloth_path:
                await cleanup_file(cloth_path)
            logger.info("Cleaned up temporary files")

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        # Ensure cleanup in case of errors
        if person_path:
            await cleanup_file(person_path)
        if cloth_path:
            await cleanup_file(cloth_path)
        return {"status": "error", "message": f"Error processing request: {str(e)}"}

@app.get("/demo")
async def demo():
    """Demo endpoint using example images."""
    try:
        logger.info("Starting demo endpoint")
        
        # Create prediction using example images
        logger.info("Calling Replicate API...")
        prediction = client.run(
            "cuuupid/idm-vton:0513734a452173b8173e907e3a59d19a36266e55b48528559432bd21c7d7e985",
            input={
                "crop": False,
                "seed": 42,
                "steps": 30,
                "category": "upper_body",
                "force_dc": False,
                "garm_img": "https://replicate.delivery/pbxt/KgwTlZyFx5aUU3gc5gMiKuD5nNPTgliMlLUWx160G4z99YjO/sweater.webp",
                "human_img": "https://replicate.delivery/pbxt/KgwTlhCMvDagRrcVzZJbuozNJ8esPqiNAIJS3eMgHrYuHmW4/KakaoTalk_Photo_2024-04-04-21-44-45.png",
                "mask_only": False,
                "garment_des": "cute pink top"
            }
        )
        
        # Detailed logging of the response
        logger.info(f"Received response from Replicate API")
        logger.info(f"Response type: {type(prediction)}")
        logger.info(f"Response content: {prediction}")
        
        if prediction is None:
            logger.error("Received None response from API")
            raise Exception("No response from Replicate API")

        # Try to extract the URL from various possible response formats
        result_url = None
        
        if isinstance(prediction, str):
            logger.info("Response is a string (direct URL)")
            result_url = prediction
        elif isinstance(prediction, list):
            logger.info(f"Response is a list with {len(prediction)} items")
            if len(prediction) > 0:
                result_url = prediction[0]
            else:
                logger.error("Received empty list from API")
                raise Exception("Empty list response from model")
        elif isinstance(prediction, dict):
            logger.info("Response is a dictionary")
            # Try different possible keys that might contain the URL
            for key in ['output', 'url', 'image', 'result']:
                if key in prediction:
                    result_url = prediction[key]
                    logger.info(f"Found URL in dictionary key: {key}")
                    break
            if result_url is None:
                logger.error(f"Dictionary response missing expected keys. Available keys: {list(prediction.keys())}")
                raise Exception("Dictionary response missing expected URL key")
        else:
            logger.error(f"Unexpected response type: {type(prediction)}")
            raise Exception(f"Invalid response format from model: {type(prediction)}")

        if not result_url:
            logger.error("Failed to extract URL from response")
            raise Exception("Could not extract result URL from response")

        logger.info(f"Successfully extracted result URL: {result_url}")
        return {"status": "success", "result_url": result_url}

    except Exception as e:
        logger.error(f"Error in demo: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 