import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { ThemeProvider } from "@/components/theme-provider";
import { ThemeToggle } from "@/components/theme-toggle";
import Link from "next/link";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ML Experiment Tracker",
  description: "Track and monitor your machine learning experiments",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <Providers>
            <div className="min-h-screen bg-background">
              <header className="border-b">
                <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                  <Link href="/" className="hover:opacity-80 transition-opacity">
                    <h1 className="text-2xl font-bold">ML Experiment Tracker</h1>
                  </Link>
                  <div className="flex items-center gap-4">
                    <nav className="flex items-center gap-4">
                      <Link 
                        href="/" 
                        className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                      >
                        Dashboard
                      </Link>
                      <Link 
                        href="/integration" 
                        className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
                      >
                        Integration
                      </Link>
                    </nav>
                    <ThemeToggle />
                  </div>
                </div>
              </header>
              <main className="container mx-auto px-4 py-8">
                {children}
              </main>
            </div>
          </Providers>
        </ThemeProvider>
      </body>
    </html>
  );
}
