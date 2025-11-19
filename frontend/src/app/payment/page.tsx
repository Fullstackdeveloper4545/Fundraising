import { Suspense } from "react";
import PaymentClient from "./PaymentClient";

export default function PaymentPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#00AFF0] to-[#0099D6] text-white">
          Loading payment details...
        </div>
      }
    >
      <PaymentClient />
    </Suspense>
  );
}
