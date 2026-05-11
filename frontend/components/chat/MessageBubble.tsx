import { Badge } from "@/components/ui/badge";
import type { ChatMessage } from "@/types";

const INTENT_LABELS: Record<string, string> = {
  shipment_status: "Kargo",
  order_status: "Sipariş",
  stock_query: "Stok",
  policy_question: "Politika",
  complaint: "Şikayet",
  manager_summary: "Özet",
  unknown: "Genel",
};

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div className={`max-w-[75%] ${isUser ? "items-end" : "items-start"} flex flex-col gap-1`}>
        {!isUser && message.intent && (
          <Badge variant="secondary" className="text-xs w-fit">
            {INTENT_LABELS[message.intent] ?? message.intent}
          </Badge>
        )}
        <div
          className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
            isUser
              ? "bg-blue-600 text-white rounded-br-sm"
              : "bg-muted text-foreground rounded-bl-sm"
          }`}
        >
          {message.content}
        </div>
        <span className="text-xs text-muted-foreground px-1">
          {message.timestamp.toLocaleTimeString("tr-TR", {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>
    </div>
  );
}
