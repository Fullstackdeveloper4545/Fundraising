"use client";
import React, { useEffect, useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch, CampaignAPI } from "@/lib/api";
import type { Campaign, User } from "@/types/api";
import { useAuth } from "@/context/AuthContext";
import Swal from "sweetalert2";
import StudentProfileModal from "@/components/StudentProfileModal";
import AdminSidebar from "@/components/AdminSidebar";

interface PlatformStats {
  total_users: number;
  total_campaigns: number;
  total_donations: number;
  active_campaigns: number;
}

const CAMPAIGN_STATUSES = ['draft','active','paused','completed','cancelled','expired'] as const;
type CampaignStatus = typeof CAMPAIGN_STATUSES[number];
type DurationOption = "1" | "3" | "6" | "12";

interface CreateFormState {
  title: string;
  description: string;
  goal_amount: number;
  duration_months: DurationOption;
  category: string;
  image_url: string;
  video_url: string;
  story: string;
}

export default function AdminDashboard() {
  const { token, user, logout } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'campaigns' | 'users'>('overview');
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<User | null>(null);
  const [showStudentProfile, setShowStudentProfile] = useState(false);
  const [showStudentForm, setShowStudentForm] = useState(false);
  const [editingStudent, setEditingStudent] = useState<User | null>(null);
  const [studentForm, setStudentForm] = useState({
    student_id: "",
    class: "",
    academic_results: "",
    phone: "",
    address: "",
    date_of_birth: "",
    emergency_contact: "",
    emergency_phone: "",
  });
  const [createForm, setCreateForm] = useState<CreateFormState>({
    title: "",
    description: "",
    goal_amount: 1000,
    duration_months: "3",
    category: "",
    image_url: "",
    video_url: "",
    story: "",
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  // removed local modal state in favor of SweetAlert2

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setCreateForm({ ...createForm, image_url: "" }); // Clear URL when file is selected
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const loadData = useCallback(async () => {
    if (!token) {
      return;
    }
    try {
      setLoading(true);
      setError(null);
      console.log("Loading admin data...");
      const [statsData, campaignsData, usersData] = await Promise.all([
        apiFetch<PlatformStats>(`/admin/stats`, { token }),
        apiFetch<Campaign[]>(`/admin/campaigns`, { token }),
        apiFetch<User[]>(`/admin/users`, { token }),
      ]);
      
      console.log("Admin data loaded:", { statsData, campaignsData, usersData });
      
      setStats(statsData);
      setCampaigns(Array.isArray(campaignsData) ? campaignsData : []);
      setUsers(Array.isArray(usersData) ? usersData : []);
    } catch (e) {
      console.error("Error loading admin data:", e);
      setError(e instanceof Error ? e.message : "Failed to load admin data");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (!token || !user || user.role !== "admin") {
      router.push("/admin/login");
      return;
    }
    
    loadData();
  }, [token, user, router, loadData]);

  const handleFeatureCampaign = async (campaignId: number) => {
    try {
      await apiFetch(`/admin/campaigns/${campaignId}/feature`, { 
        method: "POST", 
        token 
      });
      // Reload campaigns to show updated status
      const campaignsData = await apiFetch<Campaign[]>(`/admin/campaigns`, { token });
      setCampaigns(Array.isArray(campaignsData) ? campaignsData : []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to feature campaign");
    }
  };

  const handleCloseCampaign = async (campaignId: number) => {
    try {
      await apiFetch(`/admin/campaigns/${campaignId}/close`, {
        method: "POST",
        token,
      });
      const campaignsData = await apiFetch<Campaign[]>(`/admin/campaigns`, { token });
      setCampaigns(Array.isArray(campaignsData) ? campaignsData : []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to close campaign");
    }
  };

  const handleCreateCampaign = async () => {
    try {
      console.log("Creating campaign:", createForm);
      
      // Create FormData for file upload
      const formData = new FormData();
      formData.append("title", createForm.title);
      formData.append("description", createForm.description);
      formData.append("goal_amount", createForm.goal_amount.toString());
      formData.append("duration_months", createForm.duration_months);
      formData.append("category", createForm.category);
      formData.append("story", createForm.story);
      formData.append("video_url", createForm.video_url);
      
      if (selectedFile) {
        formData.append("image_file", selectedFile);
      } else if (createForm.image_url) {
        formData.append("image_url", createForm.image_url);
      }
      
      // Use the improved API method
      const response = await CampaignAPI.createWithImage(formData, token as string);
      console.log("Campaign created successfully:", response);
      
      // Refresh all data
      const [statsData, campaignsData, usersData] = await Promise.all([
        apiFetch<PlatformStats>(`/admin/stats`, { token }),
        apiFetch<Campaign[]>(`/admin/campaigns`, { token }),
        apiFetch<User[]>(`/admin/users`, { token }),
      ]);
      
      setStats(statsData);
      setCampaigns(Array.isArray(campaignsData) ? campaignsData : []);
      setUsers(Array.isArray(usersData) ? usersData : []);
      
      setShowCreate(false);
      setCreateForm({ title: "", description: "", goal_amount: 1000, duration_months: "3", category: "", image_url: "", video_url: "", story: "" });
      setSelectedFile(null);
      setImagePreview(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
      
      // Show success message
      Swal.fire({
        title: 'Success!',
        text: 'Campaign created successfully in draft status',
        icon: 'success',
        timer: 2000,
        showConfirmButton: false,
      });
    } catch (e) {
      console.error("Error creating campaign:", e);
      setError(e instanceof Error ? e.message : "Failed to create campaign");
      
      // Show error message
      Swal.fire({
        title: 'Error!',
        text: e instanceof Error ? e.message : "Failed to create campaign",
        icon: 'error',
        timer: 3000,
        showConfirmButton: false,
      });
    }
  };

  const handleViewStudentProfile = (user: User) => {
    setSelectedStudent(user);
    setShowStudentProfile(true);
  };

  const handleStudentProfileConfirm = () => {
    // Here you can add additional logic for when the admin confirms viewing student details
    console.log("Admin confirmed viewing student profile:", selectedStudent);
  };

  const handleEditStudent = (user: User) => {
    setEditingStudent(user);
    setStudentForm({
      student_id: user.student_id || "",
      class: user.class || "",
      academic_results: user.academic_results || "",
      phone: user.phone || "",
      address: user.address || "",
      date_of_birth: user.date_of_birth || "",
      emergency_contact: user.emergency_contact || "",
      emergency_phone: user.emergency_phone || "",
    });
    setShowStudentForm(true);
  };

  const handleSaveStudentDetails = async () => {
    if (!editingStudent) return;
    
    try {
      // Map frontend field names to backend field names
      const backendData = {
        student_id: studentForm.student_id,
        class_name: studentForm.class, // Map 'class' to 'class_name' for backend
        academic_results: studentForm.academic_results,
        phone: studentForm.phone,
        address: studentForm.address,
        date_of_birth: studentForm.date_of_birth,
        emergency_contact: studentForm.emergency_contact,
        emergency_phone: studentForm.emergency_phone,
      };
      
      await apiFetch(`/admin/users/${editingStudent.id}`, {
        method: "PUT",
        token,
        body: backendData,
      });
      
      // Reload users to show updated data
      const usersData = await apiFetch<User[]>(`/admin/users`, { token });
      setUsers(Array.isArray(usersData) ? usersData : []);
      
      setShowStudentForm(false);
      setEditingStudent(null);
      setStudentForm({
        student_id: "",
        class: "",
        academic_results: "",
        phone: "",
        address: "",
        date_of_birth: "",
        emergency_contact: "",
        emergency_phone: "",
      });
      
      Swal.fire({
        title: 'Success!',
        text: 'Student details updated successfully.',
        icon: 'success',
        timer: 2000,
        showConfirmButton: false,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to update student details");
    }
  };

  const handleLogout = () => {
    logout();
    router.push("/admin/login");
  };

  const handleLogoutClick = () => {
    Swal.fire({
      title: 'Logout',
      text: 'Are you sure you want to log out?',
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Logout',
      cancelButtonText: 'Cancel',
      width: '520px',
      backdrop: `rgba(0,0,0,0.4)`,
      buttonsStyling: false,
      customClass: {
        popup: 'swal2-popup-custom',
        container: 'swal2-backdrop-blur',
        confirmButton: 'btn-primary',
        cancelButton: 'btn-outline'
      }
    }).then((result) => {
      if (result.isConfirmed) {
        handleLogout();
        Swal.fire({
          title: 'Logged out',
          icon: 'success',
          timer: 1400,
          showConfirmButton: false,
          width: '420px'
        });
      }
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <svg className="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="text-lg">Loading admin dashboard...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-lg mb-4">{error}</div>
          <button
            onClick={() => window.location.reload()}
            className="btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-[#00AFF0] h-screen flex flex-col">
        <AdminSidebar activeTab={activeTab} setActiveTab={setActiveTab} user={user ?? undefined} />
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col bg-white h-screen">
        {/* Top Header */}
        <div className="bg-white shadow-sm border-b border-gray-200">
          <div className="px-6 py-4">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-sm text-gray-600">Welcome back, {user?.first_name}</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => {
                  setLoading(true);
                  setError(null);
                  loadData();
                }}
                className="text-sm text-gray-600 hover:text-[#00AFF0] transition-colors"
                title="Refresh data"
              >
                🔄 Refresh
              </button>
              <Link
                href="/"
                  className="text-sm text-gray-600 hover:text-[#00AFF0] transition-colors"
              >
                View Site
              </Link>
              <button
                onClick={handleLogoutClick}
                  className="text-sm text-gray-600 hover:text-[#00AFF0] transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

        {/* Content */}
        <div className="flex-1 p-2 bg-white overflow-y-auto">
        {activeTab === 'overview' && (
          <div className="space-y-3 h-full">
            {/* Welcome Section */}
            <div className="bg-gradient-to-r from-[#00AFF0] to-[#0099D6] rounded-xl p-4 text-white shadow-lg">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold mb-1">Welcome back, {user?.first_name}!</h2>
                  <p className="text-white/90 text-sm">Here&apos;s what&apos;s happening with your platform today</p>
                </div>
                <div className="hidden md:block">
                  <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                    <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
              <div className="group bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
                <div className="p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Total Users</p>
                      <p className="text-3xl font-bold text-gray-900 mt-2">{stats?.total_users || 0}</p>
                    </div>
                    <div className="w-12 h-12 bg-gradient-to-br from-[#00AFF0] to-[#0099D6] rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-200">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                    </div>
                  </div>
                  <div className="mt-4 flex items-center text-sm text-green-600">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                    <span>+12% from last month</span>
                  </div>
                </div>
              </div>

              <div className="group bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
                <div className="p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Total Campaigns</p>
                      <p className="text-3xl font-bold text-gray-900 mt-2">{stats?.total_campaigns || 0}</p>
                    </div>
                    <div className="w-12 h-12 bg-gradient-to-br from-[#00AFF0] to-[#0099D6] rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-200">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </div>
                  </div>
                  <div className="mt-4 flex items-center text-sm text-green-600">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                    <span>+8% from last month</span>
                  </div>
                </div>
              </div>

              <div className="group bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
                <div className="p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Total Raised</p>
                      <p className="text-3xl font-bold text-gray-900 mt-2">${(stats?.total_donations || 0).toLocaleString()}</p>
                    </div>
                    <div className="w-12 h-12 bg-gradient-to-br from-[#00AFF0] to-[#0099D6] rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-200">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                      </svg>
                    </div>
                  </div>
                  <div className="mt-4 flex items-center text-sm text-green-600">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                    <span>+24% from last month</span>
                  </div>
                </div>
              </div>

              <div className="group bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
                <div className="p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Draft Campaigns</p>
                      <p className="text-3xl font-bold text-gray-900 mt-2">{campaigns.filter(c => c.status === 'draft').length}</p>
                    </div>
                    <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-200">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                  </div>
                  <div className="mt-4 flex items-center text-sm text-yellow-600">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>Pending approval</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-3">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="grid grid-cols-3 gap-2">
                <button 
                  onClick={() => setActiveTab('campaigns')}
                  className="flex items-center space-x-2 p-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                >
                  <div className="w-10 h-10 bg-[#00AFF0]/10 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-[#00AFF0]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  </div>
                  <div className="text-left">
                    <p className="font-medium text-gray-900">Create Campaign</p>
                    <p className="text-sm text-gray-500">Start a new fundraising campaign</p>
                  </div>
                </button>
                
                <button 
                  onClick={() => setActiveTab('users')}
                  className="flex items-center space-x-2 p-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                >
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                  <div className="text-left">
                    <p className="font-medium text-gray-900">Manage Users</p>
                    <p className="text-sm text-gray-500">View and manage user accounts</p>
                  </div>
                </button>
                
                <button className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
                  <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div className="text-left">
                    <p className="font-medium text-gray-900">View Reports</p>
                    <p className="text-sm text-gray-500">Analytics and insights</p>
                  </div>
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'campaigns' && (
          <div className="space-y-6">
            {/* Header Section */}
            <div className="bg-gradient-to-r from-[#00AFF0] to-[#0099D6] rounded-xl p-6 text-white shadow-lg">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl font-bold">Campaign Management</h3>
                  <p className="mt-1 text-white/90">Monitor and manage all fundraising campaigns</p>
                </div>
                <button 
                  onClick={() => setShowCreate(true)} 
                  className="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 backdrop-blur-sm border border-white/20"
                >
                  <svg className="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Create Campaign
                </button>
              </div>
            </div>

            {/* Pending Approval Campaigns Section */}
            {campaigns.filter(c => c.status === 'pending_approval').length > 0 && (
              <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold text-gray-900 flex items-center">
                    <span className="bg-orange-100 text-orange-800 px-3 py-1 rounded-full text-sm font-medium mr-3">
                      PENDING APPROVAL
                    </span>
                    Campaigns Awaiting Approval ({campaigns.filter(c => c.status === 'pending_approval').length})
                  </h3>
                </div>
                <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                  {campaigns.filter(c => c.status === 'pending_approval').map((campaign) => (
                    <div key={campaign.id} className="group bg-orange-50 border-2 border-orange-200 rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
                      {/* Campaign Header */}
                      <div className="p-6 pb-4">
                        <div className="flex items-start justify-between mb-3">
                          <h4 className="text-lg font-semibold text-gray-900 line-clamp-2 group-hover:text-blue-600 transition-colors">
                            {campaign.title}
                          </h4>
                          <span className="ml-3 px-3 py-1 text-xs font-semibold rounded-full whitespace-nowrap bg-orange-200 text-orange-800">
                            {campaign.status}
                          </span>
                        </div>
                        
                        {/* Campaign Stats */}
                        <div className="space-y-3">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Goal</span>
                            <span className="font-medium text-gray-900">${campaign.goal_amount.toLocaleString()}</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Duration</span>
                            <span className="font-medium text-gray-900">{campaign.duration_months} months</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Referrals</span>
                            <span className="font-medium text-gray-900">{(campaign.referral_count || 0)}/5</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Created</span>
                            <span className="font-medium text-gray-900">{new Date(campaign.created_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Action Buttons */}
                      <div className="px-6 py-4 bg-orange-100 border-t border-orange-200">
                        <div className="flex space-x-2">
                          <button
                            onClick={async () => {
                              try {
                                const response = await apiFetch(`/campaigns/${campaign.id}/approve`, { method: 'POST', token });
                                console.log("Campaign approved:", response);
                                
                                // Reload campaigns
                                const campaignsData = await apiFetch<Campaign[]>(`/admin/campaigns`, { token });
                                setCampaigns(Array.isArray(campaignsData) ? campaignsData : []);
                                
                                Swal.fire({
                                  title: 'Success!',
                                  text: `Campaign "${campaign.title}" has been approved and is now active`,
                                  icon: 'success',
                                  timer: 2000,
                                  showConfirmButton: false,
                                });
                              } catch (err) {
                                console.error("Error approving campaign:", err);
                                Swal.fire({
                                  title: 'Error!',
                                  text: err instanceof Error ? err.message : 'Failed to approve campaign',
                                  icon: 'error',
                                  timer: 3000,
                                  showConfirmButton: false,
                                });
                              }
                            }}
                            className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => setSelectedCampaign(campaign)}
                            className="flex-1 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                          >
                            View Details
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Draft Campaigns Section */}
            {campaigns.filter(c => c.status === 'draft').length > 0 && (
              <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold text-gray-900 flex items-center">
                    <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium mr-3">
                      DRAFT
                    </span>
                    Draft Campaigns ({campaigns.filter(c => c.status === 'draft').length})
                  </h3>
                </div>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                  {campaigns.filter(c => c.status === 'draft').map((campaign) => (
                    <div key={campaign.id} className="group bg-yellow-50 border-2 border-yellow-200 rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
                      {/* Campaign Header */}
                      <div className="p-6 pb-4">
                        <div className="flex items-start justify-between mb-3">
                          <h4 className="text-lg font-semibold text-gray-900 line-clamp-2 group-hover:text-blue-600 transition-colors">
                            {campaign.title}
                          </h4>
                          <span className="ml-3 px-3 py-1 text-xs font-semibold rounded-full whitespace-nowrap bg-yellow-200 text-yellow-800">
                            {campaign.status}
                          </span>
                        </div>
                        
                        {/* Campaign Stats */}
                        <div className="space-y-3">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Goal</span>
                            <span className="font-medium text-gray-900">${campaign.goal_amount.toLocaleString()}</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Duration</span>
                            <span className="font-medium text-gray-900">{campaign.duration_months} months</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Referrals</span>
                            <span className="font-medium text-gray-900">{(campaign.referral_count || 0)}/5</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Created</span>
                            <span className="font-medium text-gray-900">{new Date(campaign.created_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Action Buttons */}
                      <div className="px-6 py-4 bg-yellow-100 border-t border-yellow-200">
                        <div className="flex space-x-2">
                          <button
                            onClick={async () => {
                              try {
                                const response = await apiFetch(`/admin/campaigns/${campaign.id}/status/active`, { method: 'POST', token });
                                console.log("Campaign approved:", response);
                                
                                // Reload campaigns
                                const campaignsData = await apiFetch<Campaign[]>(`/admin/campaigns`, { token });
                                setCampaigns(Array.isArray(campaignsData) ? campaignsData : []);
                                
                                Swal.fire({
                                  title: 'Success!',
                                  text: `Campaign "${campaign.title}" has been approved and is now active`,
                                  icon: 'success',
                                  timer: 2000,
                                  showConfirmButton: false,
                                });
                              } catch (err) {
                                console.error("Error approving campaign:", err);
                                Swal.fire({
                                  title: 'Error!',
                                  text: err instanceof Error ? err.message : 'Failed to approve campaign',
                                  icon: 'error',
                                  timer: 3000,
                                  showConfirmButton: false,
                                });
                              }
                            }}
                            className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                          >
                            ✓ Approve Campaign
                          </button>
                          <button
                            onClick={async () => {
                              try {
                                const response = await apiFetch(`/admin/campaigns/${campaign.id}/status/cancelled`, { method: 'POST', token });
                                console.log("Campaign rejected:", response);
                                
                                // Reload campaigns
                                const campaignsData = await apiFetch<Campaign[]>(`/admin/campaigns`, { token });
                                setCampaigns(Array.isArray(campaignsData) ? campaignsData : []);
                                
                                Swal.fire({
                                  title: 'Campaign Rejected',
                                  text: `Campaign "${campaign.title}" has been rejected`,
                                  icon: 'info',
                                  timer: 2000,
                                  showConfirmButton: false,
                                });
                              } catch (err) {
                                console.error("Error rejecting campaign:", err);
                                Swal.fire({
                                  title: 'Error!',
                                  text: err instanceof Error ? err.message : 'Failed to reject campaign',
                                  icon: 'error',
                                  timer: 3000,
                                  showConfirmButton: false,
                                });
                              }
                            }}
                            className="flex-1 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                          >
                            ✗ Reject Campaign
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* All Campaigns Grid */}
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {campaigns.filter(c => c.status !== 'draft').map((campaign) => (
                <div key={campaign.id} className="group bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
                  {/* Campaign Header */}
                  <div className="p-6 pb-4">
                    <div className="flex items-start justify-between mb-3">
                      <h4 className="text-lg font-semibold text-gray-900 line-clamp-2 group-hover:text-blue-600 transition-colors">
                        {campaign.title}
                      </h4>
                      <span className={`ml-3 px-3 py-1 text-xs font-semibold rounded-full whitespace-nowrap ${
                        campaign.status === 'active' 
                          ? 'bg-green-100 text-green-800'
                          : campaign.status === 'paused'
                          ? 'bg-yellow-100 text-yellow-800'
                          : campaign.status === 'completed'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {campaign.status}
                      </span>
                    </div>
                    
                    {/* Campaign Stats */}
                    <div className="space-y-3">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Goal</span>
                        <span className="font-medium text-gray-900">${campaign.goal_amount.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Raised</span>
                        <span className="font-medium text-green-600">${campaign.current_amount.toLocaleString()}</span>
                      </div>
                      
                      {/* Progress Bar */}
                      <div className="space-y-2">
                        <div className="flex justify-between text-xs text-gray-500">
                          <span>Progress</span>
                          <span>{Math.round((campaign.current_amount / campaign.goal_amount) * 100)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-gradient-to-r from-[#00AFF0] to-[#0099D6] h-2 rounded-full transition-all duration-500"
                            style={{ width: `${Math.min(100, (campaign.current_amount / campaign.goal_amount) * 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Campaign Actions */}
                  <div className="px-6 py-4 bg-gray-50/50 border-t border-gray-200">
                    <div className="flex items-center justify-between">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleFeatureCampaign(campaign.id)}
                          className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all duration-200 ${
                            campaign.is_featured 
                              ? 'bg-blue-100 text-blue-700' 
                              : 'bg-gray-100 text-gray-700 hover:bg-blue-100 hover:text-blue-700'
                          }`}
                        >
                          {campaign.is_featured ? '⭐ Featured' : 'Feature'}
                        </button>
                        <button
                          onClick={() => setSelectedCampaign(campaign)}
                          className="text-xs bg-[#00AFF0] hover:bg-[#0099D6] text-white px-3 py-1.5 rounded-lg font-medium transition-all duration-200"
                          title="View campaign details"
                        >
                          View Details
                        </button>
                      </div>
                      <select
                        onChange={async (e) => {
                          const next = e.target.value as CampaignStatus;
                          console.log(`Updating campaign ${campaign.id} status to ${next}`);
                          try {
                            const response = await apiFetch(`/admin/campaigns/${campaign.id}/status/${next}`, { method: 'POST', token });
                            console.log("Status update response:", response);
                            
                            // Reload campaigns to show updated status
                            const campaignsData = await apiFetch<Campaign[]>(`/admin/campaigns`, { token });
                            console.log("Reloaded campaigns:", campaignsData);
                            setCampaigns(Array.isArray(campaignsData) ? campaignsData : []);
                            
                            // Show success message
                            Swal.fire({
                              title: 'Success!',
                              text: `Campaign status updated to ${next}`,
                              icon: 'success',
                              timer: 2000,
                              showConfirmButton: false,
                            });
                          } catch (err) {
                            console.error("Error updating campaign status:", err);
                            setError(err instanceof Error ? err.message : 'Failed to update status');
                            
                            // Show error message
                            Swal.fire({
                              title: 'Error!',
                              text: err instanceof Error ? err.message : 'Failed to update status',
                              icon: 'error',
                              timer: 3000,
                              showConfirmButton: false,
                            });
                          }
                        }}
                        value={campaign.status}
                        className="text-xs rounded-lg border border-gray-300 px-2 py-1 bg-white text-gray-700 hover:border-[#00AFF0] focus:outline-none focus:ring-2 focus:ring-[#00AFF0]/50 transition"
                        title="Set campaign status"
                      >
                        {CAMPAIGN_STATUSES.map((statusOption) => (
                          <option key={statusOption} value={statusOption}>{statusOption}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Empty State */}
            {campaigns.length === 0 && (
              <div className="text-center py-12">
                <div className="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No campaigns yet</h3>
                <p className="text-gray-500 mb-4">Get started by creating your first campaign</p>
                <button 
                  onClick={() => setShowCreate(true)} 
                  className="btn-primary"
                >
                  Create Campaign
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'users' && (
          <div className="space-y-6">
            {/* Header Section */}
            <div className="bg-gradient-to-r from-[#00AFF0] to-[#0099D6] rounded-xl p-6 text-white shadow-lg">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-2xl font-bold">User Management</h3>
                  <p className="mt-1 text-white/90">Manage user accounts and permissions</p>
                </div>
                <div className="bg-white/20 rounded-lg px-4 py-2 backdrop-blur-sm border border-white/20">
                  <span className="text-sm font-medium">{users.length} Total Users</span>
                </div>
              </div>
            </div>

            {/* Users Grid */}
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {users.map((user) => (
                <div key={user.id} className="group bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
                  {/* User Header */}
                  <div className="p-6 pb-4">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold text-lg shadow-lg">
                          {user.first_name?.[0]?.toUpperCase() || 'U'}
                        </div>
                        <div>
                          <h4 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                            {user.first_name} {user.last_name}
                          </h4>
                          <p className="text-sm text-gray-500 truncate max-w-[200px]">
                            {user.email}
                          </p>
                        </div>
                      </div>
                      <span className={`px-3 py-1 text-xs font-semibold rounded-full whitespace-nowrap ${
                        user.role === 'admin' 
                          ? 'bg-red-100 text-red-800'
                          : user.role === 'student'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {user.role}
                      </span>
                    </div>
                    
                    {/* User Stats */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600 flex items-center">
                          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Status
                        </span>
                        <span className={`font-medium ${
                          user.status === 'active' 
                            ? 'text-green-600' 
                            : 'text-gray-600'
                        }`}>
                          {user.status}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600 flex items-center">
                          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                          </svg>
                          Verification
                        </span>
                        <span className={`font-medium ${
                          user.is_verified 
                            ? 'text-green-600' 
                            : 'text-yellow-600'
                        }`}>
                          {user.is_verified ? 'Verified' : 'Pending'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* User Actions */}
                  <div className="px-6 py-4 bg-gray-50/50 border-t border-gray-200">
                    <div className="flex items-center justify-between">
                      <div className="flex gap-2">
                        <button 
                          onClick={() => handleViewStudentProfile(user)}
                          className="text-xs bg-[#00AFF0] hover:bg-[#0099D6] text-white px-3 py-1.5 rounded-lg font-medium transition-all duration-200"
                        >
                          View Profile
                        </button>
                        <button 
                          onClick={() => handleEditStudent(user)}
                          className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-lg font-medium transition-all duration-200"
                        >
                          Edit
                        </button>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${
                          user.status === 'active' ? 'bg-green-500' : 'bg-gray-400'
                        }`}></div>
                        <span className="text-xs text-gray-500">
                          {user.status === 'active' ? 'Online' : 'Offline'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Empty State */}
            {users.length === 0 && (
              <div className="text-center py-12">
                <div className="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                  <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No users found</h3>
                <p className="text-gray-500">Users will appear here once they register</p>
              </div>
            )}
          </div>
        )}
        </div>
      </div>
      
      {/* View Details Modal */}
      {selectedCampaign && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40" onClick={() => setSelectedCampaign(null)} />
          <div className="relative w-full max-w-lg rounded-lg bg-white shadow-lg border border-gray-100 p-6">
            <div className="flex items-start justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Campaign Details</h2>
              <button onClick={() => setSelectedCampaign(null)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>
            <div className="mt-4 space-y-2">
              <DetailRow label="Title" value={selectedCampaign.title} />
              <DetailRow label="Status" value={<span className="capitalize">{selectedCampaign.status}</span>} />
              <DetailRow label="Description" value={<span className="whitespace-pre-wrap">{selectedCampaign.description}</span>} />
              <DetailRow label="Goal Amount" value={`$${selectedCampaign.goal_amount.toLocaleString()}`} />
              <DetailRow label="Received Amount" value={`$${selectedCampaign.current_amount.toLocaleString()}`} />
              <DetailRow label="Story" value={<span className="whitespace-pre-wrap">{selectedCampaign.story || '-'}</span>} />
              <DetailRow label="Start Date" value={selectedCampaign.start_date ? new Date(selectedCampaign.start_date).toLocaleDateString() : '-'} />
              <DetailRow label="End Date" value={selectedCampaign.end_date ? new Date(selectedCampaign.end_date).toLocaleDateString() : '-'} />
            </div>
            <div className="mt-6 flex justify-end">
              <button onClick={() => setSelectedCampaign(null)} className="btn-primary text-sm px-4 py-2">Close</button>
            </div>
          </div>
        </div>
      )}

      {/* Create Campaign Modal */}
      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40" onClick={() => setShowCreate(false)} />
          <div className="relative w-full max-w-lg rounded-lg bg-white shadow-lg border border-gray-100 p-6">
            <div className="flex items-start justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Create New Campaign</h2>
              <button onClick={() => setShowCreate(false)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>
            <div className="mt-4 grid gap-3">
              <input className="rounded border border-gray-300 bg-white px-3 py-2 text-sm" placeholder="Title" value={createForm.title} onChange={e => setCreateForm({ ...createForm, title: e.target.value })} />
              <textarea className="rounded border border-gray-300 bg-white px-3 py-2 text-sm" placeholder="Description" rows={3} value={createForm.description} onChange={e => setCreateForm({ ...createForm, description: e.target.value })} />
              <textarea className="rounded border border-gray-300 bg-white px-3 py-2 text-sm" placeholder="Story (optional)" rows={3} value={createForm.story} onChange={e => setCreateForm({ ...createForm, story: e.target.value })} />
              <div className="grid grid-cols-2 gap-3">
                <input type="number" className="rounded border border-gray-300 bg-white px-3 py-2 text-sm" placeholder="Goal Amount" value={createForm.goal_amount} onChange={e => setCreateForm({ ...createForm, goal_amount: Number(e.target.value) })} />
                <select className="rounded border border-gray-300 bg-white px-3 py-2 text-sm" value={createForm.duration_months} onChange={e => setCreateForm({ ...createForm, duration_months: e.target.value as DurationOption })}>
                  <option value="1">1 month</option>
                  <option value="3">3 months</option>
                  <option value="6">6 months</option>
                  <option value="12">12 months</option>
                </select>
              </div>
              <input className="rounded border border-gray-300 bg-white px-3 py-2 text-sm" placeholder="Category (optional)" value={createForm.category} onChange={e => setCreateForm({ ...createForm, category: e.target.value })} />
              
              {/* Image Upload Section */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Campaign Image</label>
                <div className="space-y-3">
                  {/* File Upload */}
                  <div>
                    <label className="block">
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/jpeg,image/png,image/jpg"
                        onChange={handleFileSelect}
                        className="hidden"
                      />
                      <div className="w-full bg-[#00AFF0] hover:bg-[#0099D6] text-white px-4 py-2 rounded-lg text-sm font-medium text-center cursor-pointer transition-colors duration-200 border border-[#00AFF0] hover:border-[#0099D6]">
                        📁 Choose Image File
                      </div>
                    </label>
                    <p className="mt-2 text-xs text-gray-500">
                      <strong>Recommended:</strong> 600x600 pixels, JPG or PNG format
                    </p>
                  </div>
                  
                  {/* Image Preview */}
                  {imagePreview && (
                    <div className="relative">
                      <img
                        src={imagePreview}
                        alt="Preview"
                        className="h-24 w-full rounded object-cover border border-gray-300"
                      />
                      <button
                        type="button"
                        onClick={handleRemoveFile}
                        className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs hover:bg-red-600"
                      >
                        ×
                      </button>
                    </div>
                  )}
                  
                  {/* OR Image URL */}
                  <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                      <div className="w-full border-t border-gray-300" />
                    </div>
                    <div className="relative flex justify-center text-sm">
                      <span className="bg-white px-2 text-gray-500">OR</span>
                    </div>
                  </div>
                  
                  <div>
                    <input
                      className="w-full rounded border border-gray-300 bg-white px-3 py-2 text-sm"
                      placeholder="Enter image URL instead of uploading"
                      value={createForm.image_url}
                      onChange={(e) => {
                        setCreateForm({ ...createForm, image_url: e.target.value });
                        if (e.target.value) {
                          setSelectedFile(null);
                          setImagePreview(null);
                          if (fileInputRef.current) {
                            fileInputRef.current.value = "";
                          }
                        }
                      }}
                    />
                  </div>
                </div>
              </div>
              
              <input className="rounded border border-gray-300 bg-white px-3 py-2 text-sm" placeholder="Video URL (optional)" value={createForm.video_url} onChange={e => setCreateForm({ ...createForm, video_url: e.target.value })} />
            </div>
            <div className="mt-6 flex justify-end gap-2">
              <button onClick={() => setShowCreate(false)} className="btn-outline text-sm px-4 py-2">Cancel</button>
              <button onClick={handleCreateCampaign} className="btn-primary text-sm px-4 py-2">Create</button>
            </div>
          </div>
        </div>
      )}

      {/* Student Details Form Modal */}
      {showStudentForm && editingStudent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40" onClick={() => setShowStudentForm(false)} />
          <div className="relative w-full max-w-2xl rounded-lg bg-white shadow-lg border border-gray-100 p-6">
            <div className="flex items-start justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">
                Edit Student Details - {editingStudent.first_name} {editingStudent.last_name}
              </h2>
              <button 
                onClick={() => setShowStudentForm(false)} 
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Student ID</label>
                <input 
                  className="w-full rounded border border-gray-300 bg-white px-3 py-2 text-sm" 
                  placeholder="Student ID" 
                  value={studentForm.student_id} 
                  onChange={e => setStudentForm({ ...studentForm, student_id: e.target.value })} 
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Class</label>
                <input 
                  className="w-full rounded border border-gray-300 bg-white px-3 py-2 text-sm" 
                  placeholder="Class/Grade" 
                  value={studentForm.class} 
                  onChange={e => setStudentForm({ ...studentForm, class: e.target.value })} 
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                <input 
                  className="w-full rounded border border-gray-300 bg-white px-3 py-2 text-sm" 
                  placeholder="Phone Number" 
                  value={studentForm.phone} 
                  onChange={e => setStudentForm({ ...studentForm, phone: e.target.value })} 
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
                <input 
                  type="date"
                  className="w-full rounded border border-gray-300 bg-white px-3 py-2 text-sm" 
                  value={studentForm.date_of_birth} 
                  onChange={e => setStudentForm({ ...studentForm, date_of_birth: e.target.value })} 
                />
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                <textarea 
                  className="w-full rounded border border-gray-300 bg-white px-3 py-2 text-sm" 
                  placeholder="Full Address" 
                  rows={2}
                  value={studentForm.address} 
                  onChange={e => setStudentForm({ ...studentForm, address: e.target.value })} 
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Emergency Contact</label>
                <input 
                  className="w-full rounded border border-gray-300 bg-white px-3 py-2 text-sm" 
                  placeholder="Emergency Contact Name" 
                  value={studentForm.emergency_contact} 
                  onChange={e => setStudentForm({ ...studentForm, emergency_contact: e.target.value })} 
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Emergency Phone</label>
                <input 
                  className="w-full rounded border border-gray-300 bg-white px-3 py-2 text-sm" 
                  placeholder="Emergency Contact Phone" 
                  value={studentForm.emergency_phone} 
                  onChange={e => setStudentForm({ ...studentForm, emergency_phone: e.target.value })} 
                />
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Academic Results</label>
                <textarea 
                  className="w-full rounded border border-gray-300 bg-white px-3 py-2 text-sm" 
                  placeholder="Academic results, grades, achievements, etc." 
                  rows={4}
                  value={studentForm.academic_results} 
                  onChange={e => setStudentForm({ ...studentForm, academic_results: e.target.value })} 
                />
              </div>
            </div>
            
            <div className="mt-6 flex justify-end gap-2">
              <button 
                onClick={() => setShowStudentForm(false)} 
                className="btn-outline text-sm px-4 py-2"
              >
                Cancel
              </button>
              <button 
                onClick={handleSaveStudentDetails} 
                className="btn-primary text-sm px-4 py-2"
              >
                Save Details
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Student Profile Modal */}
      <StudentProfileModal
        isOpen={showStudentProfile}
        onClose={() => setShowStudentProfile(false)}
        onConfirm={handleStudentProfileConfirm}
        student={selectedStudent}
      />
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-4 py-1">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="text-sm text-gray-900 max-w-sm text-right">{value}</div>
    </div>
  );
}
