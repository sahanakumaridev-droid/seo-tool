from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api", tags=["site"])


class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok", "message": "Zeorbit Python API is running"}


@router.post("/contact")
def create_contact(request: ContactRequest) -> dict:
    # Placeholder: wire this to DB/email provider in next phase.
    return {
        "status": "received",
        "lead": {
            "name": request.name,
            "email": request.email,
        },
    }
