import { CampaignAPI, PaymentAPI, MilestoneAPI, ShoutoutAPI } from "@/lib/api";
import { use } from "react";
import type { Campaign, Payment, Milestone, Shoutout } from "@/types/api";
import DonateButton from "@/components/DonateButton";
import CloseCampaignButton from "@/components/CloseCampaignButton";

// Helper function to construct proper image URLs
function getImageUrl(imageUrl: string | null | undefined): string | null {
  if (!imageUrl) return null;
  
  // If it's already a full URL, return as is
  if (imageUrl.startsWith('http')) return imageUrl;
  
  // If it's a relative path, prepend the backend base URL
  if (imageUrl.startsWith('/uploads/')) {
    const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.replace('/api/v1', '') || 'http://0.0.0.0:8000';
    return `${backendUrl}${imageUrl}`;
  }
  
  return imageUrl;
}

interface Params {
  params: Promise<{ id: string }>;
}

interface CampaignDetailData {
  campaign: Campaign;
  payments: Payment[];
  milestones: Milestone[];
  shoutouts: Shoutout[];
}

async function getData(id: string): Promise<CampaignDetailData | null> {
  const [campaignResult, paymentsResult, milestonesResult, shoutoutsResult] = await Promise.allSettled([
    CampaignAPI.get(id),
    PaymentAPI.forCampaign(Number(id)),
    MilestoneAPI.forCampaign(Number(id)),
    ShoutoutAPI.forCampaign(Number(id)),
  ]);

  if (campaignResult.status !== "fulfilled") {
    console.error(`CampaignDetail: failed to load campaign ${id}`, campaignResult.reason);
    return null;
  }

  const payments = paymentsResult.status === "fulfilled" ? paymentsResult.value : [];
  const milestones = milestonesResult.status === "fulfilled" ? milestonesResult.value : [];
  const shoutouts = shoutoutsResult.status === "fulfilled" ? shoutoutsResult.value : [];

  if (paymentsResult.status === "rejected") {
    console.error(`CampaignDetail: failed to load payments for campaign ${id}`, paymentsResult.reason);
  }
  if (milestonesResult.status === "rejected") {
    console.error(`CampaignDetail: failed to load milestones for campaign ${id}`, milestonesResult.reason);
  }
  if (shoutoutsResult.status === "rejected") {
    console.error(`CampaignDetail: failed to load shoutouts for campaign ${id}`, shoutoutsResult.reason);
  }

  return {
    campaign: campaignResult.value as Campaign,
    payments: payments as Payment[],
    milestones: milestones as Milestone[],
    shoutouts: shoutouts as Shoutout[],
  };
}

export default function CampaignDetailPage({ params }: Params) {
  const { id } = use(params);
  return <CampaignDetail id={id} />;
}

async function CampaignDetail({ id }: { id: string }) {
  const data = await getData(id);
  if (!data) {
    return (
      <div className="rounded border p-6 text-center text-gray-600">
        Unable to load this campaign right now. Please try again later.
      </div>
    );
  }
  const { campaign, payments, milestones, shoutouts } = data;
  return (
    <div className="space-y-8">
      <div className="grid gap-6 md:grid-cols-2">
        <div>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          {campaign.image_url ? <img alt="" src={getImageUrl(campaign.image_url) || ''} className="mb-3 w-full rounded" /> : <div className="mb-3 h-64 w-full rounded bg-gray-100" />}
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-3xl font-bold">{campaign.title}</h1>
            <span
              className={`px-2 py-0.5 text-xs font-semibold rounded-full capitalize ${
                campaign.status === "active"
                  ? "bg-green-100 text-green-800"
                  : campaign.status === "paused"
                  ? "bg-yellow-100 text-yellow-800"
                  : campaign.status === "completed"
                  ? "bg-blue-100 text-blue-800"
                  : campaign.status === "cancelled"
                  ? "bg-red-100 text-red-800"
                  : campaign.status === "expired"
                  ? "bg-gray-200 text-gray-700"
                  : "bg-gray-100 text-gray-800"
              }`}
            >
              {campaign.status}
            </span>
          </div>
          <p className="mt-2 text-gray-700">{campaign.description}</p>
          {campaign.story && <p className="mt-4 whitespace-pre-line text-gray-700">{campaign.story}</p>}
        </div>
        <div className="space-y-4">
          <div className="rounded border p-4">
            <div className="mb-2 flex items-center justify-between text-sm text-gray-600">
              <span>${'{'}campaign.current_amount{'}'} raised</span>
              <span>Goal ${'{'}campaign.goal_amount{'}'}</span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded bg-gray-200">
              <div className="h-full bg-green-600" style={{ width: `${'{'}Math.min(100, campaign.progress_percentage){'}'}%` }} />
            </div>
            <div className="mt-3 text-sm text-gray-600">{campaign.donor_count} donors • {campaign.days_remaining ?? 0} days remaining</div>
            {campaign.status === "active" ? (
              <DonateButton campaignId={campaign.id} />
            ) : (
              <div className="mt-2 text-sm text-gray-500">Donations are unavailable while the campaign is {campaign.status}.</div>
            )}
            <CloseCampaignButton campaignId={campaign.id} />
          </div>
          <div className="rounded border p-4">
            <h2 className="mb-3 text-lg font-semibold">Recent donations</h2>
            <ul className="space-y-2">
              {payments.slice(0, 6).map((p: Payment) => (
                <li key={p.id} className="flex items-center justify-between text-sm">
                  <span className="truncate">{p.is_anonymous ? "Anonymous" : (p.donor_name || p.donor_email)}</span>
                  <span>${'{'}p.amount{'}'}</span>
                </li>
              ))}
              {payments.length === 0 && <li className="text-sm text-gray-500">No donations yet.</li>}
            </ul>
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded border p-4">
          <h2 className="mb-3 text-lg font-semibold">Milestones</h2>
          {Array.isArray(milestones) && milestones.length > 0 ? (
            <ul className="space-y-2">
              {milestones.map((m: Milestone) => (
                <li key={m.id} className="flex items-center justify-between text-sm">
                  <span className="truncate">{m.title}</span>
                  <span>${'{'}m.threshold_amount{'}'}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">No milestones yet.</p>
          )}
        </div>
        <div className="rounded border p-4">
          <h2 className="mb-3 text-lg font-semibold">Donor shout-outs</h2>
          {Array.isArray(shoutouts) && shoutouts.length > 0 ? (
            <ul className="space-y-2">
              {shoutouts.map((s: Shoutout) => (
                <li key={s.id} className="text-sm">
                  <span className="font-medium">{s.display_name}</span>: {s.message}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">No shout-outs yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}


