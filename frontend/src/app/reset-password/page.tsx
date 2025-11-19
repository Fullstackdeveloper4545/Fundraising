"use client";
import React, { Suspense, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { truncatePassword } from "@/lib/password";

function ResetPasswordContent() {
  const params = useSearchParams();
  const router = useRouter();
  const token = params.get("token") || "";
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setError(null);
    const safePassword = truncatePassword(password);
    const safeConfirm = truncatePassword(confirm);
    if (safePassword.password !== safeConfirm.password) {
      setError("Passwords do not match");
      return;
    }
    if (safePassword.truncated || safeConfirm.truncated) {
      setError("Password exceeded 72-byte security limit and was truncated for compatibility.");
    }
    setLoading(true);
    try {
      await apiFetch(`/auth/reset-password`, {
        method: "POST",
        body: { token, new_password: safePassword.password },
      });
      setMessage("Password reset successfully. You can now sign in.");
      setTimeout(() => router.push("/signin"), 1500);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to reset password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-md">
      <h1 className="mb-6 text-2xl font-semibold">Reset password</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm">New password</label>
          <input type="password" className="w-full rounded border px-3 py-2" required value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <div>
          <label className="mb-1 block text-sm">Confirm password</label>
          <input type="password" className="w-full rounded border px-3 py-2" required value={confirm} onChange={(e) => setConfirm(e.target.value)} />
        </div>
        {message && <p className="text-sm text-green-600">{message}</p>}
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button disabled={loading} className="w-full rounded bg-gray-900 px-4 py-2 text-white disabled:opacity-50">{loading ? "Resetting..." : "Reset password"}</button>
      </form>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center text-muted">Loading reset form...</div>}>
      <ResetPasswordContent />
    </Suspense>
  );
}

