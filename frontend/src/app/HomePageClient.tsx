"use client";
import React, { useState } from "react";

export default function HomePageClient() {
  const [faqOpen, setFaqOpen] = useState<number | null>(null);

  const toggleFaq = (index: number) => {
    setFaqOpen(faqOpen === index ? null : index);
  };

  return (
    <>
      {/* FAQ Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">FAQ&apos;s</h2>
          </div>
          
          <div className="space-y-4">
            {[
              {
                question: "How much does it cost to start a fundraiser?",
                answer: "Starting a fundraiser on FundRise is completely free. We don't charge any platform fees, so you keep 100% of the donations you receive."
              },
              {
                question: "How quickly can I receive the funds?",
                answer: "You can withdraw your funds at any time during your fundraising campaign. Most withdrawals are processed within 1-3 business days."
              },
              {
                question: "What types of student goals can I fundraise for?",
                answer: "You can fundraise for tuition fees, study abroad programs, research projects, technology equipment, sports activities, creative projects, and any other educational needs."
              },
              {
                question: "Is there a minimum or maximum amount I can raise?",
                answer: "There's no minimum amount, but we recommend setting realistic goals. There's also no maximum limit - you can raise as much as you need for your educational goals."
              },
              {
                question: "How do I share my fundraiser?",
                answer: "You can share your fundraiser through social media, email, messaging apps, and our platform's built-in sharing tools. We provide templates and tips for effective sharing."
              }
            ].map((faq, index) => (
              <div key={index} className="bg-white rounded-lg shadow-sm">
                <button
                  className="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-gray-50 transition-colors"
                  onClick={() => toggleFaq(index)}
                >
                  <span className="font-semibold text-gray-900">{faq.question}</span>
                  <span className="text-[#00AFF0] text-xl">
                    {faqOpen === index ? '−' : '+'}
                  </span>
                </button>
                {faqOpen === index && (
                  <div className="px-6 pb-4">
                    <p className="text-gray-600">{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
