"use client";
import React, { useState } from "react";
import { PartnershipAPI } from "@/lib/api";

export default function PartnershipPage() {
  const [form, setForm] = useState({ company: "", contact: "", email: "", message: "" });
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await PartnershipAPI.request({
        company: form.company,
        contact: form.contact,
        email: form.email,
        message: form.message
      });
      setSent(true);
    } catch (err) {
      setError("Failed to send partnership request. Please try again.");
      console.error("Partnership request error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      <div className="max-w-9xl mx-auto px-2 py-12">
        <div className="grid lg:grid-cols-2 gap-8 items-stretch">
          {/* Left Side - Form */}
          <div className="bg-white rounded-2xl shadow-lg p-16 hover:shadow-xl transition-all duration-300 flex flex-col">
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-2xl font-bold text-gray-900">Partnership Request</h1>
            </div>

            <div className="mb-6">
              <p className="text-gray-600">Join us to support student success through scholarships, mentorships, and sponsorships.</p>
            </div>

            {sent ? (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                Thanks! We received your partnership request and will get back to you soon.
              </div>
            ) : (
              <form onSubmit={onSubmit} className="space-y-8 flex-1 flex flex-col">
                {/* Organization */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Organization</label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00AFF0] focus:border-transparent outline-none hover:border-[#00AFF0] transition-all duration-200"
                    placeholder="Enter organization name"
                    value={form.company}
                    onChange={(e) => setForm({ ...form, company: e.target.value })}
                    required
                  />
                </div>

                {/* Contact Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Contact Name</label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00AFF0] focus:border-transparent outline-none hover:border-[#00AFF0] transition-all duration-200"
                    placeholder="Enter contact person name"
                    value={form.contact}
                    onChange={(e) => setForm({ ...form, contact: e.target.value })}
                    required
                  />
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  <input
                    type="email"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00AFF0] focus:border-transparent outline-none hover:border-[#00AFF0] transition-all duration-200"
                    placeholder="Enter email address"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    required
                  />
                </div>

                {/* Message */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Message</label>
                  <textarea
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#00AFF0] focus:border-transparent outline-none resize-none"
                    rows={4}
                    placeholder="Tell us about your partnership proposal"
                    value={form.message}
                    onChange={(e) => setForm({ ...form, message: e.target.value })}
                  />
                </div>

                {/* Error Message */}
                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                    {error}
                  </div>
                )}

                {/* Submit Button */}
                <div className="pt-4 mt-auto">
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-[#00AFF0] hover:bg-[#0099D6] text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 hover:shadow-lg disabled:hover:scale-100 disabled:hover:shadow-none"
                  >
                    {loading ? "Sending..." : "Request Partnership"}
                  </button>
                </div>
              </form>
            )}
          </div>

          {/* Right Side - Partnership Icon with Background */}
          <div className="bg-white rounded-2xl shadow-lg p-16 flex flex-col items-center justify-center hover:shadow-xl transition-all duration-300">
            <div className="text-center w-full">
              <div className="w-48 h-48 bg-[#00AFF0] bg-opacity-10 rounded-full flex items-center justify-center mx-auto mb-12 hover:bg-opacity-20 transition-all duration-300">
                <svg className="w-24 h-24 text-[#00AFF0]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h2 className="text-4xl font-bold mb-8 text-gray-900">Partner With Us</h2>
              <p className="text-xl mb-12 text-gray-600 max-w-md mx-auto">
                Join our mission to support student success through meaningful partnerships and collaborations.
              </p>
              
              <div className="grid grid-cols-2 gap-6 mb-12 max-w-md mx-auto">
                <div className="bg-[#00AFF0] bg-opacity-10 rounded-lg p-4 hover:bg-opacity-20 transition-all duration-300">
                  <h3 className="text-lg font-semibold mb-2 text-gray-900">Scholarships</h3>
                  <p className="text-sm text-gray-600">Support students financially</p>
                </div>
                <div className="bg-[#00AFF0] bg-opacity-10 rounded-lg p-4 hover:bg-opacity-20 transition-all duration-300">
                  <h3 className="text-lg font-semibold mb-2 text-gray-900">Mentorships</h3>
                  <p className="text-sm text-gray-600">Guide student development</p>
                </div>
                <div className="bg-[#00AFF0] bg-opacity-10 rounded-lg p-4 hover:bg-opacity-20 transition-all duration-300">
                  <h3 className="text-lg font-semibold mb-2 text-gray-900">Sponsorships</h3>
                  <p className="text-sm text-gray-600">Fund campaigns directly</p>
                </div>
                <div className="bg-[#00AFF0] bg-opacity-10 rounded-lg p-4 hover:bg-opacity-20 transition-all duration-300">
                  <h3 className="text-lg font-semibold mb-2 text-gray-900">Collaborations</h3>
                  <p className="text-sm text-gray-600">Joint initiatives</p>
                </div>
              </div>
              
              <div className="space-y-4 text-lg text-gray-600 max-w-md mx-auto">
                <div className="flex items-center justify-center gap-3 hover:text-[#00AFF0] transition-colors duration-200">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Flexible partnership options</span>
                </div>
                <div className="flex items-center justify-center gap-3 hover:text-[#00AFF0] transition-colors duration-200">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Dedicated support team</span>
                </div>
                <div className="flex items-center justify-center gap-3 hover:text-[#00AFF0] transition-colors duration-200">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Impact tracking & reporting</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


