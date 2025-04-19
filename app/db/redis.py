import json
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

import redis.asyncio as aioredis

from app.core.config import get_app_settings


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
	settings = get_app_settings()
	async with aioredis.from_url(  # type: ignore[no-untyped-call]
		settings.redis_url,
		decode_responses=True,
	) as redis:
		yield redis


async def publish_event(
	redis: aioredis.Redis,
	channel: str,
	event_type: str,
	event_data: dict[str, Any],
	username: str | None = None,
) -> None:
	new_data = {
		"timestamp": datetime.now().isoformat(sep="T", timespec="auto"),
	}
	event_data.update(new_data)
	if username:
		event_data["event_user"] = username
	event = {
		"event": event_type,
		"data": event_data,
	}
	await redis.publish(channel, json.dumps(event))
