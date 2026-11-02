import type { Metadata } from "next";
import { Alan_Sans } from "next/font/google";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Gold Market Prediction | Dashboard",
  description:
    "AI-driven real-time gold market forecasting and predictive intelligence platform",
};

const alanSans = Alan_Sans({
  variable: "--font-alan-sans",
  subsets: ["latin"],
  display: "swap",
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>): React.JSX.Element {
  return (
    <html lang="en" className={`${alanSans.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col font-sans">{children}</body>
    </html>
  );
}
