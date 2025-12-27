from telethon import TelegramClient as TelethonClient
from telethon.tl.functions.account import UpdateEmojiStatusRequest
from telethon.tl.types import EmojiStatus, User
from telethon.tl.functions.users import GetFullUserRequest
from datetime import datetime


class TelegramClient:
    def __init__(self, api_id: int, api_hash: str):
        self.client = TelethonClient(
            "session/status-emoji-api", api_id, api_hash)
        self.status_history = []

    async def start(self):
        await self.client.start()  # type: ignore

        initial_status = await self.get_current_emoji_status()
        if initial_status:
            self.status_history.append(initial_status)

    async def disconnect(self):
        await self.client.disconnect()  # type: ignore

    async def get_current_emoji_status(self):
        if not await self.client.is_user_authorized():
            raise Exception(
                "User is not authorized. Please complete authentication first")

        try:
            me = await self.client.get_me()
            if not isinstance(me, User):
                raise Exception("Failed to get user information")

            if hasattr(me, "emoji_status") and me.emoji_status:
                return me.emoji_status.to_dict()

            return None

        except Exception as e:
            raise Exception(f"Failed to get emoji status: {str(e)}")

    async def update_emoji_status(self, document_id: int, until: datetime | None = None):
        if not await self.client.is_user_authorized():
            raise Exception(
                "User is not authorized. Please complete authentication first")

        try:
            # Create an EmojiStatus object with the provided emoji
            emoji_status = EmojiStatus(document_id, until)

            # Store current status before updating
            current_status = await self.get_current_emoji_status()
            if current_status:
                self.status_history.append(current_status)

            # Update the emoji status
            result = await self.client(UpdateEmojiStatusRequest(
                emoji_status=emoji_status
            ))

            if not result:
                # Remove the stored status if update failed
                if self.status_history:
                    self.status_history.pop()
                raise Exception(
                    "Failed to update emoji status: No response from Telegram")

            return True
        except ValueError as e:
            raise Exception(f"Invalid emoji ID format: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to update emoji status: {str(e)}")

    async def undo_emoji_status(self) -> dict:
        if len(self.status_history) < 1:
            raise Exception("No previous emoji status available to restore")

        # Get the previous status
        previous_status = self.status_history.pop()

        try:
            # Create emoji status object from previous status
            emoji_status = EmojiStatus(
                previous_status['document_id'], previous_status['until'])

            # Update to previous status
            result = await self.client(UpdateEmojiStatusRequest(
                emoji_status
            ))

            if not result:
                # Put the status back in history if update failed
                self.status_history.append(previous_status)
                raise Exception("Failed to restore previous emoji status")

            return previous_status
        except Exception as e:
            # Put the status back in history if there was an error
            self.status_history.append(previous_status)
            raise Exception(
                f"Failed to restore previous emoji status: {str(e)}")
