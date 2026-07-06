"""
streaming.py — Server-Sent Events endpoints for real-time updates
Enables live job progress, notifications, and streaming LLM responses
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from services.streaming_service import get_streaming_service, StreamingService
from services.advanced_ai_service import get_advanced_ai_service, AdvancedAIService
from auth import get_current_active_user, User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/job/{job_id}/progress")
async def stream_job_progress(
    job_id: str,
    current_user: User = Depends(get_current_active_user),
    streaming_service: StreamingService = Depends(get_streaming_service)
):
    """Stream job progress in real-time using Server-Sent Events."""
    
    async def event_generator():
        async for event in streaming_service.subscribe(f"job:{job_id}"):
            yield event
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/generate/stream")
async def stream_content_generation(
    prompt: str,
    model: str = "gpt-4",
    current_user: User = Depends(get_current_active_user),
    ai_service: AdvancedAIService = Depends(get_advanced_ai_service)
):
    """Stream AI-generated content token by token."""
    
    async def event_generator():
        try:
            async for chunk in ai_service.generate_content_with_streaming(
                prompt,
                model=model,
                max_tokens=2000
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            yield f"data: Error: {str(e)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/notifications")
async def stream_notifications(
    current_user: User = Depends(get_current_active_user),
    streaming_service: StreamingService = Depends(get_streaming_service)
):
    """Stream real-time notifications for the current user."""
    
    async def event_generator():
        async for event in streaming_service.subscribe(f"user:{current_user.user_id}:notifications"):
            yield event
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )
