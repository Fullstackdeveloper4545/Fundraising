"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";

export default function ResetPasswordOtpPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setError(null);
    if (password !== confirm) {
      setError("Passwords do not match");
      return;
    }
    setLoading(true);
    try {
      await apiFetch(`/auth/reset-password-otp`, {
        method: "POST",
        body: { email, otp_code: otp, new_password: password },
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
      <h1 className="mb-6 text-2xl font-semibold">Reset password via OTP</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm">Email</label>
          <input type="email" className="w-full rounded border px-3 py-2" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div>
          <label className="mb-1 block text-sm">OTP code</label>
          <input type="text" className="w-full rounded border px-3 py-2" required value={otp} onChange={(e) => setOtp(e.target.value)} />
        </div>
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


