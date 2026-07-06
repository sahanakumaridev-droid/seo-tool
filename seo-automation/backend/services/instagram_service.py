"""
Instagram Auto-Posting Service
Uses Instagram Graph API for Business accounts
"""
import httpx
import os
from typing import Optional, Dict, Any
from config import settings

class InstagramService:
    """
    Instagram Business API integration for automatic posting.
    
    Requirements:
    1. Instagram Business Account (convert from personal in Instagram app)
    2. Facebook Page connected to Instagram Business account
    3. Facebook App with Instagram permissions
    4. Access Token with instagram_basic, instagram_content_publish permissions
    """
    
    def __init__(self):
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
        self.instagram_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
        self.base_url = "https://graph.facebook.com/v18.0"
        
    async def post_to_instagram(
        self,
        image_url: str,
        caption: str,
    ) -> Dict[str, Any]:
        """
        Post image with caption to Instagram Business account.
        
        Args:
            image_url: Public URL of the image (must be accessible)
            caption: Post caption with hashtags
            
        Returns:
            Dict with post_id and permalink
        """
        if not self.access_token or not self.instagram_account_id:
            raise ValueError(
                "Instagram credentials not configured. Please set:\n"
                "INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID in .env file"
            )
        
        try:
            # Step 1: Create media container
            container_response = await self._create_media_container(image_url, caption)
            container_id = container_response.get("id")
            
            if not container_id:
                raise Exception("Failed to create media container")
            
            # Step 2: Publish the container
            publish_response = await self._publish_media(container_id)
            post_id = publish_response.get("id")
            
            # Step 3: Get permalink
            permalink = await self._get_permalink(post_id)
            
            return {
                "success": True,
                "post_id": post_id,
                "permalink": permalink,
                "message": "Posted to Instagram successfully!"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to post to Instagram: {str(e)}"
            }
    
    async def _create_media_container(self, image_url: str, caption: str) -> Dict:
        """Create Instagram media container (Step 1)"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/{self.instagram_account_id}/media",
                params={
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": self.access_token,
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def _publish_media(self, container_id: str) -> Dict:
        """Publish the media container (Step 2)"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/{self.instagram_account_id}/media_publish",
                params={
                    "creation_id": container_id,
                    "access_token": self.access_token,
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def _get_permalink(self, post_id: str) -> str:
        """Get the permalink of the published post"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{post_id}",
                params={
                    "fields": "permalink",
                    "access_token": self.access_token,
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("permalink", "")
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get Instagram Business account information"""
        if not self.access_token or not self.instagram_account_id:
            return {
                "success": False,
                "error": "Instagram credentials not configured"
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{self.instagram_account_id}",
                    params={
                        "fields": "username,name,profile_picture_url,followers_count,follows_count,media_count",
                        "access_token": self.access_token,
                    }
                )
                response.raise_for_status()
                return {
                    "success": True,
                    "data": response.json()
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
instagram_service = InstagramService()
