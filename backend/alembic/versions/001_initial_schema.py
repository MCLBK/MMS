"""Initial schema — all tables.

Revision ID: 001_initial
Revises:
Create Date: 2026-10-31
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Roles
    op.create_table(
        "roles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(50), unique=True, nullable=False),
        sa.Column("description", sa.Text, default=""),
        sa.Column("is_system", sa.Boolean, default=False),
    )

    # Permissions
    op.create_table(
        "permissions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("codename", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text, default=""),
    )

    # Role-Permissions M2M
    op.create_table(
        "role_permissions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permission_id", UUID(as_uuid=True), sa.ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False),
    )

    # Companies
    op.create_table(
        "companies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("address", sa.Text, default=""),
        sa.Column("city", sa.String(100), default=""),
        sa.Column("country", sa.String(100), default="CI"),
        sa.Column("phone", sa.String(20), default=""),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("settings_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Users
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("is_verified", sa.Boolean, default=False),
        sa.Column("global_role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id"), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Company memberships
    op.create_table(
        "company_memberships",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "company_id", name="uq_membership_user_company"),
    )

    # Customers
    op.create_table(
        "customers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("address", sa.Text, default=""),
        sa.Column("city", sa.String(100), default=""),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Courier profiles
    op.create_table(
        "courier_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("vehicle_type", sa.Enum("bicycle", "motorcycle", "car", "van", "truck", name="vehicle_type"), default="motorcycle"),
        sa.Column("max_weight_kg", sa.Numeric(8, 2), default=20.0),
        sa.Column("max_volume_m3", sa.Numeric(8, 3), default=0.5),
        sa.Column("license_number", sa.String(50), nullable=True),
        sa.Column("status", sa.Enum("available", "busy", "offline", name="courier_status"), default="offline"),
        sa.Column("current_lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("current_lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("last_position_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rating", sa.Numeric(3, 2), default=5.0),
        sa.Column("total_deliveries", sa.Integer, default=0),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Delivery orders
    op.create_table(
        "delivery_orders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("customer_id", UUID(as_uuid=True), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reference", sa.String(50), unique=True, nullable=False, index=True),
        sa.Column("status", sa.Enum(
            "draft", "pending", "analyzing", "ready_to_assign", "assigning", "assigned",
            "courier_accepted", "pickup_in_progress", "picked_up", "in_transit", "arriving",
            "delivered", "confirmed", "completed", "courier_refused", "expired",
            "delivery_failed", "cancelled", "disputed", "under_review", "resolved",
            name="order_status"
        ), default="draft", index=True),
        sa.Column("priority", sa.Enum("low", "normal", "high", "urgent", name="order_priority"), default="normal"),
        sa.Column("pickup_address", sa.Text, nullable=False),
        sa.Column("pickup_lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("pickup_lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("delivery_address", sa.Text, nullable=False),
        sa.Column("delivery_lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("delivery_lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("total_weight_kg", sa.Numeric(8, 2), nullable=True),
        sa.Column("total_volume_m3", sa.Numeric(8, 3), nullable=True),
        sa.Column("estimated_distance_km", sa.Numeric(10, 2), nullable=True),
        sa.Column("estimated_duration_min", sa.Integer, nullable=True),
        sa.Column("requested_delivery_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("special_instructions", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Delivery items
    op.create_table(
        "delivery_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("order_id", UUID(as_uuid=True), sa.ForeignKey("delivery_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("description", sa.String(300), nullable=False),
        sa.Column("quantity", sa.Integer, default=1),
        sa.Column("weight_kg", sa.Numeric(8, 2), nullable=True),
        sa.Column("is_fragile", sa.Boolean, default=False),
        sa.Column("requires_signature", sa.Boolean, default=False),
    )

    # Delivery assignments
    op.create_table(
        "delivery_assignments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("order_id", UUID(as_uuid=True), sa.ForeignKey("delivery_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("courier_id", UUID(as_uuid=True), sa.ForeignKey("courier_profiles.id"), nullable=False, index=True),
        sa.Column("status", sa.Enum("pending", "accepted", "refused", "expired", "completed", "failed", name="assignment_status"), default="pending", index=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pickup_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ai_score", sa.Numeric(5, 4), nullable=True),
        sa.Column("ai_reasoning", sa.JSON, nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Delivery status history
    op.create_table(
        "delivery_status_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("order_id", UUID(as_uuid=True), sa.ForeignKey("delivery_orders.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("changed_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("old_status", sa.String(50), nullable=False),
        sa.Column("new_status", sa.String(50), nullable=False),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("metadata_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Delivery proofs
    op.create_table(
        "delivery_proofs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("assignment_id", UUID(as_uuid=True), sa.ForeignKey("delivery_assignments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.Enum("photo", "signature", "code", name="proof_type"), nullable=False),
        sa.Column("file_url", sa.String(500), nullable=True),
        sa.Column("verification_code", sa.String(20), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Delivery confirmations
    op.create_table(
        "delivery_confirmations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("assignment_id", UUID(as_uuid=True), sa.ForeignKey("delivery_assignments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("confirmed_by", sa.Enum("courier", "customer", "system", name="confirmation_source"), nullable=False),
        sa.Column("status", sa.Enum("confirmed", "disputed", "partial", name="confirmation_status"), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=False),
    )

    # GPS locations
    op.create_table(
        "gps_locations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("courier_id", UUID(as_uuid=True), sa.ForeignKey("courier_profiles.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("assignment_id", UUID(as_uuid=True), sa.ForeignKey("delivery_assignments.id"), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=False),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=False),
        sa.Column("altitude", sa.Numeric(10, 2), nullable=True),
        sa.Column("accuracy", sa.Numeric(8, 2), nullable=True),
        sa.Column("speed_kmh", sa.Numeric(6, 2), nullable=True),
        sa.Column("heading", sa.Numeric(5, 2), nullable=True),
        sa.Column("battery_level", sa.SmallInteger, nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Notifications
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("data", sa.JSON, nullable=True),
        sa.Column("is_read", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Chat conversations
    op.create_table(
        "chat_conversations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order_id", UUID(as_uuid=True), sa.ForeignKey("delivery_orders.id"), nullable=True),
        sa.Column("title", sa.String(200), default=""),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Chat messages
    op.create_table(
        "chat_messages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", UUID(as_uuid=True), sa.ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("metadata_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # AI recommendations
    op.create_table(
        "ai_recommendations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("order_id", UUID(as_uuid=True), sa.ForeignKey("delivery_orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("courier_id", UUID(as_uuid=True), sa.ForeignKey("courier_profiles.id"), nullable=False),
        sa.Column("score", sa.Numeric(5, 4), nullable=False),
        sa.Column("factors", sa.JSON, nullable=False),
        sa.Column("distance_km", sa.Numeric(10, 2), nullable=False),
        sa.Column("estimated_arrival_min", sa.Integer, nullable=False),
        sa.Column("confidence", sa.Numeric(3, 2), nullable=False),
        sa.Column("model_version", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Audit logs
    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(100), nullable=True),
        sa.Column("details", sa.JSON, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
    )


def downgrade() -> None:
    tables = [
        "audit_logs", "ai_recommendations", "chat_messages", "chat_conversations",
        "notifications", "gps_locations", "delivery_confirmations", "delivery_proofs",
        "delivery_status_history", "delivery_assignments", "delivery_items",
        "delivery_orders", "courier_profiles", "customers", "company_memberships",
        "users", "companies", "role_permissions", "permissions", "roles",
    ]
    for t in tables:
        op.drop_table(t)

    for enum_name in [
        "vehicle_type", "courier_status", "order_status", "order_priority",
        "assignment_status", "proof_type", "confirmation_source", "confirmation_status",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
