import { Package, ShoppingCart, Truck, AlertTriangle } from "lucide-react";
import { fetchDashboardSummary, fetchOrders, fetchStock } from "@/services/api";
import { SummaryCard } from "@/components/dashboard/SummaryCard";
import { StockAlert } from "@/components/dashboard/StockAlert";
import { OrderTable } from "@/components/dashboard/OrderTable";

export default async function DashboardPage() {
  const [summary, orders, stock] = await Promise.all([
    fetchDashboardSummary(),
    fetchOrders(),
    fetchStock(),
  ]);

  const delayedVariant = summary.delayed_orders > 0 ? "danger" : "default";
  const stockVariant = summary.critical_stock.length > 0 ? "warning" : "default";

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground text-sm mt-1">Günlük operasyon özeti</p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <SummaryCard
          title="Toplam Sipariş"
          value={summary.total_orders}
          Icon={ShoppingCart}
        />
        <SummaryCard
          title="Kargodaki"
          value={summary.shipped_orders}
          Icon={Truck}
          variant="default"
        />
        <SummaryCard
          title="Geciken"
          value={summary.delayed_orders}
          Icon={AlertTriangle}
          variant={delayedVariant}
        />
        <SummaryCard
          title="Toplam Ürün"
          value={summary.total_products}
          Icon={Package}
          variant={stockVariant}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <StockAlert products={stock} />
        <OrderTable orders={orders} />
      </div>
    </div>
  );
}
