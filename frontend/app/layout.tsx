import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { Separator } from "@/components/ui/separator";
import { MessageSquare, LayoutDashboard, Bot, BarChart3 } from "lucide-react";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "ShopPilot AI",
  description: "KOBİ için AI destekli müşteri hizmetleri",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="tr" className={cn("font-sans", geistSans.variable)}>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <div className="flex h-screen">
          <aside className="w-56 flex-shrink-0 border-r bg-muted/30 flex flex-col">
            <div className="p-4 flex items-center gap-2">
              <Bot className="h-6 w-6 text-primary" />
              <span className="font-bold text-sm">ShopPilot AI</span>
            </div>
            <Separator />
            <nav className="flex-1 p-3 space-y-1">
              <Link
                href="/chat"
                className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors"
              >
                <MessageSquare className="h-4 w-4" />
                Chat
              </Link>
              <Link
                href="/dashboard"
                className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors"
              >
                <LayoutDashboard className="h-4 w-4" />
                Dashboard
              </Link>
              <Link
                href="/analytics"
                className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors"
              >
                <BarChart3 className="h-4 w-4" />
                Analytics
              </Link>
            </nav>
          </aside>
          <main className="flex-1 overflow-hidden flex flex-col">{children}</main>
        </div>
      </body>
    </html>
  );
}