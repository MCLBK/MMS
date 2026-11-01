from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_orders: int
    orders_today: int
    in_transit: int
    completed_today: int
    pending: int
    failed: int
    total_couriers: int
    available_couriers: int
    avg_delivery_time_min: float | None
    completion_rate: float | None


class OrdersByStatus(BaseModel):
    status: str
    count: int


class DailyStats(BaseModel):
    date: str
    created: int
    completed: int
    failed: int


class CourierPerformance(BaseModel):
    courier_id: str
    courier_name: str
    total_deliveries: int
    completed: int
    failed: int
    avg_rating: float
    completion_rate: float
