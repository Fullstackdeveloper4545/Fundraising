import React from "react";
import Link from "next/link";
import { CampaignAPI } from "@/lib/api";
import type { Campaign } from "@/types/api";
import HomePageClient from "./HomePageClient";

export const dynamic = "force-dynamic";
export const revalidate = 0;

// Helper function to construct proper image URLs
function getImageUrl(imageUrl: string | null | undefined): string | null {
  if (!imageUrl) return null;
  
  // If it's already a full URL, return as is
  if (imageUrl.startsWith('http')) return imageUrl;
  
  // If it's a relative path, prepend the backend base URL
  if (imageUrl.startsWith('/uploads/')) {
    const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.replace('/api/v1', '') || 'http://0.0.0.0:8000';
    return `${backendUrl}${imageUrl}`;
  }
  
  return imageUrl;
}

export default async function HomePage() {
  let featuredItems: Campaign[] = [];
  try {
    const featuredCampaigns = await CampaignAPI.featured(3);
    featuredItems = Array.isArray(featuredCampaigns) ? featuredCampaigns : [];
  } catch (error) {
    console.error("HomePage: failed to load featured campaigns", error);
  }

  return (
    <div className="min-h-screen bg-white">

      {/* Hero Section */}
      <section className="relative bg-gradient-to-b from-green-50 to-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-5xl font-bold text-gray-900 mb-6">
                Need Funds For Your <span className="text-[#00AFF0]">Student Goals</span>?
              </h1>
              <p className="text-xl text-gray-600 mb-8">
                Raise money for education, projects, and dreams with the support of your community.
              </p>
              <Link 
                href="/create-campaign"
                className="btn-primary inline-block px-8 py-4 text-lg"
              >
                Start Campaign
              </Link>
            </div>
            <div className="relative">
              <div className="bg-white rounded-2xl shadow-2xl p-8">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-[#00AFF0] bg-opacity-10 rounded-full flex items-center justify-center mr-4">
                    <span className="text-[#00AFF0] font-bold">🎓</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">Education Fund</h3>
                    <p className="text-sm text-gray-600">STUDENT</p>
                  </div>
                </div>
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>$2,500 raised</span>
                    <span>Goal $5,000</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-[#00AFF0] h-2 rounded-full" style={{width: '50%'}}></div>
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900 mb-2">50% Funded</div>
                  <div className="text-sm text-gray-600">127 supporters</div>
                </div>
              </div>
          </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-[#00AFF0] bg-opacity-10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-[#00AFF0] text-xl">💰</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">0% Platform Fee</h3>
              <p className="text-sm text-gray-600">Keep 100% of donations</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-[#00AFF0] bg-opacity-10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-[#00AFF0] text-xl">⚡</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Quick Disbursal</h3>
              <p className="text-sm text-gray-600">Fast fund transfers</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-[#00AFF0] bg-opacity-10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-[#00AFF0] text-xl">👥</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">10,000+ Students</h3>
              <p className="text-sm text-gray-600">Successfully funded</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-[#00AFF0] bg-opacity-10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-[#00AFF0] text-xl">💰</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">$2M+ Raised</h3>
              <p className="text-sm text-gray-600">Total impact</p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Campaigns Section */}
      {featuredItems.length > 0 && (
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">⭐ Featured Campaigns</h2>
              <p className="text-xl text-gray-600">Hand-picked campaigns that deserve special attention</p>
            </div>
            
            <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
              {featuredItems.map((campaign: Campaign) => (
                <Link 
                  href={`/campaign/${campaign.id}`} 
                  key={campaign.id} 
                  className="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 overflow-hidden border border-gray-200"
                >
                  {/* Featured Badge */}
                  <div className="bg-[#00AFF0] text-white px-4 py-2 text-center font-semibold">
                    ⭐ Featured Campaign
                  </div>
                  
                  {/* Campaign Image */}
                  <div className="relative">
                    {campaign.image_url ? (
                      <img 
                        alt={campaign.title} 
                        src={getImageUrl(campaign.image_url) || ''} 
                        className="w-full h-48 object-cover" 
                      />
                    ) : (
                      <div className="w-full h-48 bg-gradient-to-br from-[#00AFF0] to-[#0099D6] flex items-center justify-center">
                        <svg className="w-12 h-12 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                        </svg>
                      </div>
                    )}
                  </div>
                  
                  {/* Campaign Info */}
                  <div className="p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-3 line-clamp-2 group-hover:text-[#00AFF0] transition-colors">
                      {campaign.title}
                    </h3>
                    <p className="text-gray-600 mb-4 line-clamp-2">{campaign.description}</p>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Raised</span>
                        <span className="font-semibold text-gray-900">${campaign.current_amount.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Goal</span>
                        <span className="font-semibold text-gray-900">${campaign.goal_amount.toLocaleString()}</span>
                      </div>
                      
                      {/* Progress Bar */}
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div 
                          className="bg-gradient-to-r from-[#00AFF0] to-[#0099D6] h-3 rounded-full transition-all duration-500" 
                          style={{ width: `${Math.min(100, campaign.progress_percentage)}%` }}
                        />
                      </div>
                      
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>{Math.round(campaign.progress_percentage)}% complete</span>
                        <span>{campaign.donor_count} donors</span>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
            
            <div className="text-center mt-12">
              <Link 
                href="/campaigns" 
                className="bg-[#00AFF0] text-white px-8 py-4 rounded-lg font-semibold hover:bg-[#0099D6] transition-colors inline-block"
                style={{ color: 'white' }}
              >
                View All Campaigns
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* Why Choose Us Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold text-gray-900 mb-6">
                You can Choose Student Fundraising with FundRise if
              </h2>
              <ul className="space-y-4 mb-8">
                <li className="flex items-center">
                  <div className="w-6 h-6 bg-[#00AFF0] bg-opacity-10 rounded-full flex items-center justify-center mr-3">
                    <span className="text-[#00AFF0] text-sm">✓</span>
                  </div>
                  <span className="text-gray-700">You need funds for education or projects</span>
                </li>
                <li className="flex items-center">
                  <div className="w-6 h-6 bg-[#00AFF0] bg-opacity-10 rounded-full flex items-center justify-center mr-3">
                    <span className="text-[#00AFF0] text-sm">✓</span>
                  </div>
                  <span className="text-gray-700">You have limited financial resources</span>
                </li>
                <li className="flex items-center">
                  <div className="w-6 h-6 bg-[#00AFF0] bg-opacity-10 rounded-full flex items-center justify-center mr-3">
                    <span className="text-[#00AFF0] text-sm">✓</span>
                  </div>
                  <span className="text-gray-700">Scholarships and grants are not enough</span>
                </li>
              </ul>
              <p className="text-gray-600 mb-6">
                Get financial support for your educational goals by raising funds with the help of donors, family, and friends online.
              </p>
              <Link 
                href="/partnership"
                className="border-2 border-[#00AFF0] text-[#00AFF0] px-6 py-3 rounded-lg font-semibold hover:bg-[#00AFF0] hover:text-white transition-colors inline-block text-center hover:!text-white no-underline hover:no-underline"
              >
                Partnership
              </Link>
            </div>
            <div className="relative">
              <div className="bg-white rounded-2xl shadow-xl p-6 max-w-sm mx-auto">
                <div className="text-center mb-4">
                  <div className="w-16 h-16 bg-[#00AFF0] bg-opacity-10 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-2xl">🎓</span>
                  </div>
                  <h3 className="font-semibold text-gray-900">Education Fund</h3>
                  <p className="text-sm text-gray-600">STUDENT</p>
                </div>
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>$4,900 raised</span>
                    <span>Goal $10,000</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-[#00AFF0] h-2 rounded-full" style={{width: '49%'}}></div>
        </div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-gray-900">49% Funded</div>
                  <div className="text-sm text-gray-600">89 supporters</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Campaign Categories */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Raise Funds For Your Student Goals
            </h2>
            <p className="text-xl text-gray-600">
              Get financial support for education, projects, and dreams with online fundraising.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-[#00AFF0] bg-opacity-10 rounded-lg flex items-center justify-center mb-4">
                <span className="text-[#00AFF0] text-xl">🎓</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Tuition Fees</h3>
              <p className="text-gray-600 mb-4">Raise funds for college tuition and educational expenses</p>
              <div className="text-sm text-[#00AFF0] font-semibold">Max Raised: $25,000</div>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-[#00AFF0] bg-opacity-10 rounded-lg flex items-center justify-center mb-4">
                <span className="text-[#00AFF0] text-xl">🔬</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Research Projects</h3>
              <p className="text-gray-600 mb-4">Fund your academic research and scientific projects</p>
              <div className="text-sm text-[#00AFF0] font-semibold">Max Raised: $15,000</div>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-[#00AFF0] bg-opacity-10 rounded-lg flex items-center justify-center mb-4">
                <span className="text-[#00AFF0] text-xl">🌍</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Study Abroad</h3>
              <p className="text-gray-600 mb-4">Support international education and exchange programs</p>
              <div className="text-sm text-[#00AFF0] font-semibold">Max Raised: $30,000</div>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-[#00AFF0] bg-opacity-10 rounded-lg flex items-center justify-center mb-4">
                <span className="text-[#00AFF0] text-xl">💻</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Tech Equipment</h3>
              <p className="text-gray-600 mb-4">Fund laptops, software, and technology needs</p>
              <div className="text-sm text-[#00AFF0] font-semibold">Max Raised: $8,000</div>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-[#00AFF0] bg-opacity-10 rounded-lg flex items-center justify-center mb-4">
                <span className="text-[#00AFF0] text-xl">🏃</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Sports & Activities</h3>
              <p className="text-gray-600 mb-4">Support athletic programs and extracurricular activities</p>
              <div className="text-sm text-[#00AFF0] font-semibold">Max Raised: $12,000</div>
            </div>
            
            <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-[#00AFF0] bg-opacity-10 rounded-lg flex items-center justify-center mb-4">
                <span className="text-[#00AFF0] text-xl">🎨</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Creative Projects</h3>
              <p className="text-gray-600 mb-4">Fund art, music, and creative student projects</p>
              <div className="text-sm text-[#00AFF0] font-semibold">Max Raised: $6,000</div>
            </div>
          </div>
        </div>
      </section>

      {/* Lead Magnet */}
      <section className="py-12 bg-[#00AFF0]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-4">
                <span className="text-white text-lg">📚</span>
              </div>
              <span className="text-white text-lg font-medium">
                Unlock the secrets of student fundraising - Get your free guide now!
              </span>
            </div>
            <button className="bg-white text-[#00AFF0] px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
              Download Now
            </button>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              How does Student Fundraising on FundRise work?
            </h2>
            <p className="text-xl text-gray-600">
              Three simple steps to get the support you need for your educational goals.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="text-center">
              <div className="w-16 h-16 bg-[#00AFF0] text-white rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold">
                1
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Start a free fundraiser</h3>
              <p className="text-gray-600">Create your campaign by filling in all the relevant details about your educational goals and funding needs.</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-[#00AFF0] text-white rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold">
                2
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Share Your Fundraiser</h3>
              <p className="text-gray-600">Share your fundraiser with friends, family, and your network to raise funds quickly and effectively.</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-[#00AFF0] text-white rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold">
                3
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Withdraw All Donations</h3>
              <p className="text-gray-600">Withdraw all the money you receive at any point in your fundraising journey to support your education.</p>
            </div>
          </div>
          
          <div className="text-center">
            <p className="text-lg text-gray-700 mb-8">
              Your fundraising journey is successful! We wish you success in your educational pursuits!
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                href="/create-campaign"
                className="btn-primary inline-block px-8 py-4 text-lg"
              >
                START CAMPAIGN
              </Link>
              <Link 
                href="/partnership"
                className="border-2 border-[#00AFF0] text-[#00AFF0] px-8 py-4 rounded-lg text-lg font-semibold hover:bg-[#00AFF0] hover:text-white transition-colors inline-block text-center hover:!text-white no-underline hover:no-underline"
              >
                Partnership
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Why Choose Us */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Why Fundraise With FundRise?
            </h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="text-center">
              <div className="w-16 h-16 bg-[#00AFF0] bg-opacity-10 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-[#00AFF0] text-2xl">💰</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">0% Platform Fee</h3>
              <p className="text-gray-600">Keep 100% of the donations you receive for your educational goals.</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-[#00AFF0] bg-opacity-10 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-[#00AFF0] text-2xl">📱</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Free Mobile App</h3>
              <p className="text-gray-600">Manage your fundraising campaign on the go with our mobile app for iOS and Android.</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-[#00AFF0] bg-opacity-10 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-[#00AFF0] text-2xl">👥</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">50,000+ Donor Community</h3>
              <p className="text-gray-600">Access our large community of supporters who believe in student success.</p>
            </div>
          </div>
          
          <div className="text-center">
            <div>
              <Link 
                href="/create-campaign"
                className="btn-primary inline-block px-8 py-4 text-lg"
              >
                START CAMPAIGN
              </Link>
            </div>
          </div>
        </div>
      </section>

      <HomePageClient />

    </div>
  );
}
