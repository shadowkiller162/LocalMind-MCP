# core/tests/conftest.py
import factory
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from ..models import Conversation
from ..models import Message

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """使用者工廠"""

    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    name = factory.Faker("name")
    display_name = factory.Faker("name")
    is_active = True
    is_verified = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if extracted:
            self.set_password(extracted)
        else:
            self.set_password("testpassword123")


class ConversationFactory(factory.django.DjangoModelFactory):
    """對話工廠"""

    class Meta:
        model = Conversation

    user = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence", nb_words=3)
    is_active = True


class MessageFactory(factory.django.DjangoModelFactory):
    """訊息工廠"""

    class Meta:
        model = Message

    conversation = factory.SubFactory(ConversationFactory)
    sender = Message.SenderType.USER
    content = factory.Faker("text", max_nb_chars=200)
    is_processed = False


@pytest.fixture()
def user():
    """創建測試使用者"""
    return UserFactory()


@pytest.fixture()
def conversation(user):
    """創建測試對話"""
    return ConversationFactory(user=user)


@pytest.fixture()
def message(conversation):
    """創建測試訊息"""
    return MessageFactory(conversation=conversation)


@pytest.fixture()
def api_client():
    """創建 API 客戶端"""
    return APIClient()


@pytest.fixture()
def authenticated_client(api_client, user):
    """創建已認證的 API 客戶端"""
    api_client.force_authenticate(user=user)
    return api_client
