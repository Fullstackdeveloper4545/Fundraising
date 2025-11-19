import type { Metadata } from "next";
import "./globals.css";
import "sweetalert2/dist/sweetalert2.min.css";
import ClientRoot from "@/components/ClientRoot";

export const metadata: Metadata = {
  title: "Fundraising Platform",
  description: "Help students raise funds for education and achievements.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <ClientRoot>{children}</ClientRoot>
      </body>
    </html>
  );
}
