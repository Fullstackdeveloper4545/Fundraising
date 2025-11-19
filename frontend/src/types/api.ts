export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: "student" | "admin" | "company" | "donor";
  is_verified?: boolean;
  status?: "active" | "inactive" | "suspended" | "banned" | string;
  // Student-specific fields
  student_id?: string;
  class?: string;
  academic_results?: string;
  phone?: string;
  address?: string;
  date_of_birth?: string;
  emergency_contact?: string;
  emergency_phone?: string;
}

export interface Campaign {
  id: number;
  user_id: number;
  title: string;
  description: string;
  goal_amount: number;
  current_amount: number;
  status: string;
  duration_months: "1" | "3" | "6" | "12";
  start_date?: string;
  end_date?: string;
  category?: string;
  image_url?: string;
  video_url?: string;
  story?: string;
  is_featured: boolean;
  referral_requirement_met: boolean;
  referral_count?: number;
  created_at: string;
  updated_at: string;
  progress_percentage: number;
  days_remaining?: number;
  donor_count: number;
}

export interface Payment {
  id: number;
  campaign_id: number;
  donor_email: string;
  donor_name?: string;
  amount: number;
  method: "credit_card" | "paypal" | "bank_transfer" | "square";
  status: string;
  transaction_id?: string;
  is_anonymous: boolean;
  message?: string;
  created_at: string;
  processed_at?: string;
}

export interface Milestone {
  id: number;
  campaign_id: number;
  title: string;
  threshold_amount: number;
  achieved_at?: string;
  is_auto: boolean;
  created_at: string;
  is_achieved: boolean;
}

export interface Shoutout {
  id: number;
  campaign_id: number;
  donor_id?: number;
  display_name: string;
  message: string;
  visible: boolean;
  created_at: string;
}


