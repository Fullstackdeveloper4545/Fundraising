"use client";
import React, { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { apiFetch } from "@/lib/api";

function SignInContent() {
  const router = useRouter();
  const search = useSearchParams();
  const preset = search.get("as");
  const { login, user } = useAuth();
  const [form, setForm] = useState({ email: preset === "admin" ? "admin@fundraising.com" : "", password: preset === "admin" ? "Admin@12345" : "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [verifying, setVerifying] = useState(false);
  const [verifyToken, setVerifyToken] = useState("");
  const [verifyMsg, setVerifyMsg] = useState<string | null>(null);
  const showVerify = (user && user.is_verified === false) || (!!error && error.toLowerCase().includes("verify your email"));
  // email verification UI removed per request

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(form.email, form.password);
      router.push("/");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Sign in failed";
      setError(msg);
      // If backend says to verify email, auto resend code and redirect to verify page
      if (msg.toLowerCase().includes("verify your email")) {
        try {
          await apiFetch(`/auth/resend-verification`, { method: "POST", body: { email: form.email } });
        } catch {}
        router.push(`/verify-email?email=${encodeURIComponent(form.email)}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const onVerifyEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setVerifyMsg(null);
    setError(null);
    setVerifying(true);
    try {
      await apiFetch(`/auth/verify-otp`, {
        method: "POST",
        body: { email: form.email, otp_code: verifyToken, purpose: "email_verification" },
      });
      setVerifyMsg("Email verified successfully. You can now use all features.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Verification failed");
    } finally {
      setVerifying(false);
    }
  };

  // removed verify flow handler

  return (
    <div className="mx-auto w-full max-w-md">
      <h1 className="mb-6 text-2xl font-semibold">Sign in</h1>
      {preset && <p className="mb-2 text-sm text-muted">Signing in as {preset}.</p>}
      <form onSubmit={onSubmit} className="space-y-4">
        
        <div>
          <label className="mb-1 block text-sm">Email</label>
          <input type="email" className="w-full rounded border px-3 py-2" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </div>
        <div>
          <label className="mb-1 block text-sm">Password</label>
          <input type="password" className="w-full rounded border px-3 py-2" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </div>
        {error && <p className="text-sm text-error">{error}</p>}
        <button disabled={loading} className="btn-primary w-full disabled:opacity-50">{loading ? "Signing in..." : "Sign in"}</button>
      </form>
      {showVerify && (
        <div className="mt-6 rounded border p-4">
          <h2 className="mb-2 text-sm font-semibold">Verify your email</h2>
          <form onSubmit={onVerifyEmail} className="space-y-3">
            <input
              className="w-full rounded border px-3 py-2"
              placeholder="Paste verification token"
              value={verifyToken}
              onChange={(e) => setVerifyToken(e.target.value)}
            />
            {verifyMsg && <p className="text-sm text-success">{verifyMsg}</p>}
            <button disabled={verifying} className="btn-primary w-full disabled:opacity-50">{verifying ? "Verifying..." : "Verify Email"}</button>
          </form>
          <p className="mt-2 text-xs text-muted">Use the token sent to your email during sign up.</p>
        </div>
      )}
      {/* email verification UI removed per request */}
      <div className="mt-3 flex items-center justify-between text-sm text-muted">
        <div className="flex gap-3">
          <a href="/forgot-password" className="underline">Forgot password?</a>
          <a href="/forgot-password-otp" className="underline">Forgot via OTP?</a>
        </div>
        <span>
          No account? <a href="/signup" className="underline">Create one</a>
        </span>
      </div>
    </div>
  );
}

export default function SignInPage() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center text-muted">Loading sign in...</div>}>
      <SignInContent />
    </Suspense>
  );
}


