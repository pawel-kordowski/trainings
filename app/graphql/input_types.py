from datetime import datetime
from typing import Optional

import strawberry


@strawberry.input
class TrainingInput:
    name: str
    start_time: datetime
    end_time: Optional[datetime]
