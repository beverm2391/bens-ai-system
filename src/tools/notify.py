#!/usr/bin/env python3
"""
AI script for sending notifications using Claude.
"""
from src.clients.notification_client import NotificationClient

def handle_notification(**kwargs):
    """Handle notification tool calls from Claude"""
    NotificationClient.notify(**kwargs)
    return {"status": "success"}