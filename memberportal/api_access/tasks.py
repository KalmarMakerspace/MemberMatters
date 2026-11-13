from membermatters.celeryapp import app
from constance import config
from django.utils import timezone
from datetime import timedelta
import os
import logging

logger = logging.getLogger("api_access:tasks")


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        3600 if os.environ.get("MM_ENV") == "Production" else 30,
        heartbeat_logger.s(),
        expires=10,
        name="celery_heartbeat_logger",
    )
    sender.add_periodic_task(
        3600 * 24,
        prune_access_logs.s(),
        expires=3600,
        name="celery_prune_access_logs",
    )


@app.task
def heartbeat_logger():
    logger.debug("Celery is alive!")


@app.task
def prune_access_logs():
    """Delete door and interlock log entries older than ACCESS_LOG_RETENTION_DAYS."""
    from access.models import DoorLog, InterlockLog

    retention_days = config.ACCESS_LOG_RETENTION_DAYS
    if not retention_days or retention_days <= 0:
        logger.info(
            "ACCESS_LOG_RETENTION_DAYS is disabled, skipping access log pruning."
        )
        return

    cutoff = timezone.now() - timedelta(days=retention_days)

    door_deleted, _ = DoorLog.objects.filter(date__lt=cutoff).delete()
    interlock_deleted, _ = InterlockLog.objects.filter(date_updated__lt=cutoff).delete()

    logger.info(
        f"Pruned {door_deleted} door log and {interlock_deleted} interlock log "
        f"entries older than {retention_days} days ({cutoff.isoformat()})."
    )
