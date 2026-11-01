"""Import all models so Alembic and the app can discover them."""

from src.ai.models import AIRecommendation  # noqa: F401
from src.chat.models import ChatConversation, ChatMessage  # noqa: F401
from src.companies.models import Company  # noqa: F401
from src.delivery.models import (  # noqa: F401
    CourierProfile,
    Customer,
    DeliveryAssignment,
    DeliveryConfirmation,
    DeliveryItem,
    DeliveryOrder,
    DeliveryProof,
    DeliveryStatusHistory,
)
from src.notifications.models import Notification  # noqa: F401
from src.schemas.audit import AuditLog  # noqa: F401
from src.tracking.models import GPSLocation  # noqa: F401
from src.users.models import CompanyMembership, Permission, Role, User, role_permissions  # noqa: F401
