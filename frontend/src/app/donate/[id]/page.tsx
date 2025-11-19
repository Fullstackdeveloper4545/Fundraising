"use client";
import React, { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { PaymentAPI } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function DonatePage() {
  const router = useRouter();
  const routeParams = useParams<{ id: string }>();
  const id = routeParams?.id as string;
  const { user, token } = useAuth();
  const [form, setForm] = useState({
    donor_email: user?.email || "",
    donor_name: "",
    amount: 25,
    method: "credit_card" as "credit_card" | "paypal" | "bank_transfer" | "square",
    is_anonymous: false,
    message: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const isStudent = user?.role === "student";

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await PaymentAPI.donate({
        campaign_id: Number(id),
        donor_email: form.donor_email,
        donor_name: form.donor_name || undefined,
        amount: Number(form.amount),
        method: form.method,
        is_anonymous: form.is_anonymous,
        message: form.message || undefined,
      }, token);
      router.push(`/campaign/${id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Donation failed");
    } finally {
      setLoading(false);
    }
  };

  if (isStudent) {
    return (
      <div className="mx-auto w-full max-w-md">
        <h1 className="mb-6 text-2xl font-semibold">Donations not available</h1>
        <p className="text-sm text-gray-600">Student accounts cannot donate. Please use a donor account.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-md">
      <h1 className="mb-6 text-2xl font-semibold">Donate to campaign #{id}</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm">Your email</label>
          <input type="email" className="w-full rounded border px-3 py-2" required value={form.donor_email} onChange={(e) => setForm({ ...form, donor_email: e.target.value })} />
        </div>
        <div>
          <label className="mb-1 block text-sm">Display name (optional)</label>
          <input className="w-full rounded border px-3 py-2" value={form.donor_name} onChange={(e) => setForm({ ...form, donor_name: e.target.value })} />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm">Amount ($)</label>
            <input type="number" min={1} className="w-full rounded border px-3 py-2" value={form.amount} onChange={(e) => setForm({ ...form, amount: Number(e.target.value) })} />
          </div>
          <div>
            <label className="mb-1 block text-sm">Method</label>
            <select className="w-full rounded border px-3 py-2" value={form.method} onChange={(e) => setForm({ ...form, method: e.target.value as "credit_card" | "paypal" | "bank_transfer" | "square" })}>
              <option value="credit_card">Credit card</option>
              <option value="paypal">PayPal</option>
              <option value="bank_transfer">Bank transfer</option>
              <option value="square">Square</option>
            </select>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <input id="anon" type="checkbox" checked={form.is_anonymous} onChange={(e) => setForm({ ...form, is_anonymous: e.target.checked })} />
          <label htmlFor="anon" className="text-sm">Donate anonymously</label>
        </div>
        <div>
          <label className="mb-1 block text-sm">Message (optional)</label>
          <textarea className="w-full rounded border px-3 py-2" rows={3} value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} />
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button disabled={loading} className="w-full rounded bg-gray-900 px-4 py-2 text-white disabled:opacity-50">{loading ? "Processing..." : "Donate"}</button>
      </form>
    </div>
  );
}


