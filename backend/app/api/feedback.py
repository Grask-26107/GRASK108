import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import FeedbackRequest, FeedbackResponse
from app.core.database import log_feedback

router = APIRouter(prefix="/feedback", tags=["Feedback & Telemetry"])


@router.post("", response_model=FeedbackResponse)
def submit_feedback(feedback: FeedbackRequest):
    """
    Captures user ratings (thumbs up/down) and comments on AI responses to
    power the accuracy improvement loop for government audit oversight.
    """
    try:
        feedback_id = f"FB-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
        log_feedback(
            feedback_id=feedback_id,
            query_id=feedback.query_id,
            rating=feedback.rating.value,
            query_text=feedback.query_text,
            response_text=feedback.response_text,
            mode=feedback.mode,
            comments=feedback.comments
        )
        return FeedbackResponse(
            status="SUCCESS",
            feedback_id=feedback_id,
            recorded_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record feedback: {str(e)}"
        )
