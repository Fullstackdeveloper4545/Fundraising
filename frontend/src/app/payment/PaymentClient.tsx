"use client";
import React, { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Swal from "sweetalert2";
import { useAuth } from "@/context/AuthContext";
import { CampaignAPI } from "@/lib/api";

export default function PaymentClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [selectedMethod, setSelectedMethod] = useState<string>("");

  const amount = searchParams.get("amount") || "10";
  const duration = searchParams.get("duration") || "1";

  useEffect(() => {
    if (!user) {
      router.push("/signin");
    }
  }, [user, router]);

  const createCampaignAfterPayment = async () => {
    try {
      const storedFormData = sessionStorage.getItem("campaignFormData");
      const hasFile = sessionStorage.getItem("selectedFile") === "true";

      if (!storedFormData) {
        throw new Error("Campaign form data not found");
      }

      const formData = JSON.parse(storedFormData);

      const apiFormData = new FormData();
      apiFormData.append("title", formData.title);
      apiFormData.append("description", formData.description);
      apiFormData.append("goal_amount", formData.goal_amount.toString());
      apiFormData.append("duration_months", formData.duration_months);
      apiFormData.append("category", formData.category || "");
      apiFormData.append("story", formData.story || "");
      apiFormData.append("video_url", formData.video_url || "");

      if (hasFile) {
        const fileData = sessionStorage.getItem("campaignFileData");
        const fileName = sessionStorage.getItem("campaignFileName");

        if (fileData && fileName) {
          const response = await fetch(fileData);
          const blob = await response.blob();
          const file = new File([blob], fileName, { type: blob.type });
          apiFormData.append("image_file", file);
        }
      } else if (formData.image_url) {
        apiFormData.append("image_url", formData.image_url);
      }

      const response = await CampaignAPI.createWithImage(apiFormData, token as string);

      sessionStorage.removeItem("campaignFormData");
      sessionStorage.removeItem("selectedFile");
      sessionStorage.removeItem("campaignFileData");
      sessionStorage.removeItem("campaignFileName");

      return response;
    } catch (error) {
      console.error("Error creating campaign:", error);
      throw error;
    }
  };

  const handlePayment = async () => {
    if (!selectedMethod) {
      Swal.fire({
        title: "Select Payment Method",
        text: "Please select a payment method to continue.",
        icon: "warning",
        customClass: {
          popup: "swal2-popup-custom",
        },
      });
      return;
    }

    setLoading(true);

    try {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      const campaign = await createCampaignAfterPayment();

      Swal.fire({
        title: "Payment Successful!",
        html: `
          <div class="text-left">
            <p class="mb-4">Your campaign "<strong>${campaign.title}</strong>" has been created and is now in <strong>draft status</strong>.</p>
            <div class="bg-blue-50 p-4 rounded-lg mb-4">
              <h4 class="font-semibold text-blue-900 mb-2">Next Steps:</h4>
              <ol class="list-decimal list-inside space-y-1 text-sm text-blue-800">
                <li>Refer 5 friends to get your campaign approved</li>
                <li>Share your referral links with friends and family</li>
                <li>Once 5 referrals are accepted, your campaign will go to admin for approval</li>
                <li>Your campaign will become active after admin approval</li>
              </ol>
            </div>
            <p class="text-sm text-gray-600">You can track your referral progress in the referrals section.</p>
          </div>
        `,
        icon: "success",
        confirmButtonText: "Continue to Referrals",
        customClass: {
          popup: "swal2-popup-custom",
          confirmButton: "swal2-confirm",
        },
      }).then(() => {
        router.push("/referrals");
      });
    } catch (error) {
      console.error("Payment/Campaign creation failed:", error);

      let errorMessage = "There was an error processing your payment or creating your campaign. Please try again.";

      if (error instanceof Error) {
        try {
          const errorData = JSON.parse(error.message);
          if (errorData.error && errorData.error.includes("validation error")) {
            errorMessage = "Please check your campaign details and make sure all fields meet the requirements.";
          } else {
            errorMessage = error.message;
          }
        } catch {
          errorMessage = error.message;
        }
      }

      Swal.fire({
        title: "Error",
        text: errorMessage,
        icon: "error",
        customClass: {
          popup: "swal2-popup-custom",
        },
      });
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#00AFF0] to-[#0099D6] flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full mx-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Sign in required</h1>
          <p className="text-gray-600 mb-6">Please sign in to complete your payment.</p>
          <button className="btn-primary w-full" onClick={() => router.push("/signin")}>
            Sign in
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#00AFF0] to-[#0099D6]">
      <div className="max-w-7xl mx-auto px-2 py-12">
        <div className="bg-white rounded-2xl shadow-lg p-16 hover:shadow-xl transition-all duration-300">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Complete Your Payment</h1>
            <p className="text-gray-600">Choose your preferred payment method to continue</p>
          </div>

          <div className="bg-gray-50 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Payment Summary</h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Campaign Duration:</span>
                <span className="font-semibold">
                  {duration} month{duration !== "1" ? "s" : ""}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Monthly Fee:</span>
                <span className="font-semibold">$10/month</span>
              </div>
              <div className="flex justify-between text-lg font-bold text-[#00AFF0] border-t pt-2">
                <span>Total Amount:</span>
                <span>${amount}</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {[
              {
                id: "paypal",
                label: "PayPal",
                description: "Pay securely using PayPal balance, bank account, or credit card.",
              },
              {
                id: "square",
                label: "Square",
                description: "Use Square for fast, secure credit and debit card payments.",
              },
            ].map((method) => (
              <button
                key={method.id}
                onClick={() => setSelectedMethod(method.id)}
                className={`border rounded-xl p-6 text-left transition-all ${
                  selectedMethod === method.id ? "border-[#00AFF0] bg-blue-50 shadow-lg" : "border-gray-200 hover:border-[#00AFF0]"
                }`}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xl font-semibold">{method.label}</span>
                  <span className="text-sm text-gray-500">{method.id.toUpperCase()}</span>
                </div>
                <p className="text-gray-600">{method.description}</p>
              </button>
            ))}
          </div>

          <div className="space-y-4">
            <button
              className="btn-primary w-full text-lg py-4 disabled:opacity-50"
              onClick={() => handlePayment()}
              disabled={loading || !selectedMethod}
            >
              {loading ? "Processing..." : `Pay $${amount} with ${selectedMethod ? selectedMethod.toUpperCase() : "selected method"}`}
            </button>
            <button className="btn-outline w-full text-lg py-4" onClick={() => router.back()}>
              Cancel and go back
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
