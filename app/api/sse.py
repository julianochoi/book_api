import asyncio
import json
from typing import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from app.api import dependencies

router = APIRouter(
	prefix="/sse",
	tags=["sse"],
)

# TODO move to app settings later
STREAM_DELAY = 0.1  # second


async def event_generator(
	redis: aioredis.Redis,
	channel: str,
	request: Request,
) -> AsyncGenerator[str, None]:
	pubsub = redis.pubsub()
	await pubsub.subscribe(channel)

	try:
		while True:
			if await request.is_disconnected():
				break

			message = await pubsub.get_message(ignore_subscribe_messages=True)
			if message:
				# TODO improve message handling
				yield json.loads(message["data"])

			await asyncio.sleep(STREAM_DELAY)
	except asyncio.CancelledError:
		raise
	finally:
		await pubsub.unsubscribe(channel)
		await pubsub.close()
		await redis.close()


@router.get(
	"/updates/{channel}",
	status_code=200,
	summary="Get update stream from channel",
)
async def sse_updates(
	redis: dependencies.RedisDep,
	channel: str,
	request: Request,
) -> EventSourceResponse:
	"""This endpoint provides a server-sent events (SSE) stream of real-time updates from a specified Redis channel.
	
	Clients can subscribe to this stream to receive updates as they occur."""
	return EventSourceResponse(
		content=event_generator(redis, channel, request),
		send_timeout=30,  # seconds
	)
