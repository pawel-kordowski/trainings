from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

from app.domain import entities
from app.domain.services.training_service import TrainingService


@patch("app.domain.services.training_service.TrainingRepository", autospec=True)
@patch("app.domain.services.training_service.tasks.handle_new_training")
async def test_create_training(mocked_handle_new_training, mocked_training_repository):
    start_time = datetime.utcnow()
    end_time = datetime.utcnow()
    name = "name"
    user_id = uuid4()
    training = entities.Training(
        id=uuid4(), start_time=start_time, end_time=end_time, name=name, user_id=user_id
    )
    mocked_training_repository_instance = (
        mocked_training_repository.return_value.__aenter__.return_value
    )
    mocked_training_repository_instance.create_training.return_value = training

    assert (
        await TrainingService.create_training(
            user_id=user_id, name=name, start_time=start_time, end_time=end_time
        )
        == training
    )
    mocked_training_repository_instance.create_training.assert_awaited_once_with(
        user_id=user_id, name=name, start_time=start_time, end_time=end_time
    )
    mocked_handle_new_training.delay.assert_called_once_with(
        user_id=str(user_id), training_id=str(training.id)
    )


@patch("app.domain.services.training_service.TrainingRepository", autospec=True)
async def test_get_training(mocked_training_repository):
    request_user_id = uuid4()
    training = entities.Training(
        id=uuid4(),
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow(),
        name="name",
        user_id=uuid4(),
    )
    mocked_training_repository_instance = (
        mocked_training_repository.return_value.__aenter__.return_value
    )
    mocked_training_repository_instance.get_training_by_id.return_value = training

    assert (
        await TrainingService.get_training(
            request_user_id=request_user_id, training_id=training.id
        )
        == training
    )
    mocked_training_repository_instance.get_training_by_id.assert_awaited_once_with(
        request_user_id=request_user_id, training_id=training.id
    )


@patch("app.domain.services.training_service.TrainingRepository", autospec=True)
async def test_get_user_trainings(mocked_training_repository):
    request_user_id = uuid4()
    user_id = uuid4()
    trainings = [
        entities.Training(
            id=uuid4(),
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            name="name",
            user_id=uuid4(),
        ),
        entities.Training(
            id=uuid4(),
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            name="name",
            user_id=uuid4(),
        ),
    ]
    mocked_training_repository_instance = (
        mocked_training_repository.return_value.__aenter__.return_value
    )
    mocked_training_repository_instance.get_user_trainings.return_value = trainings

    assert (
        await TrainingService.get_user_trainings(
            request_user_id=request_user_id, user_id=user_id
        )
        == trainings
    )
    mocked_training_repository_instance.get_user_trainings.assert_awaited_once_with(
        request_user_id=request_user_id, user_id=user_id
    )
