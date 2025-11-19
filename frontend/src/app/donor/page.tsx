import { PaymentAPI } from "@/lib/api";
import { cookies } from "next/headers";
import type { Payment } from "@/types/api";

interface AuthCookieData {
  token: string;
  user: { id: number };
}

export default async function DonorDashboard() {
  const cookieStore = await cookies();
  const authCookie = cookieStore.get("auth");
  let payments: Payment[] = [];
  let isAuthenticated = false;

  if (authCookie?.value) {
    try {
      const parsed = JSON.parse(authCookie.value) as AuthCookieData;
      if (parsed.token && parsed.user?.id) {
        isAuthenticated = true;
        payments = await PaymentAPI.forUser(parsed.user.id, parsed.token);
      }
    } catch (error) {
      console.error("Failed to read donor auth cookie", error);
    }
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Your Donations</h1>
      <div className="rounded border p-4">
        {!isAuthenticated ? (
          <p className="text-gray-600">Sign in to view your donations.</p>
        ) : payments.length === 0 ? (
          <p className="text-gray-600">You haven&apos;t made any donations yet.</p>
        ) : (
          <ul className="divide-y">
            {payments.map((payment) => (
              <li key={payment.id} className="flex items-center justify-between py-3 text-sm">
                <span className="truncate">Campaign #{payment.campaign_id}</span>
                <span>${payment.amount.toLocaleString()}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}


