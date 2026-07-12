from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class MediaItem(BaseModel):
    id: str
    title: str
    creator: str
    publisher: Optional[str] = "Inconnu"
    year: Optional[str] = "N/A"
    rating: Optional[float] = 0.0
    rating_count: Optional[int] = 0
    rating_source: Optional[str] = ""
    cover_url: Optional[str] = ""
    description: Optional[str] = ""
    genres: List[str] = []
    media_type: str = "books" # "books", "movies", "games"

class ExploreResponse(BaseModel):
    items: List[MediaItem]
    total: int
    media_type: str
    query: Optional[str] = None
    genre: Optional[str] = None

class RecommendationExplanation(BaseModel):
    score: float
    reasons: List[str]
    stats: Dict[str, Any]

class MediaDetailResponse(BaseModel):
    media: MediaItem
    why_recommended: Optional[str] = None
    explanation: Optional[RecommendationExplanation] = None
    similars: List[MediaItem] = []

class FeedbackRequest(BaseModel):
    media_id: str
    media_type: str
    feedback_type: str = Field(..., description="Must be 'like' or 'dislike'")

class FeedbackResponse(BaseModel):
    status: str
    message: str

class ChatRequest(BaseModel):
    question: str
    chat_history: Optional[List[Dict[str, str]]] = None
    lang: Optional[str] = "fr"
    provider: Optional[str] = "nvidia"

class ChatResponse(BaseModel):
    response: str
    type: str = "text" # "text" or "image"
    image_bytes_b64: Optional[str] = None

class PublicConfigResponse(BaseModel):
    status: str
    version: str
    providers: Dict[str, bool]
