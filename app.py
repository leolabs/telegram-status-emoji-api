import os
import asyncio
import sys
import signal
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from telegram_client import TelegramClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

security = HTTPBearer()
api_key = os.getenv("API_KEY")


def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    if not api_key:
        return  # No API key required if not set
    if credentials.credentials != api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )


app = FastAPI(title="Telegram Emoji Status Updater")
telegram_client = None


class EmojiUpdate(BaseModel):
    document_id: int
    until: datetime | None = None


@app.on_event("startup")
async def startup_event():
    global telegram_client
    api_id = os.getenv("TG_API_ID")
    api_hash = os.getenv("TG_API_HASH")

    if not all([api_id, api_hash]):
        raise Exception("Missing required environment variables")

    # Type checking to satisfy mypy
    if not isinstance(api_id, str) or not isinstance(api_hash, str):
        raise Exception("Environment variables must be strings")

    telegram_client = TelegramClient(int(api_id), api_hash)
    await telegram_client.start()

    # Shutdown after timeout to allow Docker restart
    timeout = int(os.getenv("SERVER_TIMEOUT", 86400))  # Default 24 hours

    async def shutdown_after_timeout():
        await asyncio.sleep(timeout)
        os.kill(os.getpid(), signal.SIGTERM)

    asyncio.create_task(shutdown_after_timeout())


@app.on_event("shutdown")
async def shutdown_event():
    if telegram_client:
        await telegram_client.disconnect()


@app.get("/current-emoji")
async def get_current_emoji(auth: None = Depends(verify_api_key)):
    """Get the current emoji status of the account."""
    if not telegram_client:
        raise HTTPException(
            status_code=500, detail="Telegram client not initialized")

    try:
        current_status = await telegram_client.get_current_emoji_status()
        return {
            "current_emoji": current_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update-emoji")
async def update_emoji(emoji_update: EmojiUpdate, auth: None = Depends(verify_api_key)):
    if not telegram_client:
        raise HTTPException(
            status_code=500, detail="Telegram client not initialized")

    try:
        await telegram_client.update_emoji_status(
            emoji_update.document_id,
            until=emoji_update.until
        )
        return {
            "status": "success",
            "message": f"Emoji status updated to ID: {emoji_update.document_id}",
            "expires_at": emoji_update.until.isoformat() if emoji_update.until else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/undo-emoji")
async def undo_emoji(auth: None = Depends(verify_api_key)):
    """Undo the last emoji status change."""
    if not telegram_client:
        raise HTTPException(
            status_code=500, detail="Telegram client not initialized")

    try:
        previous_status = await telegram_client.undo_emoji_status()
        return {
            "status": "success",
            "message": "Emoji status reverted to previous state",
            "previous_status": previous_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
