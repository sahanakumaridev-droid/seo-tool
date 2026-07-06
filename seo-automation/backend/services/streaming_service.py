"""
streaming_service.py — Server-Sent Events (SSE) for real-time updates
Enables live job progress, notifications, and streaming LLM responses
"""
import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Callable
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class StreamingService:
    """Manages Server-Sent Events for real-time updates."""
    
    def __init__(self):
        self.subscribers: Dict[str, list] = {}
    
    async def subscribe(self, channel: str) -> AsyncGenerator[str, None]:
        """Subscribe to a channel and receive updates."""
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        
        queue: asyncio.Queue = asyncio.Queue()
        self.subscribers[channel].append(queue)
        
        try:
            while True:
                message = await queue.get()
                yield f"data: {json.dumps(message)}\n\n"
        except asyncio.CancelledError:
            self.subscribers[channel].remove(queue)
            raise
    
    async def publish(self, channel: str, data: Dict[str, Any]) -> None:
        """Publish a message to all subscribers on a channel."""
        if channel not in self.subscribers:
            return
        
        message = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        }
        
        for queue in self.subscribers[channel]:
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                logger.warning(f"Queue full for channel {channel}")
    
    async def stream_job_progress(
        self,
        job_id: str,
        items: list,
        task_fn: Callable,
        concurrency: int = 3
    ) -> AsyncGenerator[str, None]:
        """Stream job progress in real-time."""
        total = len(items)
        completed = 0
        failed = 0
        results = []
        
        # Yield initial status
        yield f"data: {json.dumps({'status': 'started', 'total': total})}\n\n"
        
        # Process items with concurrency control
        semaphore = asyncio.Semaphore(concurrency)
        
        async def process_item(item):
            nonlocal completed, failed
            async with semaphore:
                try:
                    result = await task_fn(item)
                    completed += 1
                    return result, None
                except Exception as e:
                    failed += 1
                    logger.error(f"Task failed: {e}")
                    return None, str(e)
        
        # Run all tasks
        tasks = [process_item(item) for item in items]
        for task in asyncio.as_completed(tasks):
            result, error = await task
            if error:
                yield f"data: {json.dumps({
                    'status': 'error',
                    'completed': completed,
                    'failed': failed,
                    'error': error
                })}\n\n"
            else:
                yield f"data: {json.dumps({
                    'status': 'progress',
                    'completed': completed,
                    'total': total,
                    'percentage': int((completed / total) * 100),
                    'result': result
                })}\n\n"
                results.append(result)
        
        # Yield final status
        yield f"data: {json.dumps({
            'status': 'completed',
            'total': total,
            'completed': completed,
            'failed': failed,
            'results': results
        })}\n\n"
    
    async def stream_llm_response(
        self,
        prompt: str,
        model_fn: Callable,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream LLM response token by token."""
        try:
            async for chunk in model_fn(prompt, stream=True, **kwargs):
                if chunk:
                    yield f"data: {json.dumps({'token': chunk})}\n\n"
        except Exception as e:
            logger.error(f"LLM streaming failed: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"


# Singleton instance
streaming_service = StreamingService()


async def get_streaming_service() -> StreamingService:
    """Dependency injection for streaming service."""
    return streaming_service
