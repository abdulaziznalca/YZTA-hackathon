import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface SummaryCardProps {
  title: string;
  value: string | number;
  Icon?: LucideIcon;
  variant?: "default" | "warning" | "danger";
}

const variantStyles: Record<string, string> = {
  default: "border-border",
  warning: "border-yellow-400",
  danger: "border-red-500",
};

const variantValueStyles: Record<string, string> = {
  default: "text-foreground",
  warning: "text-yellow-600",
  danger: "text-red-600",
};

export function SummaryCard({ title, value, Icon, variant = "default" }: SummaryCardProps) {
  return (
    <Card className={`border-2 ${variantStyles[variant]}`}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
      </CardHeader>
      <CardContent>
        <p className={`text-3xl font-bold ${variantValueStyles[variant]}`}>{value}</p>
      </CardContent>
    </Card>
  );
}
