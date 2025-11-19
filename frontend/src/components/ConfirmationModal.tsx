"use client";
import React from "react";

interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  confirmButtonClass?: string;
}

export default function ConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
  confirmButtonClass = "bg-red-600 hover:bg-red-700"
}: ConfirmationModalProps) {
  if (!isOpen) return null;

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
        <div className="w-full max-w-sm transform transition-all duration-300 ease-out animate-in zoom-in-95 slide-in-from-bottom-4">
          <div className="relative rounded-2xl bg-white shadow-2xl ring-1 ring-black/5">
            {/* Content */}
            <div className="px-6 py-6">
              {/* Title */}
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                {title}
              </h3>
              
              {/* Message */}
              <p className="text-gray-600 mb-6 leading-relaxed">
                {message}
              </p>
              
              {/* Actions */}
              <div className="flex justify-end gap-3">
                <button
                  onClick={() => {
                    onConfirm();
                    onClose();
                  }}
                  className={`px-6 py-2 text-sm font-semibold text-white rounded-lg transition-all duration-200 ${confirmButtonClass}`}
                >
                  {confirmText}
                </button>
                <button
                  onClick={onClose}
                  className="px-6 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 transition-colors duration-200"
                >
                  {cancelText}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
