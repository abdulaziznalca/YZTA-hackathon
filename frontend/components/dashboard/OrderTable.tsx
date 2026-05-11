import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Order } from "@/types";

interface OrderTableProps {
  orders: Order[];
}

const statusStyles: Record<string, string> = {
  "Kargoya Verildi": "bg-blue-100 text-blue-800 hover:bg-blue-100",
  "Teslim Edildi": "bg-green-100 text-green-800 hover:bg-green-100",
  "Hazırlanıyor": "bg-yellow-100 text-yellow-800 hover:bg-yellow-100",
  "İptal Edildi": "bg-red-100 text-red-800 hover:bg-red-100",
  "Gecikti": "bg-orange-100 text-orange-800 hover:bg-orange-100",
};

export function OrderTable({ orders }: OrderTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Siparişler</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-muted-foreground">
                <th className="py-2 text-left font-medium">Sipariş No</th>
                <th className="py-2 text-left font-medium">Müşteri</th>
                <th className="py-2 text-left font-medium">Durum</th>
                <th className="py-2 text-left font-medium">Tahmini Teslim</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.id} className="border-b last:border-0">
                  <td className="py-2 font-mono">#{order.id}</td>
                  <td className="py-2">{order.musteri_adi}</td>
                  <td className="py-2">
                    <Badge className={statusStyles[order.durum] ?? "bg-gray-100 text-gray-800 hover:bg-gray-100"}>
                      {order.durum}
                    </Badge>
                  </td>
                  <td className="py-2 text-muted-foreground">{order.tahmini_teslim}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
