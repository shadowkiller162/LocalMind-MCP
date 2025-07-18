# core/services/factory.py
import logging

from django.conf import settings

from .ai_service import AIService
from .anthropic_service import AnthropicService
from .google_service import GoogleService
from .mock_service import MockAIService
from .openai_service import OpenAIService

logger = logging.getLogger(__name__)


class AIServiceFactory:
    """AI 服務工廠類"""

    # 註冊的服務類型
    SERVICE_CLASSES = {
        "openai": OpenAIService,
        "anthropic": AnthropicService,
        "google": GoogleService,
        "mock": MockAIService,
    }

    @classmethod
    def create_service(cls, service_name: str | None = None) -> AIService:
        """
        建立 AI 服務實例

        Args:
            service_name: 服務名稱，如果為 None 則使用預設服務

        Returns:
            AIService: AI 服務實例
        """
        # 取得設定
        config = getattr(settings, "AI_SERVICES_CONFIG", {})

        # 決定使用哪個服務
        if service_name is None:
            service_name = config.get("DEFAULT_SERVICE", "mock")

        service_name = service_name.lower()

        # 檢查服務是否支援
        if service_name not in cls.SERVICE_CLASSES:
            logger.warning(f"不支援的 AI 服務：{service_name}，將使用 Mock 服務")
            service_name = "mock"

        # 取得服務配置
        service_config = config.get(service_name.upper(), {})

        # 檢查服務是否啟用
        if not service_config.get("ENABLED", False) and service_name != "mock":
            logger.warning(f"{service_name} 服務被禁用，將使用 Mock 服務")
            service_name = "mock"
            service_config = config.get("MOCK", {})

        # 添加通用設定
        service_config.update({
            "TIMEOUT": config.get("TIMEOUT", 30),
            "RETRY_ATTEMPTS": config.get("RETRY_ATTEMPTS", 3),
        })

        # 建立服務實例
        service_class = cls.SERVICE_CLASSES[service_name]

        try:
            service = service_class(service_config)
            logger.info(f"成功建立 {service.get_service_name()} 服務")
            return service
        except Exception as e:
            logger.error(f"建立 {service_name} 服務失敗：{e!s}")

            # 如果不是 mock 服務且允許回退，則嘗試使用 mock 服務
            if service_name != "mock" and config.get("FALLBACK_TO_MOCK", True):
                logger.info("回退到 Mock 服務")
                return cls.create_service("mock")
            else:
                raise

    @classmethod
    def get_available_services(cls) -> dict[str, bool]:
        """
        取得所有服務的可用狀態

        Returns:
            Dict[str, bool]: 服務名稱與可用狀態的字典
        """
        config = getattr(settings, "AI_SERVICES_CONFIG", {})
        availability = {}

        for service_name in cls.SERVICE_CLASSES.keys():
            try:
                service_config = config.get(service_name.upper(), {})
                service_class = cls.SERVICE_CLASSES[service_name]
                service = service_class(service_config)
                availability[service_name] = service.is_available()
            except Exception as e:
                logger.error(f"檢查 {service_name} 服務可用性失敗：{e!s}")
                availability[service_name] = False

        return availability

    @classmethod
    def create_service_with_fallback(cls, preferred_services: list) -> AIService:
        """
        按優先順序建立服務，如果首選服務不可用則嘗試備選服務

        Args:
            preferred_services: 優先順序的服務名稱列表

        Returns:
            AIService: AI 服務實例
        """
        for service_name in preferred_services:
            try:
                service = cls.create_service(service_name)
                if service.is_available():
                    logger.info(f"使用 {service.get_service_name()} 服務")
                    return service
                else:
                    logger.warning(f"{service_name} 服務不可用，嘗試下一個服務")
            except Exception as e:
                logger.error(f"建立 {service_name} 服務失敗：{e!s}，嘗試下一個服務")

        # 如果所有服務都不可用，使用 mock 服務
        logger.warning("所有首選服務都不可用，使用 Mock 服務")
        return cls.create_service("mock")
