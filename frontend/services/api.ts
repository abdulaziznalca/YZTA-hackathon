import type { ChatResponse, DashboardSummary, Order, Product } from "@/types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function sendChatMessage(message: string): Promise<ChatResponse> {
  const res = await fetch(`${BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error("Mesaj gönderilemedi");
  return res.json();
}

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  const res = await fetch(`${BASE}/api/dashboard/summary`, { cache: "no-store" });
  if (!res.ok) throw new Error("Dashboard verisi alınamadı");
  return res.json();
}

export async function fetchOrders(): Promise<Order[]> {
  const res = await fetch(`${BASE}/api/orders`, { cache: "no-store" });
  if (!res.ok) throw new Error("Siparişler alınamadı");
  return res.json();
}

export async function fetchStock(): Promise<Product[]> {
  const res = await fetch(`${BASE}/api/stock`, { cache: "no-store" });
  if (!res.ok) throw new Error("Stok bilgisi alınamadı");
  return res.json();
}
