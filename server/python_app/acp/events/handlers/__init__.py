import logging

logger = logging.getLogger("acp.events")

def logging_handler(event):
    logger.info(f"[ACP-Event] {event.name}: {str(event.data)[:200]}")

def metrics_handler(event):
    pass

def audit_handler(event):
    logger.info(f"[AUDIT] {event.name} at {event.timestamp}")

def webhook_handler(event):
    pass
