from datetime import timedelta

from temporalio.common import RetryPolicy

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