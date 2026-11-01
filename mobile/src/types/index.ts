export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string | null;
  avatar_url: string | null;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface DeliveryAssignment {
  id: string;
  order_id: string;
  reference: string;
  status: string;
  pickup_address: string;
  delivery_address: string;
  customer_name: string;
  customer_phone: string;
  priority: string;
  assigned_at: string;
  expires_at: string;
}

export interface GPSPosition {
  latitude: number;
  longitude: number;
  timestamp: number;
}
