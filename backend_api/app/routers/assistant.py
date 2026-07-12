import os
import sys
import base64
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.media import ChatRequest, ChatResponse
from app.dependencies import get_agent

# Add app_build to path if not present
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_BUILD_DIR = os.path.join(BASE_DIR, "app_build")
if APP_BUILD_DIR not in sys.path:
    sys.path.insert(0, APP_BUILD_DIR)

router = APIRouter(prefix="/api")

@router.post("/assistant/chat", response_model=ChatResponse)
def assistant_chat(
    req: ChatRequest,
    agent=Depends(get_agent)
):
    try:
        # Call the existing BookLensAgent
        response = agent.answer(
            question=req.question,
            chat_history=req.chat_history,
            lang=req.lang,
            provider=req.provider
        )
        
        # Check if response is a dict (e.g. image generation from Flux)
        if isinstance(response, dict) and response.get("type") == "image":
            img_bytes = response.get("image_bytes")
            b64_str = base64.b64encode(img_bytes).decode("utf-8") if img_bytes else None
            return ChatResponse(
                response=response.get("content", ""),
                type="image",
                image_bytes_b64=b64_str
            )
            
        return ChatResponse(
            response=str(response),
            type="text"
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
