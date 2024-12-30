"""
Client for sending macOS notifications using osascript.
"""
import subprocess
from typing import Literal

class NotificationClient:
    @staticmethod
    def notify(
        message: str,
        title: str = "AI System",
        subtitle: str = "",
        sound: bool = True,
        style: Literal["alert", "banner"] = "banner"
    ) -> None:
        """
        Send a macOS notification using osascript.
        
        Args:
            message: The notification message
            title: The notification title
            subtitle: Optional subtitle
            sound: Whether to play the default notification sound
            style: "alert" for modal dialog or "banner" for notification center
        """
        if style == "alert":
            script = f'display alert "{title}"'
            if message:
                script += f' message "{message}"'
            if subtitle:
                script += f' as critical'
        else:
            script = f'display notification "{message}" with title "{title}"'
            if subtitle:
                script += f' subtitle "{subtitle}"'
            if sound:
                script += ' sound name "default"'
        
        subprocess.run(["osascript", "-e", script], check=True) 