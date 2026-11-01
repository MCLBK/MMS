export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string | null;
  avatar_url: string | null;
  is_active: boolean;
  is_verified: boolean;
  is_super_admin: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Company {
  id: string;
  name: string;
  slug: string;
  address: string;
  city: string;
  country: string;
  latitude: number | null;
  longitude: number | null;
  phone: string | null;
  email: string | null;
  logo_url: string | null;
  is_active: boolean;
  created_at: string;
}

export type OrderStatus =
  | "draft"
  | "pending"
  | "analyzing"
  | "ready_to_assign"
  | "assigning"
  | "assigned"
  | "courier_accepted"
  | "pickup_in_progress"
  | "picked_up"
  | "in_transit"
  | "arriving"
  | "delivered"
  | "confirmed"
  | "completed"
  | "courier_refused"
  | "expired"
  | "delivery_failed"
  | "cancelled"
  | "disputed"
  | "under_review"
  | "resolved";

export type OrderPriority = "low" | "normal" | "high" | "urgent";

export interface DeliveryOrder {
  id: string;
  company_id: string;
  customer_id: string;
  reference: string;
  status: OrderStatus;
  priority: OrderPriority;
  pickup_address: string;
  delivery_address: string;
  total_weight_kg: number | null;
  estimated_distance_km: number | null;
  estimated_duration_min: number | null;
  requested_delivery_at: string | null;
  special_instructions: string | null;
  created_at: string;
}

export interface Customer {
  id: string;
  name: string;
  phone: string;
  email: string | null;
  address: string;
  city: string;
}

export interface DeliveryItem {
  id: string;
  description: string;
  quantity: number;
  weight_kg: number | null;
  is_fragile: boolean;
  requires_signature: boolean;
}

export interface OrderDetail extends DeliveryOrder {
  pickup_lat: number | null;
  pickup_lng: number | null;
  delivery_lat: number | null;
  delivery_lng: number | null;
  customer: Customer;
  items: DeliveryItem[];
  updated_at: string;
}

export interface OrderListItem {
  id: string;
  reference: string;
  status: OrderStatus;
  priority: OrderPriority;
  customer_name: string;
  pickup_address: string;
  delivery_address: string;
  created_at: string;
}

export interface PaginatedOrders {
  items: OrderListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export type VehicleType = "bicycle" | "motorcycle" | "car" | "van" | "truck";
export type CourierStatus = "available" | "busy" | "offline";

export interface CourierListItem {
  id: string;
  user_name: string;
  vehicle_type: VehicleType;
  status: CourierStatus;
  rating: number;
  total_deliveries: number;
  is_active: boolean;
}

export interface CourierDetail extends CourierListItem {
  user_id: string;
  user_email: string;
  max_weight_kg: number;
  max_volume_m3: number;
  license_number: string | null;
  current_lat: number | null;
  current_lng: number | null;
  last_position_at: string | null;
  created_at: string;
}

export interface ApiError {
  detail: string;
}
