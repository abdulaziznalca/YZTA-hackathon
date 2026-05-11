import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Product } from "@/types";

interface StockAlertProps {
  products: Product[];
}

function getStockBadge(stok: number) {
  if (stok <= 0) return <Badge variant="destructive">Tükendi</Badge>;
  if (stok <= 5) return <Badge variant="destructive">Kritik</Badge>;
  return <Badge className="bg-yellow-400 text-yellow-900 hover:bg-yellow-400">Düşük</Badge>;
}

export function StockAlert({ products }: StockAlertProps) {
  const alerts = products.filter((p) => p.stok_miktari <= 10);

  if (alerts.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Stok Uyarıları</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Kritik stok yok.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Stok Uyarıları</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {alerts.map((p) => (
            <li key={p.isim} className="flex items-center justify-between text-sm">
              <span>{p.isim}</span>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">{p.stok_miktari} adet</span>
                {getStockBadge(p.stok_miktari)}
              </div>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
