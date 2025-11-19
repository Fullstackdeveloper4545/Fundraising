"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import Link from "next/link";
import { PASSWORD_MAX_BYTES, truncatePassword } from "@/lib/password";

export default function SignUpPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [form, setForm] = useState({ email: "", password: "", first_name: "", last_name: "", role: "student" as "student" | "donor" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { password: safePassword, truncated } = truncatePassword(form.password);
      if (truncated) {
        setError("Password was longer than 72 bytes and has been truncated for compatibility.");
      }
      await register({ ...form, password: safePassword });
      router.push("/signin");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-md">
      <h1 className="mb-6 text-2xl font-semibold">Create an account</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm">I am a</label>
          <div className="space-y-2">
            <label className="flex cursor-pointer items-center gap-2 rounded border p-3">
              <input type="radio" name="role" value="student" checked={form.role === "student"} onChange={() => setForm({ ...form, role: "student" })} />
              <div>
                <div className="font-medium">Student</div>
                <div className="text-xs text-gray-500">Create campaigns and learn</div>
              </div>
            </label>
            <label className="flex cursor-pointer items-center gap-2 rounded border p-3">
              <input type="radio" name="role" value="donor" checked={form.role === "donor"} onChange={() => setForm({ ...form, role: "donor" })} />
              <div>
                <div className="font-medium">Donor</div>
                <div className="text-xs text-gray-500">Support students</div>
              </div>
            </label>
          </div>
          <p className="mt-2 text-xs text-gray-500">Note: Donor is a regular user who donates; Student can create campaigns.</p>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="mb-1 block text-sm">First name</label>
            <input className="w-full rounded border px-3 py-2" required value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
          </div>
          <div>
            <label className="mb-1 block text-sm">Last name</label>
            <input className="w-full rounded border px-3 py-2" required value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
          </div>
        </div>
        <div>
          <label className="mb-1 block text-sm">Email</label>
          <input type="email" className="w-full rounded border px-3 py-2" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </div>
        <div>
          <label className="mb-1 block text-sm">Password</label>
          <input type="password" maxLength={PASSWORD_MAX_BYTES} className="w-full rounded border px-3 py-2" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <p className="mt-1 text-xs text-gray-500">Passwords are limited to {PASSWORD_MAX_BYTES} bytes for security compatibility.</p>
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button disabled={loading} className="w-full rounded bg-gray-900 px-4 py-2 text-white disabled:opacity-50">{loading ? "Creating..." : "Sign up"}</button>
      </form>
      <p className="mt-3 text-sm text-gray-600">Already have an account? <a href="/signin" className="underline">Sign in</a></p>
      <div className="mt-4 rounded border p-4 bg-gray-50">
        <h2 className="mb-2 text-sm font-semibold">Didn’t receive a verification email?</h2>
        <p className="text-xs text-gray-600">After signing up, check your inbox for a verification token. You can verify it later on the <Link href="/signin" className="underline">Sign in</Link> page.</p>
      </div>
    </div>
  );
}


