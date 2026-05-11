export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  intent?: string;
  timestamp: Date;
}

export interface ChatResponse {
  response: string;
  intent?: string;
}

export interface Order {
  id: number;
  musteri_adi: string;
  durum: string;
  tahmini_teslim: string;
}

export interface Product {
  isim: string;
  stok_miktari: number;
  fiyat: number;
}

export interface DashboardSummary {
  total_orders: number;
  shipped_orders: number;
  delayed_orders: number;
  total_products: number;
  critical_stock: { isim: string; stok_miktari: number }[];
}
