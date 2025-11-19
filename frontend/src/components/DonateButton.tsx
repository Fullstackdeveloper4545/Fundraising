"use client";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";

export default function DonateButton({ campaignId }: { campaignId: number }) {
  const { user } = useAuth();
  if (!user || user.role !== "donor") {
    return null;
  }
  return (
    <Link href={`/donate/${campaignId}`} className="mt-4 inline-block rounded bg-gray-900 px-4 py-2 text-white">
      Donate
    </Link>
  );
}


