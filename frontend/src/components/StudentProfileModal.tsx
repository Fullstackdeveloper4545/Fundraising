"use client";
import React from "react";
import type { User } from "@/types/api";

interface StudentProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  student: User | null;
}

export default function StudentProfileModal({
  isOpen,
  onClose,
  onConfirm,
  student,
}: StudentProfileModalProps) {
  if (!isOpen || !student) return null;

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-black/30 backdrop-blur-md animate-in fade-in duration-300"
      onClick={handleBackdropClick}
      onKeyDown={handleKeyDown}
      tabIndex={-1}
    >
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="w-full max-w-2xl transform transition-all duration-300 ease-out animate-in zoom-in-95 slide-in-from-bottom-4">
          <div className="relative rounded-2xl bg-white shadow-2xl ring-1 ring-black/5">
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-gray-900">
                  Student Profile Details
                </h3>
                <button
                  onClick={onClose}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="px-6 py-6 max-h-96 overflow-y-auto">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Basic Information */}
                <div className="space-y-4">
                  <h4 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
                    Basic Information
                  </h4>
                  
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Full Name</label>
                      <p className="mt-1 text-sm text-gray-900">
                        {student.first_name} {student.last_name}
                      </p>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Email</label>
                      <p className="mt-1 text-sm text-gray-900">{student.email}</p>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Student ID</label>
                      <p className="mt-1 text-sm text-gray-900">
                        {student.student_id || "Not provided"}
                      </p>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Class</label>
                      <p className="mt-1 text-sm text-gray-900">
                        {student.class || "Not provided"}
                      </p>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Phone</label>
                      <p className="mt-1 text-sm text-gray-900">
                        {student.phone || "Not provided"}
                      </p>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Date of Birth</label>
                      <p className="mt-1 text-sm text-gray-900">
                        {student.date_of_birth || "Not provided"}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Academic & Contact Information */}
                <div className="space-y-4">
                  <h4 className="text-lg font-semibold text-gray-900 border-b border-gray-200 pb-2">
                    Academic & Contact Information
                  </h4>
                  
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Academic Results</label>
                      <div className="mt-1 p-3 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-900 whitespace-pre-wrap">
                          {student.academic_results || "No academic results provided"}
                        </p>
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Address</label>
                      <p className="mt-1 text-sm text-gray-900">
                        {student.address || "Not provided"}
                      </p>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Emergency Contact</label>
                      <p className="mt-1 text-sm text-gray-900">
                        {student.emergency_contact || "Not provided"}
                      </p>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Emergency Phone</label>
                      <p className="mt-1 text-sm text-gray-900">
                        {student.emergency_phone || "Not provided"}
                      </p>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Account Status</label>
                      <div className="mt-1">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          student.is_verified 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {student.is_verified ? 'Verified' : 'Pending Verification'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-2xl">
              <div className="flex justify-end gap-3">
                <button
                  onClick={onClose}
                  className="px-6 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 transition-colors duration-200"
                >
                  Close
                </button>
                <button
                  onClick={() => {
                    onConfirm();
                    onClose();
                  }}
                  className="px-6 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-all duration-200"
                >
                  View Full Details
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
