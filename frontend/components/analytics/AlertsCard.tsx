import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, AlertCircle, Info } from "lucide-react";
import type { AnalyticsAlert } from "@/types";

interface AlertsCardProps {
  alerts: AnalyticsAlert[];
}

const SEVERITY_STYLES: Record<string, { bg: string; icon: typeof AlertTriangle }> = {
  high: { bg: "bg-red-50 border-red-200", icon: AlertTriangle },
  medium: { bg: "bg-yellow-50 border-yellow-200", icon: AlertCircle },
  low: { bg: "bg-blue-50 border-blue-200", icon: Info },
};

export function AlertsCard({ alerts }: AlertsCardProps) {
  if (alerts.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Uyarılar</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Aktif uyarı yok.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Uyarılar</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {alerts.map((alert, index) => {
          const style = SEVERITY_STYLES[alert.severity] || SEVERITY_STYLES.low;
          const Icon = style.icon;
          return (
            <div
              key={index}
              className={`flex items-start gap-3 p-3 rounded-lg border ${style.bg}`}
            >
              <Icon className="h-5 w-5 mt-0.5 flex-shrink-0" />
              <p className="text-sm">{alert.message}</p>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}