"use client";
import Link from "next/link";

export default function Footer() {
  return (
    <footer className="bg-[#00AFF0] border-t border-[#0099D6]">
      <div className="mx-auto max-w-7xl px-4 py-12">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4">
          {/* Company Info */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded-lg bg-[#00AFF0] flex items-center justify-center">
                <span className="text-white font-bold text-sm">F</span>
              </div>
              <span className="text-xl font-bold text-white">
                Fundraising Platform
              </span>
            </div>
            <p className="text-sm text-white/90 max-w-xs">
              Empowering students to achieve their dreams through community support and fundraising.
            </p>
            <div className="flex space-x-4">
              <a
                href="#"
                className="text-white/80 hover:text-white transition-colors"
                aria-label="Facebook"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
              </a>
              <a
                href="#"
                className="text-white/80 hover:text-white transition-colors"
                aria-label="Twitter"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                </svg>
              </a>
              <a
                href="#"
                className="text-white/80 hover:text-white transition-colors"
                aria-label="LinkedIn"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
              </a>
              <a
                href="#"
                className="text-white/80 hover:text-white transition-colors"
                aria-label="Instagram"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 6.62 5.367 11.987 11.988 11.987s11.987-5.367 11.987-11.987C24.014 5.367 18.647.001 12.017.001zM8.449 16.988c-1.297 0-2.448-.49-3.323-1.297C4.198 14.895 3.708 13.744 3.708 12.447s.49-2.448 1.297-3.323c.875-.807 2.026-1.297 3.323-1.297s2.448.49 3.323 1.297c.807.875 1.297 2.026 1.297 3.323s-.49 2.448-1.297 3.323c-.875.807-2.026 1.297-3.323 1.297zm7.718-1.297c-.875.807-2.026 1.297-3.323 1.297s-2.448-.49-3.323-1.297c-.807-.875-1.297-2.026-1.297-3.323s.49-2.448 1.297-3.323c.875-.807 2.026-1.297 3.323-1.297s2.448.49 3.323 1.297c.807.875 1.297 2.026 1.297 3.323s-.49 2.448-1.297 3.323z"/>
                </svg>
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider">
              Quick Links
            </h3>
            <ul className="space-y-3">
              <li>
                <Link href="/" className="text-sm text-white/90 hover:text-white transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link href="/campaigns" className="text-sm text-white/90 hover:text-white transition-colors">
                  Browse Campaigns
                </Link>
              </li>
              <li>
                <Link href="/create-campaign" className="text-sm text-white/90 hover:text-white transition-colors">
                  Start a Campaign
                </Link>
              </li>
              <li>
                <Link href="/partnership" className="text-sm text-white/90 hover:text-white transition-colors">
                  Partnership
                </Link>
              </li>
              <li>
                <Link href="/spotlight" className="text-sm text-white/90 hover:text-white transition-colors">
                  Student Spotlight
                </Link>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider">
              Support
            </h3>
            <ul className="space-y-3">
              <li>
                <Link href="/signin" className="text-sm text-white/90 hover:text-white transition-colors">
                  Sign In
                </Link>
              </li>
              <li>
                <Link href="/signup" className="text-sm text-white/90 hover:text-white transition-colors">
                  Sign Up
                </Link>
              </li>
              <li>
                <Link href="/donor" className="text-sm text-white/90 hover:text-white transition-colors">
                  For Donors
                </Link>
              </li>
              <li>
                <Link href="/admin/login" className="text-sm text-white/90 hover:text-white transition-colors">
                  Admin Login
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider">
              Legal
            </h3>
            <ul className="space-y-3">
              <li>
                <span className="text-sm text-white/70">
                  Privacy Policy
                </span>
              </li>
              <li>
                <span className="text-sm text-white/70">
                  Terms of Service
                </span>
              </li>
              <li>
                <span className="text-sm text-white/70">
                  Cookie Policy
                </span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-12 border-t border-white/20 pt-8">
          <div className="flex flex-col items-center justify-between space-y-4 md:flex-row md:space-y-0">
            <div className="flex flex-col items-center space-y-2 md:flex-row md:space-y-0 md:space-x-6">
              <p className="text-sm text-white/90">
                © {new Date().getFullYear()} Fundraising Platform. All rights reserved.
              </p>
              <div className="flex items-center space-x-4 text-xs text-white/70">
                <span className="flex items-center gap-1">Made with <span className="text-[#00AFF0] text-xl">💰</span> for students</span>
                <span>•</span>
                <span>Secure & Trusted</span>
              </div>
            </div>
            
            {/* Payment Methods */}
            <div className="flex items-center space-x-4">
              <span className="text-xs text-white/70">Secure payments:</span>
              <div className="flex items-center space-x-3">
                {/* Visa */}
                <div className="payment-badge h-8 w-12 bg-white rounded flex items-center justify-center p-1">
                  <svg viewBox="0 0 24 16" className="h-6 w-8">
                    <rect width="24" height="16" rx="2" fill="white"/>
                    <rect x="0" y="0" width="24" height="2" fill="#1A1F71"/>
                    <rect x="0" y="14" width="24" height="2" fill="#F7A600"/>
                    <text x="12" y="10" textAnchor="middle" fontSize="8" fontWeight="bold" fill="#1A1F71">VISA</text>
                  </svg>
                </div>
                
                {/* MasterCard */}
                <div className="payment-badge h-8 w-12 bg-white rounded flex items-center justify-center p-1">
                  <svg viewBox="0 0 24 16" className="h-6 w-8">
                    <rect width="24" height="16" rx="2" fill="white"/>
                    <circle cx="8" cy="8" r="6" fill="#EB001B"/>
                    <circle cx="16" cy="8" r="6" fill="#F79E1B"/>
                    <path d="M12 2C8.5 2 5.5 4.5 5.5 8s3 6 6.5 6 6.5-3.5 6.5-6-3-6-6.5-6z" fill="white"/>
                    <path d="M12 2C15.5 2 18.5 4.5 18.5 8s-3 6-6.5 6-6.5-3.5-6.5-6 3-6 6.5-6z" fill="white"/>
                  </svg>
                </div>
                
                {/* PayPal */}
                <div className="payment-badge h-8 w-12 bg-white rounded flex items-center justify-center p-1">
                  <svg viewBox="0 0 24 16" className="h-6 w-8">
                    <rect width="24" height="16" rx="2" fill="white"/>
                    <g transform="translate(2, 2)">
                      <path d="M8.5 1.5c-1.5 0-2.5 1-2.5 2.5s1 2.5 2.5 2.5h1.5l1-4h-2.5z" fill="#0070BA"/>
                      <path d="M6 1.5c-1.5 0-2.5 1-2.5 2.5s1 2.5 2.5 2.5h1.5l1-4h-2.5z" fill="#009CDE"/>
                    </g>
                  </svg>
                </div>
                
                {/* Square */}
                <div className="payment-badge h-8 w-12 bg-white rounded flex items-center justify-center p-1">
                  <svg viewBox="0 0 24 16" className="h-6 w-8">
                    <rect width="24" height="16" rx="2" fill="white"/>
                    <rect x="4" y="4" width="16" height="8" rx="1" fill="#3E3E3E"/>
                    <rect x="6" y="6" width="12" height="4" rx="0.5" fill="white"/>
                    <rect x="8" y="8" width="8" height="0.5" fill="#3E3E3E"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
