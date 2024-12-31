#!/usr/bin/env python3
"""
Tool for sending system notifications
"""
import os
import time
import logging
from typing import Dict, Any
import subprocess

logger = logging.getLogger(__name__)

def send_notification(
    message: str,
    title: str = "AI System",
    subtitle: str = "",
    style: str = "banner"
) -> Dict[str, Any]:
    """
    Send a system notification
    
    Args:
        message: The notification message
        title: Notification title
        subtitle: Optional subtitle
        style: Notification style ("banner" or "alert")
        
    Returns:
        Dict containing status and basic usage metrics
    """
    start_time = time.time()
    
    try:
        script_path = os.path.join("ai-scripts", "notify.py")
        cmd = [
            "python3",
            script_path,
            message,
            title,
            subtitle
        ]
        if style == "alert":
            cmd.append("--alert")
            
        subprocess.run(cmd, check=True)
        
        # Track basic usage metrics
        usage = {
            "notifications": 1,
            "message_length": len(message),
            "style": style,
            "latency_seconds": time.time() - start_time
        }
        
        return {
            "success": True,
            "usage": usage
        }
        
    except Exception as e:
        logger.error(f"Notification failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "usage": {
                "notifications": 0,
                "message_length": len(message),
                "style": style,
                "latency_seconds": time.time() - start_time
            }
        }