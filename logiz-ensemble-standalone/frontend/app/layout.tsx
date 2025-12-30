import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Anomi AI - İleri Seviye Tehdit Tespit Sistemi",
  description: "Advanced anomaly detection powered by Ensemble Machine Learning",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="tr" className="dark" suppressHydrationWarning>
      <body className={`${inter.className} bg-background text-foreground antialiased`} suppressHydrationWarning>
        <div className="flex min-h-screen relative overflow-hidden">
          {/* Ambient Background Elements */}
          <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/5 rounded-full blur-[120px] pointer-events-none" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-primary/5 rounded-full blur-[120px] pointer-events-none" />

          <Sidebar />

          <main className="flex-1 ml-64 transition-all duration-300 p-8">
            <div className="max-w-7xl mx-auto pt-4">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
