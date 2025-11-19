"use client";
import React, { Suspense, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";

function VerifyEmailContent() {
  const search = useSearchParams();
  const router = useRouter();
  const email = search.get("email") || "";
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg(null);
    setError(null);
    setLoading(true);
    try {
      await apiFetch(`/auth/verify-otp`, { method: "POST", body: { email, otp_code: token, purpose: "email_verification" } });
      setMsg("Email verified successfully.");
      // Redirect to sign-in and prefill email so user can log in immediately
      setTimeout(() => router.push(`/signin?email=${encodeURIComponent(email)}`), 1000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Verification failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-md">
      <h1 className="mb-2 text-2xl font-semibold">Verify your email</h1>
      {email && <p className="mb-4 text-sm text-gray-600">We sent a code to {email}.</p>}
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm">Verification token</label>
          <input className="w-full rounded border px-3 py-2" placeholder="Paste token" value={token} onChange={(e) => setToken(e.target.value)} />
        </div>
        {msg && <p className="text-sm text-green-600">{msg}</p>}
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button disabled={loading} className="w-full rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50">{loading ? "Verifying..." : "Verify"}</button>
      </form>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center text-muted">Loading verify form...</div>}>
      <VerifyEmailContent />
    </Suspense>
  );
}

