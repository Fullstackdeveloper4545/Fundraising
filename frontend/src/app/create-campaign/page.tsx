"use client";
import React, { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { CampaignAPI } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import Swal from "sweetalert2";

export default function CreateCampaignPage() {
  const router = useRouter();
  const { token, user } = useAuth();
  const [form, setForm] = useState({
    title: "",
    description: "",
    goal_amount: 1000,
    duration_months: "1" as "1" | "3" | "6" | "12",
    category: "",
    image_url: "",
    story: "",
    video_url: "",
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<{[key: string]: string}>({});
  const fileInputRef = useRef<HTMLInputElement>(null);
  const monthsNum = Number(form.duration_months);
  const monthlyFee = 10;
  const totalFee = monthlyFee * monthsNum;

  const validateForm = () => {
    const errors: {[key: string]: string} = {};
    
    if (!form.title || form.title.trim().length < 5) {
      errors.title = 'Title must be at least 5 characters long';
    }
    
    if (!form.description || form.description.trim().length < 20) {
      errors.description = 'Description must be at least 20 characters long';
    }
    
    if (!form.goal_amount || form.goal_amount <= 0) {
      errors.goal_amount = 'Goal amount must be greater than 0';
    }
    
    if (form.goal_amount && form.goal_amount > 100000) {
      errors.goal_amount = 'Goal amount cannot exceed $100,000';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setForm({ ...form, image_url: "" });
      
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

  const showCancelModal = () => {
    Swal.fire({
      title: 'Cancel Campaign Creation?',
      text: 'Are you sure you want to cancel? All your progress will be lost.',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#ef4444',
      cancelButtonColor: '#6b7280',
      confirmButtonText: 'Yes, cancel',
      cancelButtonText: 'Continue editing',
      customClass: {
        popup: 'swal2-popup-custom',
        confirmButton: 'swal2-confirm',
        cancelButton: 'swal2-cancel'
      }
    }).then((result) => {
      if (result.isConfirmed) {
        router.push('/campaigns');
      }
    });
  };

  const showCreateModal = () => {
    // Validate form before showing modal
    if (!validateForm()) {
      Swal.fire({
        title: 'Validation Error',
        text: 'Please fix the errors in the form before creating your campaign.',
        icon: 'error',
        customClass: {
          popup: 'swal2-popup-custom'
        }
      });
      return;
    }

    Swal.fire({
      title: 'Create Campaign?',
      html: `
        <div class="text-left">
          <p class="mb-2"><strong>Campaign:</strong> ${form.title}</p>
          <p class="mb-2"><strong>Goal:</strong> $${form.goal_amount}</p>
          <p class="mb-2"><strong>Duration:</strong> ${form.duration_months} month${monthsNum > 1 ? 's' : ''}</p>
          <p class="mb-4"><strong>Fee:</strong> $${totalFee} ($${monthlyFee}/month)</p>
          <p class="text-sm text-gray-600">You will be redirected to payment after confirmation.</p>
        </div>
      `,
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#00AFF0',
      cancelButtonColor: '#6b7280',
      confirmButtonText: 'Yes, create campaign',
      cancelButtonText: 'Review details',
      customClass: {
        popup: 'swal2-popup-custom',
        confirmButton: 'swal2-confirm',
        cancelButton: 'swal2-cancel'
      }
    }).then((result) => {
      if (result.isConfirmed) {
        handlePayment();
      }
    });
  };

  const handlePayment = () => {
    // Redirect to payment gateway
    const paymentData = {
      amount: totalFee,
      campaign_title: form.title,
      duration: form.duration_months,
      user_id: user?.id
    };
    
    // Store form data in sessionStorage for after payment
    sessionStorage.setItem('campaignFormData', JSON.stringify(form));
    
    // Store file information
    if (selectedFile) {
      // Convert file to base64 for storage
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result as string;
        sessionStorage.setItem('campaignFileData', base64);
        sessionStorage.setItem('campaignFileName', selectedFile.name);
        sessionStorage.setItem('selectedFile', 'true');
        
        // Redirect to payment page
        router.push(`/payment?amount=${totalFee}&type=campaign&duration=${form.duration_months}`);
      };
      reader.readAsDataURL(selectedFile);
    } else {
      sessionStorage.setItem('selectedFile', 'false');
      // Redirect to payment page
      router.push(`/payment?amount=${totalFee}&type=campaign&duration=${form.duration_months}`);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#00AFF0] to-[#0099D6] flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full mx-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Sign in required</h1>
          <p className="text-gray-600 mb-6">Please sign in with a student or admin account to create a campaign.</p>
          <button className="btn-primary w-full" onClick={() => router.push("/signin")}>Sign in</button>
        </div>
      </div>
    );
  }

  if (user && !["student", "admin"].includes(user.role)) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#00AFF0] to-[#0099D6] flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full mx-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Campaign creation is restricted</h1>
          <p className="text-gray-600 mb-6">Only student and admin accounts can create campaigns on this platform.</p>
          <button className="btn-primary w-full" onClick={() => router.push("/campaigns")}>Browse campaigns</button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen ">
      <div className="max-w-9xl mx-auto px-2 py-12">
        <div className="grid lg:grid-cols-2 gap-8 items-stretch">
          {/* Left Side - Form */}
          <div className="bg-white rounded-2xl shadow-lg p-16 hover:shadow-xl transition-all duration-300 flex flex-col">
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-2xl font-bold text-gray-900">Create New Campaign</h1>
              <button
                onClick={showCancelModal}
                className="text-gray-400 hover:text-gray-600 hover:scale-110 transition-all duration-200"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form className="space-y-8 flex-1 flex flex-col">
              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
                <input
                  type="text"
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-[#00AFF0] focus:border-transparent outline-none transition-all duration-200 ${
                    validationErrors.title 
                      ? 'border-red-300 hover:border-red-400' 
                      : 'border-gray-300 hover:border-[#00AFF0]'
                  }`}
                  placeholder="Enter campaign title (minimum 5 characters)"
                  value={form.title}
                  onChange={(e) => {
                    setForm({ ...form, title: e.target.value });
                    // Clear validation error when user starts typing
                    if (validationErrors.title) {
                      setValidationErrors({ ...validationErrors, title: '' });
                    }
                  }}
                  required
                />
                <div className="flex justify-between items-center mt-1">
                  {validationErrors.title ? (
                    <p className="text-sm text-red-600">{validationErrors.title}</p>
                  ) : (
                    <p className="text-sm text-gray-500">
                      {form.title.length}/5 characters minimum
                    </p>
                  )}
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-[#00AFF0] focus:border-transparent outline-none resize-none transition-all duration-200 ${
                    validationErrors.description 
                      ? 'border-red-300 hover:border-red-400' 
                      : 'border-gray-300 hover:border-[#00AFF0]'
                  }`}
                  rows={4}
                  placeholder="Describe your campaign (minimum 20 characters)"
                  value={form.description}
                  onChange={(e) => {
                    setForm({ ...form, description: e.target.value });
                    // Clear validation error when user starts typing
                    if (validationErrors.description) {
                      setValidationErrors({ ...validationErrors, description: '' });
                    }
                  }}
                  required
                />
                <div className="flex justify-between items-center mt-1">
                  {validationErrors.description ? (
                    <p className="text-sm text-red-600">{validationErrors.description}</p>
                  ) : (
                    <p className="text-sm text-gray-500">
                      {form.description.length}/20 characters minimum
                    </p>
                  )}
                </div>
              </div>

              {/* Story */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Story (optional)</label>
                <textarea
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00AFF0] focus:border-transparent outline-none resize-none"
                  rows={4}
                  placeholder="Tell your story"
                  value={form.story}
                  onChange={(e) => setForm({ ...form, story: e.target.value })}
                />
              </div>

              {/* Amount and Duration */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Goal Amount ($)</label>
                  <input
                    type="number"
                    min="1"
                    max="100000"
                    className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-[#00AFF0] focus:border-transparent outline-none transition-all duration-200 ${
                      validationErrors.goal_amount 
                        ? 'border-red-300 hover:border-red-400' 
                        : 'border-gray-300 hover:border-[#00AFF0]'
                    }`}
                    placeholder="1000"
                    value={form.goal_amount}
                    onChange={(e) => {
                      setForm({ ...form, goal_amount: Number(e.target.value) });
                      // Clear validation error when user starts typing
                      if (validationErrors.goal_amount) {
                        setValidationErrors({ ...validationErrors, goal_amount: '' });
                      }
                    }}
                    required
                  />
                  {validationErrors.goal_amount && (
                    <p className="mt-1 text-sm text-red-600">{validationErrors.goal_amount}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Duration</label>
                  <select
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00AFF0] focus:border-transparent outline-none hover:border-[#00AFF0] transition-all duration-200"
                    value={form.duration_months}
                    onChange={(e) => setForm({ ...form, duration_months: e.target.value as "1" | "3" | "6" | "12" })}
                  >
                    <option value="1">1 month</option>
                    <option value="3">3 months</option>
                    <option value="6">6 months</option>
                    <option value="12">12 months</option>
                  </select>
                </div>
              </div>

              {/* Category */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Category (optional)</label>
                <input
                  type="text"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00AFF0] focus:border-transparent outline-none hover:border-[#00AFF0] transition-all duration-200"
                  placeholder="e.g., Education, Technology, Sports"
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                />
              </div>

              {/* Campaign Image */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Campaign Image</label>
                <div className="space-y-4">
                  {/* File Upload Button */}
                  <div>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/jpeg,image/png,image/jpg"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="w-full bg-[#00AFF0] hover:bg-[#0099D6] text-white px-4 py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 hover:scale-105 hover:shadow-lg"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                      </svg>
                      Choose Image File
                    </button>
                    <p className="mt-2 text-sm text-gray-500">
                      Recommended: 600x600 pixels, JPG or PNG format
                    </p>
                  </div>

                  {/* Image Preview */}
                  {imagePreview && (
                    <div className="relative">
                      <img
                        src={imagePreview}
                        alt="Preview"
                        className="w-full h-32 object-cover rounded-lg border border-gray-300"
                      />
                      <button
                        type="button"
                        onClick={handleRemoveFile}
                         className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm hover:bg-red-600 hover:scale-110 transition-all duration-200"
                      >
                        ×
                      </button>
                    </div>
                  )}

                  {/* OR Divider */}
                  <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                      <div className="w-full border-t border-gray-300" />
                    </div>
                    <div className="relative flex justify-center text-sm">
                      <span className="bg-white px-2 text-gray-500">OR</span>
                    </div>
                  </div>

                  {/* Image URL */}
                  <div>
                    <input
                      type="url"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00AFF0] focus:border-transparent outline-none hover:border-[#00AFF0] transition-all duration-200"
                      placeholder="Enter image URL instead of uploading"
                      value={form.image_url}
                      onChange={(e) => {
                        setForm({ ...form, image_url: e.target.value });
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

              {/* Video URL */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Video URL (optional)</label>
                <input
                  type="url"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00AFF0] focus:border-transparent outline-none hover:border-[#00AFF0] transition-all duration-200"
                  placeholder="https://youtube.com/watch?v=..."
                  value={form.video_url}
                  onChange={(e) => setForm({ ...form, video_url: e.target.value })}
                />
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-4 pt-4 mt-auto">
                <button
                  type="button"
                  onClick={showCancelModal}
                  className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 hover:scale-105 hover:shadow-md transition-all duration-200"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={showCreateModal}
                  disabled={loading || !form.title || !form.description}
                  className="flex-1 bg-[#00AFF0] hover:bg-[#0099D6] text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 hover:shadow-lg disabled:hover:scale-100 disabled:hover:shadow-none"
                >
                  {loading ? "Creating..." : `Create ($${totalFee})`}
                </button>
              </div>
            </form>
          </div>

          {/* Right Side - Icon with Background */}
          <div className="bg-white rounded-2xl shadow-lg p-16 flex flex-col items-center justify-center hover:shadow-xl transition-all duration-300">
            <div className="text-center w-full">
              <div className="w-48 h-48 bg-[#00AFF0] bg-opacity-10 rounded-full flex items-center justify-center mx-auto mb-12 hover:bg-opacity-20 transition-all duration-300">
                <svg className="w-24 h-24 text-[#00AFF0]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <h2 className="text-4xl font-bold mb-8 text-gray-900">Start Your Campaign</h2>
              <p className="text-xl mb-12 text-gray-600 max-w-md mx-auto">
                Create a compelling campaign and reach your funding goals with our community support.
              </p>
              
              <div className="grid grid-cols-2 gap-6 mb-12 max-w-md mx-auto">
                <div className="bg-[#00AFF0] bg-opacity-10 rounded-lg p-4 hover:bg-opacity-20 transition-all duration-300">
                  <h3 className="text-lg font-semibold mb-2 text-gray-900">1 Month</h3>
                  <p className="text-2xl font-bold text-[#00AFF0]">$10</p>
                </div>
                <div className="bg-[#00AFF0] bg-opacity-10 rounded-lg p-4 hover:bg-opacity-20 transition-all duration-300">
                  <h3 className="text-lg font-semibold mb-2 text-gray-900">3 Months</h3>
                  <p className="text-2xl font-bold text-[#00AFF0]">$30</p>
                </div>
                <div className="bg-[#00AFF0] bg-opacity-10 rounded-lg p-4 hover:bg-opacity-20 transition-all duration-300">
                  <h3 className="text-lg font-semibold mb-2 text-gray-900">6 Months</h3>
                  <p className="text-2xl font-bold text-[#00AFF0]">$60</p>
                </div>
                <div className="bg-[#00AFF0] bg-opacity-10 rounded-lg p-4 hover:bg-opacity-20 transition-all duration-300">
                  <h3 className="text-lg font-semibold mb-2 text-gray-900">12 Months</h3>
                  <p className="text-2xl font-bold text-[#00AFF0]">$120</p>
                </div>
              </div>
              
              <div className="space-y-4 text-lg text-gray-600 max-w-md mx-auto">
                <div className="flex items-center justify-center gap-3 hover:text-[#00AFF0] transition-colors duration-200">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Secure payment processing</span>
                </div>
                <div className="flex items-center justify-center gap-3 hover:text-[#00AFF0] transition-colors duration-200">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>24/7 customer support</span>
                </div>
                <div className="flex items-center justify-center gap-3 hover:text-[#00AFF0] transition-colors duration-200">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Referral program included</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}