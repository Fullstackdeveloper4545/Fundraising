import type { Payment, User } from "@/types/api";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "https://srv1133545.hstgr.cloud/api/v1";

export type HttpMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";

async function getErrorMessage(res: Response): Promise<string> {
  const jsonData = await res.clone().json().catch(() => undefined);
  const jsonMessage = extractErrorText(jsonData);
  if (jsonMessage) {
    return jsonMessage;
  }
  if (jsonData && typeof jsonData === "object") {
    return JSON.stringify(jsonData);
  }
  if (typeof jsonData === "string") {
    return jsonData;
  }

  const raw = await res.text().catch(() => "");
  if (raw) {
    return raw;
  }
  return formatStatusMessage(res);
}

function extractErrorText(value: unknown): string | undefined {
  if (!value) {
    return undefined;
  }
  if (typeof value === "string") {
    return value;
  }
  if (Array.isArray(value)) {
    const parts = value
      .map((item) => extractErrorText(item))
      .filter((item): item is string => Boolean(item));
    if (parts.length) {
      return parts.join(", ");
    }
    return undefined;
  }
  if (typeof value === "object" && value !== null) {
    const record = value as Record<string, unknown>;
    const prioritizedKeys = ["detail", "message", "msg", "error"];
    for (const key of prioritizedKeys) {
      if (key in record) {
        const text = extractErrorText(record[key]);
        if (text) {
          return text;
        }
      }
    }
    const fallbackValue = Object.values(record)
      .map((val) => extractErrorText(val))
      .filter((val): val is string => Boolean(val))[0];
    if (fallbackValue) {
      return fallbackValue;
    }
  }
  return undefined;
}

function formatStatusMessage(res: Response): string {
  const base = `Request failed: ${res.status}`;
  return res.statusText ? `${base} ${res.statusText}` : base;
}

export async function apiFetch<T>(
  path: string,
  options: {
    method?: HttpMethod;
    body?: unknown;
    token?: string | null;
    headers?: Record<string, string>;
    cache?: RequestCache;
  } = {}
): Promise<T> {
  const { method = "GET", body, token, headers = {}, cache = "no-store" } = options;
  const url = `${API_BASE_URL}${path}`;
  const finalHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    ...headers,
  };
  if (token) {
    finalHeaders.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(url, {
    method,
    headers: finalHeaders,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    cache,
  });

  if (!res.ok) {
    throw new Error(await getErrorMessage(res));
  }
  const contentType = res.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return (await res.json()) as T;
  }
  return undefined as T;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export const AuthAPI = {
  register: (data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    phone?: string;
    referral_code?: string;
  }) => apiFetch<{ id: number; email: string }>(`/auth/register`, { method: "POST", body: data }),
  login: (data: { email: string; password: string }) =>
    apiFetch<LoginResponse>(`/auth/login`, { method: "POST", body: data }),
  me: (token: string) => apiFetch(`/auth/me`, { token }),
};

export interface CampaignPayload {
  title: string;
  description: string;
  goal_amount: number;
  duration_months: "1" | "3" | "6" | "12";
  category?: string;
  image_url?: string;
  video_url?: string;
  story?: string;
}

export type CampaignUpdatePayload = Partial<CampaignPayload>;

export const CampaignAPI = {
  list: (params?: { status?: string; featured?: boolean; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.status) query.set("status", params.status);
    if (params?.featured !== undefined) query.set("featured", String(params.featured));
    if (params?.limit) query.set("limit", String(params.limit));
    const qs = query.toString();
    return apiFetch(`/campaigns${qs ? `?${qs}` : ""}`);
  },
  featured: (limit?: number) => {
    const query = new URLSearchParams();
    if (limit) query.set("limit", String(limit));
    const qs = query.toString();
    return apiFetch(`/campaigns/featured${qs ? `?${qs}` : ""}`);
  },
  spotlight: (limit?: number) => {
    const query = new URLSearchParams();
    if (limit) query.set("limit", String(limit));
    const qs = query.toString();
    return apiFetch(`/campaigns/spotlight${qs ? `?${qs}` : ""}`);
  },
  get: (id: string | number) => apiFetch(`/campaigns/${id}`),
  create: (data: CampaignPayload, token: string) =>
    apiFetch(`/campaigns/`, { method: "POST", body: data, token }),
  createWithImage: (formData: FormData, token: string) => {
    const url = `${API_BASE_URL}/campaigns/with-image`;
    return fetch(url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
      body: formData,
    }).then(async (res) => {
      if (!res.ok) {
        throw new Error(await getErrorMessage(res));
      }
      return res.json();
    });
  },
  update: (id: string | number, data: CampaignUpdatePayload, token: string) =>
    apiFetch(`/campaigns/${id}`, { method: "PUT", body: data, token }),
  delete: (id: string | number, token: string) => 
    apiFetch(`/campaigns/${id}`, { method: "DELETE", token }),
};

export const PaymentAPI = {
  donate: (
    data: {
      campaign_id: number;
      donor_email: string;
      donor_name?: string;
      amount: number;
      method: "credit_card" | "paypal" | "bank_transfer" | "square";
      is_anonymous?: boolean;
      message?: string;
    },
    token?: string | null
  ) => apiFetch<Payment>(`/payments/`, { method: "POST", body: data, token: token || null }),
  forCampaign: (campaignId: number) => apiFetch<Payment[]>(`/payments/campaign/${campaignId}`),
  forUser: (userId: number, token: string) => apiFetch<Payment[]>(`/payments/user/${userId}`, { token }),
};

export const ReferralAPI = {
  stats: (campaignId: number, token: string) => apiFetch(`/referrals/stats/${campaignId}`, { token }),
};

export const MilestoneAPI = {
  forCampaign: (campaignId: number) => apiFetch(`/milestones/campaign/${campaignId}`),
};

export const ShoutoutAPI = {
  forCampaign: (campaignId: number) => apiFetch(`/shoutouts/campaign/${campaignId}`),
};

export const AdminAPI = {
  closeCampaign: (campaignId: number, token: string) =>
    apiFetch(`/admin/campaigns/${campaignId}/close`, { method: "POST", token }),
  setCampaignStatus: (campaignId: number, status: "draft" | "active" | "paused" | "completed" | "cancelled" | "expired", token: string) =>
    apiFetch(`/admin/campaigns/${campaignId}/status/${status}`, { method: "POST", token }),
};

export const PartnershipAPI = {
  request: (data: {
    company: string;
    contact: string;
    email: string;
    message?: string;
  }) => apiFetch(`/partnership/request`, { method: "POST", body: data }),
};
