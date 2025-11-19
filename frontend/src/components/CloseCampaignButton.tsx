"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { AdminAPI } from "@/lib/api";

export default function CloseCampaignButton({ campaignId }: { campaignId: number }) {
  const { user, token } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!user || user.role !== "admin") return null;

  const onClick = async () => {
    setError(null);
    setLoading(true);
    try {
      await AdminAPI.closeCampaign(campaignId, token as string);
      router.refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to close campaign");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-2">
      <button onClick={onClick} disabled={loading} className="inline-block rounded bg-red-600 px-4 py-2 text-white disabled:opacity-50">
        {loading ? "Closing..." : "Close Campaign"}
      </button>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  );
}


