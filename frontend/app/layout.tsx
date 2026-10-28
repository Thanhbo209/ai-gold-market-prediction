import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Gold Market Prediction | Dashboard",
  description:
    "AI-driven real-time gold market forecasting and predictive intelligence platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>): React.JSX.Element {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col font-sans">{children}</body>
    </html>
  );
}
