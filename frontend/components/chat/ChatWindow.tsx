"use client";

import { useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageBubble } from "./MessageBubble";
import type { ChatMessage } from "@/types";

interface ChatWindowProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

export function ChatWindow({ messages, isLoading }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <ScrollArea className="flex-1 px-4 pt-4">
      {messages.length === 0 && (
        <div className="flex flex-col items-center justify-center h-full text-muted-foreground text-sm gap-2 py-20">
          <p className="text-2xl">🤖</p>
          <p className="font-medium">ShopPilot AI&apos;ya hoş geldiniz</p>
          <p>Sipariş, stok veya iade hakkında bir soru sorun.</p>
        </div>
      )}

      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}

      {isLoading && (
        <div className="flex justify-start mb-4">
          <div className="bg-muted rounded-2xl rounded-bl-sm px-4 py-3 flex gap-1">
            <span className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:0ms]" />
            <span className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:150ms]" />
            <span className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:300ms]" />
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </ScrollArea>
  );
}
