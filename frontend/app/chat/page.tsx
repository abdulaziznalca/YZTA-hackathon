"use client";

import { useChat } from "@/hooks/useChat";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { ChatInput } from "@/components/chat/ChatInput";

export default function ChatPage() {
  const { messages, isLoading, sendMessage } = useChat();

  return (
    <div className="flex flex-col h-full">
      <div className="border-b px-6 py-3">
        <h1 className="font-semibold text-sm">Müşteri Asistanı</h1>
        <p className="text-xs text-muted-foreground">
          Sipariş, kargo, stok ve iade sorularınızı sorabilirsiniz.
        </p>
      </div>
      <ChatWindow messages={messages} isLoading={isLoading} />
      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}
