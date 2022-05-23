from datetime import datetime
from uuid import UUID

import strawberry

from app.graphql.types.reactions import Reaction


@strawberry.type
class Training:
    id: UUID
    start_time: datetime
    end_time: datetime | None
    name: str

    @strawberry.field
    async def reactions_count(self) -> int:
        from app.graphql.data_loaders.reactions import (
            get_reaction_count_by_training_ids_loader,
        )

        return await get_reaction_count_by_training_ids_loader.load(self.id)

    @strawberry.field
    async def reactions(self) -> list[Reaction]:
        from app.graphql.data_loaders.reactions import (
            get_reactions_by_training_ids_loader,
        )

        return await get_reactions_by_training_ids_loader.load(self.id)
