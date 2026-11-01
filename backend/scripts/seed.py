"""
Seed script — populate the database with demo data.
Usage: python -m scripts.seed
"""

import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import async_session, engine
from src.database.all_models import (
    Company,
    CourierProfile,
    Customer,
    DeliveryAssignment,
    DeliveryItem,
    DeliveryOrder,
    DeliveryStatusHistory,
    GPSLocation,
    Notification,
    Permission,
    Role,
    User,
    CompanyMembership,
    role_permissions,
)

DEMO_COMPANY_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
SUPER_ADMIN_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")
COMPANY_ADMIN_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000011")
COURIER_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000012")
CUSTOMER_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000013")

now = datetime.now(timezone.utc)


def _id() -> uuid.UUID:
    return uuid.uuid4()


async def seed_roles(db: AsyncSession) -> None:
    roles = [
        Role(id=SUPER_ADMIN_ROLE_ID, name="super_admin", description="Super administrateur", is_system=True),
        Role(id=COMPANY_ADMIN_ROLE_ID, name="company_admin", description="Administrateur entreprise", is_system=True),
        Role(id=COURIER_ROLE_ID, name="courier", description="Livreur", is_system=True),
        Role(id=CUSTOMER_ROLE_ID, name="customer", description="Client", is_system=True),
    ]
    db.add_all(roles)

    perms = [
        Permission(id=_id(), codename="orders.create", description="Créer des commandes"),
        Permission(id=_id(), codename="orders.read", description="Lire les commandes"),
        Permission(id=_id(), codename="orders.update", description="Modifier les commandes"),
        Permission(id=_id(), codename="orders.delete", description="Supprimer les commandes"),
        Permission(id=_id(), codename="couriers.manage", description="Gérer les livreurs"),
        Permission(id=_id(), codename="analytics.read", description="Accéder aux analytics"),
        Permission(id=_id(), codename="company.manage", description="Gérer l'entreprise"),
        Permission(id=_id(), codename="users.manage", description="Gérer les utilisateurs"),
        Permission(id=_id(), codename="ai.use", description="Utiliser les fonctions IA"),
    ]
    db.add_all(perms)
    await db.flush()


async def seed_company(db: AsyncSession) -> None:
    company = Company(
        id=DEMO_COMPANY_ID,
        name="MMS Express Demo",
        slug="mms-express-demo",
        address="Boulevard de la République, Plateau",
        city="Abidjan",
        country="CI",
        phone="+225 07 00 00 00 00",
        email="contact@mmsexpress.ci",
        is_active=True,
        settings_json={"currency": "XOF", "timezone": "Africa/Abidjan", "max_couriers": 50},
    )
    db.add(company)
    await db.flush()


async def seed_users(db: AsyncSession) -> list[User]:
    # Argon2 hash for "Admin123!"
    hashed = "$argon2id$v=19$m=65536,t=3,p=4$c2FsdHNhbHRzYWx0$XGhImFPCbFCiLcfMbGMmtJoVFkLhBblvaV8bX3lXNfs"

    admin = User(
        id=_id(),
        email="admin@mmsexpress.com",
        hashed_password=hashed,
        first_name="Admin",
        last_name="MMS",
        phone="+225 07 01 01 01 01",
        is_active=True,
        is_verified=True,
        global_role_id=SUPER_ADMIN_ROLE_ID,
    )

    manager = User(
        id=_id(),
        email="manager@mmsexpress.com",
        hashed_password=hashed,
        first_name="Kouamé",
        last_name="Yao",
        phone="+225 07 02 02 02 02",
        is_active=True,
        is_verified=True,
        global_role_id=COMPANY_ADMIN_ROLE_ID,
    )

    courier_users = []
    courier_data = [
        ("Koné", "Moussa", "+225 07 10 10 10 10"),
        ("Traoré", "Ibrahim", "+225 07 11 11 11 11"),
        ("Coulibaly", "Fatou", "+225 07 12 12 12 12"),
        ("Diallo", "Seydou", "+225 07 13 13 13 13"),
        ("Bamba", "Aminata", "+225 07 14 14 14 14"),
    ]
    for last, first, phone in courier_data:
        u = User(
            id=_id(),
            email=f"{first.lower()}.{last.lower()}@mmsexpress.com",
            hashed_password=hashed,
            first_name=first,
            last_name=last,
            phone=phone,
            is_active=True,
            is_verified=True,
            global_role_id=COURIER_ROLE_ID,
        )
        courier_users.append(u)

    all_users = [admin, manager] + courier_users
    db.add_all(all_users)
    await db.flush()

    for u in all_users:
        role_id = u.global_role_id
        db.add(CompanyMembership(
            id=_id(),
            user_id=u.id,
            company_id=DEMO_COMPANY_ID,
            role_id=role_id,
            is_active=True,
        ))

    await db.flush()
    return all_users


async def seed_couriers(db: AsyncSession, courier_users: list[User]) -> list[CourierProfile]:
    vehicles = ["motorcycle", "motorcycle", "car", "bicycle", "van"]
    lats = [5.3364, 5.3480, 5.3200, 5.3550, 5.3100]
    lngs = [-4.0266, -3.9900, -4.0150, -4.0050, -3.9800]
    statuses = ["available", "available", "busy", "available", "offline"]

    profiles = []
    for i, user in enumerate(courier_users):
        p = CourierProfile(
            id=_id(),
            user_id=user.id,
            company_id=DEMO_COMPANY_ID,
            vehicle_type=vehicles[i],
            max_weight_kg=Decimal("25.0") if vehicles[i] != "bicycle" else Decimal("10.0"),
            max_volume_m3=Decimal("0.5") if vehicles[i] != "van" else Decimal("2.0"),
            status=statuses[i],
            current_lat=Decimal(str(lats[i])),
            current_lng=Decimal(str(lngs[i])),
            last_position_at=now - timedelta(minutes=i * 5),
            rating=Decimal(str(round(4.0 + i * 0.15, 2))),
            total_deliveries=20 + i * 12,
            is_active=True,
        )
        profiles.append(p)

    db.add_all(profiles)
    await db.flush()
    return profiles


async def seed_customers(db: AsyncSession) -> list[Customer]:
    data = [
        ("Supermarché Bonheur", "bonheur@test.ci", "+225 27 20 30 00 01", "Cocody, Riviera Palmeraie", "Abidjan", 5.3590, -3.9870),
        ("Restaurant Le Plateau", "plateau@test.ci", "+225 27 20 30 00 02", "Rue du Commerce, Plateau", "Abidjan", 5.3240, -4.0170),
        ("Pharmacie Santé+", "sante@test.ci", "+225 27 20 30 00 03", "Boulevard Lagunaire, Treichville", "Abidjan", 5.3080, -4.0120),
        ("Boutique Mode Africa", "mode@test.ci", "+225 27 20 30 00 04", "Avenue Chardy, Marcory", "Abidjan", 5.3020, -3.9900),
        ("Librairie Éducation", "educ@test.ci", "+225 27 20 30 00 05", "Rue 12, Adjamé", "Abidjan", 5.3500, -4.0250),
        ("Boulangerie Délice", "delice@test.ci", "+225 27 20 30 00 06", "Zone 4, Marcory", "Abidjan", 5.3100, -3.9950),
        ("Tech Solutions CI", "tech@test.ci", "+225 27 20 30 00 07", "Angré 8ème tranche", "Abidjan", 5.3750, -3.9650),
        ("Clinique Espoir", "espoir@test.ci", "+225 27 20 30 00 08", "Yopougon Maroc", "Abidjan", 5.3300, -4.0700),
    ]

    customers = []
    for name, email, phone, address, city, lat, lng in data:
        c = Customer(
            id=_id(),
            company_id=DEMO_COMPANY_ID,
            name=name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            latitude=Decimal(str(lat)),
            longitude=Decimal(str(lng)),
        )
        customers.append(c)

    db.add_all(customers)
    await db.flush()
    return customers


async def seed_orders(
    db: AsyncSession,
    customers: list[Customer],
    admin_user: User,
    couriers: list[CourierProfile],
) -> None:
    statuses_progression = [
        "completed", "completed", "completed", "delivered", "in_transit",
        "assigned", "pending", "draft", "cancelled", "pickup_in_progress",
    ]
    priorities = ["normal", "normal", "high", "urgent", "normal", "low", "normal", "high", "normal", "normal"]
    pickup_addr = "Entrepôt MMS, Zone Industrielle, Yopougon"
    pickup_lat, pickup_lng = Decimal("5.3260"), Decimal("-4.0600")

    for i in range(10):
        cust = customers[i % len(customers)]
        ref = f"MMS-2026-{1001 + i}"
        order_id = _id()
        created = now - timedelta(days=10 - i, hours=i)

        order = DeliveryOrder(
            id=order_id,
            company_id=DEMO_COMPANY_ID,
            customer_id=cust.id,
            created_by=admin_user.id,
            reference=ref,
            status=statuses_progression[i],
            priority=priorities[i],
            pickup_address=pickup_addr,
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            delivery_address=cust.address,
            delivery_lat=cust.latitude,
            delivery_lng=cust.longitude,
            total_weight_kg=Decimal(str(round(1.5 + i * 0.8, 2))),
            estimated_distance_km=Decimal(str(round(3.0 + i * 1.2, 2))),
            estimated_duration_min=15 + i * 5,
            requested_delivery_at=created + timedelta(hours=4),
            created_at=created,
            updated_at=created,
        )
        db.add(order)
        await db.flush()

        for j in range(1, 3):
            db.add(DeliveryItem(
                id=_id(),
                order_id=order_id,
                description=f"Colis {j} — commande {ref}",
                quantity=j,
                weight_kg=Decimal(str(round(0.5 + j * 0.3, 2))),
                is_fragile=(j == 1 and i % 3 == 0),
            ))

        if statuses_progression[i] not in ("draft", "pending", "cancelled"):
            courier = couriers[i % len(couriers)]
            assignment_id = _id()
            db.add(DeliveryAssignment(
                id=assignment_id,
                order_id=order_id,
                courier_id=courier.id,
                status="completed" if statuses_progression[i] in ("completed", "delivered", "confirmed") else "accepted",
                assigned_at=created + timedelta(minutes=10),
                responded_at=created + timedelta(minutes=12),
                pickup_at=created + timedelta(minutes=30) if statuses_progression[i] not in ("assigned",) else None,
                delivered_at=created + timedelta(hours=2) if statuses_progression[i] in ("completed", "delivered") else None,
                ai_score=Decimal(str(round(0.75 + i * 0.02, 4))),
                expires_at=created + timedelta(hours=1),
            ))

            db.add(DeliveryStatusHistory(
                id=_id(),
                order_id=order_id,
                old_status="pending",
                new_status="assigned",
                reason="Attribution IA automatique",
                created_at=created + timedelta(minutes=10),
            ))

    await db.flush()


async def seed_gps(db: AsyncSession, couriers: list[CourierProfile]) -> None:
    for courier in couriers[:3]:
        base_lat = float(courier.current_lat or 5.33)
        base_lng = float(courier.current_lng or -4.02)
        for j in range(20):
            db.add(GPSLocation(
                id=_id(),
                courier_id=courier.id,
                latitude=Decimal(str(round(base_lat + j * 0.001, 7))),
                longitude=Decimal(str(round(base_lng - j * 0.0005, 7))),
                accuracy=Decimal("8.5"),
                speed_kmh=Decimal(str(round(15 + j * 1.5, 2))),
                heading=Decimal(str(round(45 + j * 5, 2))),
                battery_level=max(20, 95 - j * 3),
                recorded_at=now - timedelta(minutes=40 - j * 2),
            ))
    await db.flush()


async def seed_notifications(db: AsyncSession, users: list[User]) -> None:
    admin = users[0]
    notifs = [
        ("order_created", "Nouvelle commande", "La commande MMS-2026-1001 a été créée"),
        ("courier_assigned", "Livreur assigné", "Moussa Koné a été assigné à MMS-2026-1003"),
        ("delivery_completed", "Livraison terminée", "MMS-2026-1001 livrée avec succès"),
        ("system", "Bienvenue", "Bienvenue sur MMS Express ! Votre plateforme est prête."),
    ]
    for ntype, title, message in notifs:
        db.add(Notification(
            id=_id(),
            user_id=admin.id,
            type=ntype,
            title=title,
            message=message,
            is_read=(ntype == "system"),
        ))
    await db.flush()


async def main() -> None:
    async with async_session() as db:
        async with db.begin():
            print("Seeding roles & permissions...")
            await seed_roles(db)

            print("Seeding company...")
            await seed_company(db)

            print("Seeding users...")
            users = await seed_users(db)
            admin = users[0]
            courier_users = users[2:]

            print("Seeding courier profiles...")
            couriers = await seed_couriers(db, courier_users)

            print("Seeding customers...")
            customers = await seed_customers(db)

            print("Seeding orders & items...")
            await seed_orders(db, customers, admin, couriers)

            print("Seeding GPS locations...")
            await seed_gps(db, couriers)

            print("Seeding notifications...")
            await seed_notifications(db, users)

        print("Done! Demo data seeded successfully.")


if __name__ == "__main__":
    asyncio.run(main())
