from datetime import timedelta

from temporalio.common import RetryPolicy
from temporalio.client import Client

from config import settings

RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=2),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=30),
    maximum_attempts=10,
)
ACTIVITY_OPTS = dict(
    start_to_close_timeout=timedelta(seconds=60),
    schedule_to_close_timeout=timedelta(seconds=60),
    retry_policy=RETRY_POLICY,
)

async def get_temporal_client():
    client = await Client.connect(
        settings.temporal_server_url,
    )
    return client
