import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CoolShift — Energy Cooling Optimization Platform",
  description: "Advanced decision and optimization platform for cooling appliances, solar generation, and battery assets.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable} dark h-full antialiased`}
      style={{ colorScheme: "dark" }}
    >
      <body className="h-full bg-background text-foreground font-sans noise-overlay">
        <div className="flex h-full overflow-hidden">
          {/* Glassmorphic Sidebar */}
          <Sidebar />

          {/* Main workspace */}
          <div className="flex flex-col flex-1 overflow-hidden">
            <Header />
            <main className="flex-1 overflow-y-auto px-6 py-6 md:px-8">
              <div className="max-w-7xl mx-auto w-full animate-fade-in">
                {children}
              </div>
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
