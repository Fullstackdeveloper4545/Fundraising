"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import Swal from "sweetalert2";

export default function ReferralsPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [referrals, setReferrals] = useState([
    { id: 1, email: "", name: "", status: "pending" },
    { id: 2, email: "", name: "", status: "pending" },
    { id: 3, email: "", name: "", status: "pending" },
    { id: 4, email: "", name: "", status: "pending" },
    { id: 5, email: "", name: "", status: "pending" }
  ]);
  const [loading, setLoading] = useState(false);
  const [sentCount, setSentCount] = useState(0);

  const handleInputChange = (id: number, field: 'email' | 'name', value: string) => {
    setReferrals(prev => prev.map(ref => 
      ref.id === id ? { ...ref, [field]: value } : ref
    ));
  };

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const sendInvitations = async () => {
    const validReferrals = referrals.filter(ref => 
      ref.email.trim() !== "" && ref.name.trim() !== "" && validateEmail(ref.email)
    );

    if (validReferrals.length === 0) {
      Swal.fire({
        title: 'No Valid Referrals',
        text: 'Please enter at least one valid email and name.',
        icon: 'warning',
        customClass: {
          popup: 'swal2-popup-custom'
        }
      });
      return;
    }

    setLoading(true);
    
    try {
      // Simulate sending invitations
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setSentCount(validReferrals.length);
      
      // Update referral statuses
      setReferrals(prev => prev.map(ref => 
        validReferrals.some(valid => valid.id === ref.id) 
          ? { ...ref, status: "sent" }
          : ref
      ));

      Swal.fire({
        title: 'Invitations Sent!',
        text: `Successfully sent ${validReferrals.length} invitation${validReferrals.length > 1 ? 's' : ''}. Your friends will receive an email with your referral link.`,
        icon: 'success',
        confirmButtonText: 'Continue to Campaign',
        customClass: {
          popup: 'swal2-popup-custom',
          confirmButton: 'swal2-confirm'
        }
      }).then(() => {
        router.push('/campaigns');
      });
      
    } catch (error) {
      Swal.fire({
        title: 'Error Sending Invitations',
        text: 'There was an error sending the invitations. Please try again.',
        icon: 'error',
        customClass: {
          popup: 'swal2-popup-custom'
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const copyReferralLink = () => {
    const referralLink = `${window.location.origin}/signup?ref=${user?.id}`;
    navigator.clipboard.writeText(referralLink);
    
    Swal.fire({
      title: 'Link Copied!',
      text: 'Your referral link has been copied to clipboard.',
      icon: 'success',
      timer: 2000,
      showConfirmButton: false,
      customClass: {
        popup: 'swal2-popup-custom'
      }
    });
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#00AFF0] to-[#0099D6] flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full mx-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Sign in required</h1>
          <p className="text-gray-600 mb-6">Please sign in to access the referral system.</p>
          <button className="btn-primary w-full" onClick={() => router.push("/signin")}>Sign in</button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#00AFF0] to-[#0099D6]">
      <div className="max-w-7xl mx-auto px-2 py-12">
        <div className="bg-white rounded-2xl shadow-lg p-16 hover:shadow-xl transition-all duration-300">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Invite 5 Friends</h1>
            <p className="text-gray-600 mb-6">
              Invite 5 friends to join our platform and unlock your campaign. 
              Once they sign up, your campaign will be activated!
            </p>
          </div>

          {/* Referral Link Section */}
          <div className="bg-[#00AFF0] bg-opacity-10 rounded-lg p-6 mb-8 hover:bg-opacity-20 transition-all duration-300">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Your Referral Link</h2>
            <div className="flex gap-4">
              <input
                type="text"
                value={`${typeof window !== 'undefined' ? window.location.origin : ''}/signup?ref=${user?.id}`}
                readOnly
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 text-sm"
              />
              <button
                onClick={copyReferralLink}
                className="bg-[#00AFF0] hover:bg-[#0099D6] text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105 hover:shadow-lg"
              >
                Copy Link
              </button>
            </div>
            <p className="text-sm text-gray-600 mt-2">
              Share this link with your friends via text, email, or social media
            </p>
          </div>

          {/* Invitation Form */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Send Email Invitations</h2>
            <div className="space-y-4">
              {referrals.map((referral) => (
                <div key={referral.id} className="grid md:grid-cols-2 gap-4 p-4 border border-gray-200 rounded-lg">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Friend&apos;s Name
                    </label>
                    <input
                      type="text"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00AFF0] focus:border-transparent outline-none hover:border-[#00AFF0] transition-all duration-200"
                      placeholder="Enter friend&apos;s name"
                      value={referral.name}
                      onChange={(e) => handleInputChange(referral.id, 'name', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="email"
                        className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00AFF0] focus:border-transparent outline-none"
                        placeholder="friend@example.com"
                        value={referral.email}
                        onChange={(e) => handleInputChange(referral.id, 'email', e.target.value)}
                      />
                      {referral.status === "sent" && (
                        <div className="flex items-center px-3 py-3 text-green-600">
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Progress Indicator */}
          <div className="bg-gray-50 rounded-lg p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Referral Progress</h3>
            <div className="flex items-center gap-4">
              <div className="flex-1 bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-[#00AFF0] h-3 rounded-full transition-all duration-500"
                  style={{ width: `${(sentCount / 5) * 100}%` }}
                ></div>
              </div>
              <span className="text-sm font-medium text-gray-700">
                {sentCount}/5 invitations sent
              </span>
            </div>
            <p className="text-sm text-gray-600 mt-2">
              {sentCount >= 5 
                ? "🎉 Congratulations! You&apos;ve sent all required invitations. Your campaign will be activated once your friends sign up."
                : `Send ${5 - sentCount} more invitation${5 - sentCount > 1 ? 's' : ''} to activate your campaign.`
              }
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button
              onClick={() => router.push('/campaigns')}
              className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 hover:scale-105 hover:shadow-md transition-all duration-200"
            >
              Skip for Now
            </button>
            <button
              onClick={sendInvitations}
              disabled={loading}
              className="flex-1 bg-[#00AFF0] hover:bg-[#0099D6] text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 hover:shadow-lg disabled:hover:scale-100 disabled:hover:shadow-none"
            >
              {loading ? 'Sending...' : 'Send Invitations'}
            </button>
          </div>

          {/* Benefits Section */}
          <div className="mt-8 bg-green-50 border border-green-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-green-800 mb-4">Why Invite Friends?</h3>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3 hover:bg-green-200 transition-all duration-200">
                  <svg className="w-6 h-6 text-green-600 hover:text-green-700 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h4 className="font-semibold text-green-800 mb-2">Activate Campaign</h4>
                <p className="text-sm text-green-700">Unlock your fundraising campaign</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3 hover:bg-green-200 transition-all duration-200">
                  <svg className="w-6 h-6 text-green-600 hover:text-green-700 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <h4 className="font-semibold text-green-800 mb-2">Build Community</h4>
                <p className="text-sm text-green-700">Grow our student network</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3 hover:bg-green-200 transition-all duration-200">
                  <svg className="w-6 h-6 text-green-600 hover:text-green-700 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h4 className="font-semibold text-green-800 mb-2">Earn Rewards</h4>
                <p className="text-sm text-green-700">Get bonus features for referrals</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
