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

export interface IntentCount {
  intent: string;
  count: number;
}

export interface ProductQueryItem {
  product_name: string;
  query_count: number;
  current_stock: number | null;
  stock_status: "ok" | "low" | "critical" | "out_of_stock" | "unknown";
}

export interface AnalyticsAlert {
  type: string;
  message: string;
  severity: "high" | "medium" | "low";
}

export interface AnalyticsStats {
  total_interactions: number;
  intent_distribution: IntentCount[];
}

export interface AnalyticsSummary {
  period_hours: number;
  stats: AnalyticsStats;
  top_queried_products: ProductQueryItem[];
  alerts: AnalyticsAlert[];
}