import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageSquare, Package, Truck, AlertTriangle } from "lucide-react";
import type { AnalyticsStats } from "@/types";

interface StatsCardsProps {
  stats: AnalyticsStats;
}

const INTENT_ICONS: Record<string, typeof MessageSquare> = {
  stock_query: Package,
  shipment_status: Truck,
  complaint: AlertTriangle,
};

const INTENT_LABELS: Record<string, string> = {
  stock_query: "Stok Sorgusu",
  shipment_status: "Kargo Takibi",
  order_status: "Sipariş Durumu",
  policy_question: "Politika",
  complaint: "Şikayet",
  manager_summary: "Yönetici Özeti",
  unknown: "Diğer",
};

export function StatsCards({ stats }: StatsCardsProps) {
  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Toplam Etkileşim
          </CardTitle>
          <MessageSquare className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold">{stats.total_interactions}</p>
        </CardContent>
      </Card>

      {stats.intent_distribution.slice(0, 3).map((item) => {
        const Icon = INTENT_ICONS[item.intent] || MessageSquare;
        return (
          <Card key={item.intent}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {INTENT_LABELS[item.intent] || item.intent}
              </CardTitle>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{item.count}</p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}