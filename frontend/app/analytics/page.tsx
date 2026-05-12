import { fetchAnalyticsSummary } from "@/services/api";
import { StatsCards } from "@/components/analytics/StatsCards";
import { ProductQueryTable } from "@/components/analytics/ProductQueryTable";
import { AlertsCard } from "@/components/analytics/AlertsCard";

export default async function AnalyticsPage() {
  const summary = await fetchAnalyticsSummary(24);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Chat Analytics</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Son 24 saatlik müşteri etkileşim analizi
        </p>
      </div>

      <StatsCards stats={summary.stats} />

      <div className="grid gap-4 lg:grid-cols-2">
        <ProductQueryTable products={summary.top_queried_products} />
        <AlertsCard alerts={summary.alerts} />
      </div>
    </div>
  );
}