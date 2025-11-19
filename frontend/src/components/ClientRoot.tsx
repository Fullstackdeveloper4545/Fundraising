"use client";
import React from "react";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import NavBar from "@/components/NavBar";
import Link from "next/link";
import Footer from "@/components/Footer";
import { usePathname } from "next/navigation";

export default function ClientRoot({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isAdminPage = pathname?.startsWith('/admin');
  
  if (isAdminPage) {
    return (
      <AuthProvider>
        {children}
      </AuthProvider>
    );
  }
  
  return (
    <AuthProvider>
      <NavBar />
      <main className="mx-auto max-w-7xl px-4 py-8">
        <VerifiedBanner />
        {children}
      </main>
      <Footer />
    </AuthProvider>
  );
}

function VerifiedBanner() {
  const { user } = useAuth();
  if (!user || user.is_verified) return null;
  return (
    <div className="mb-6 rounded-md border border-yellow-300 bg-yellow-50 p-4 text-sm text-yellow-900">
      <div className="flex items-center justify-between gap-3">
        <div>
          Your email is not verified. Please verify to access all features.
        </div>
        <Link href="/signin" className="rounded bg-yellow-600 px-3 py-1 text-white hover:bg-yellow-700">Verify now</Link>
      </div>
    </div>
  );
}


