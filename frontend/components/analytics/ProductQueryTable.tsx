import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ProductQueryItem } from "@/types";

interface ProductQueryTableProps {
  products: ProductQueryItem[];
}

const STATUS_STYLES: Record<string, string> = {
  ok: "bg-green-100 text-green-800",
  low: "bg-yellow-100 text-yellow-800",
  critical: "bg-orange-100 text-orange-800",
  out_of_stock: "bg-red-100 text-red-800",
  unknown: "bg-gray-100 text-gray-800",
};

const STATUS_LABELS: Record<string, string> = {
  ok: "Yeterli",
  low: "Düşük",
  critical: "Kritik",
  out_of_stock: "Tükendi",
  unknown: "Bilinmiyor",
};

export function ProductQueryTable({ products }: ProductQueryTableProps) {
  if (products.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Talep Gören Ürünler</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Henüz ürün sorgusu yok.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Talep Gören Ürünler</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-muted-foreground">
                <th className="py-2 text-left font-medium">Ürün</th>
                <th className="py-2 text-left font-medium">Sorgu</th>
                <th className="py-2 text-left font-medium">Stok</th>
                <th className="py-2 text-left font-medium">Durum</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => (
                <tr key={product.product_name} className="border-b last:border-0">
                  <td className="py-2 font-medium">{product.product_name}</td>
                  <td className="py-2">{product.query_count} sorgu</td>
                  <td className="py-2">{product.current_stock ?? "-"} adet</td>
                  <td className="py-2">
                    <Badge className={STATUS_STYLES[product.stock_status]}>
                      {STATUS_LABELS[product.stock_status]}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}