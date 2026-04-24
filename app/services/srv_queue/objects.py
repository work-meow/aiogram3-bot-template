# fmt: off
# isort: off
import time
import asyncio

from enum import Enum
from uuid import UUID, uuid4
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


class RequestStatus(Enum):
    """Статус запроса."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True)
class MemoryRequest:
    """Запрос в памяти."""
    payload: Dict[str, Any]
    id: UUID = field(default_factory=uuid4)

    done_event: asyncio.Event = field(init=False)
    status: RequestStatus = RequestStatus.PENDING

    created_at: float = field(default_factory=time.monotonic)
    processed_at: Optional[float] = None

    error: Optional[str] = None
    result: Optional[Any] = None

    def __post_init__(self):
        self.done_event = asyncio.Event()
