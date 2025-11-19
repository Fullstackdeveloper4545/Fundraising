import Link from "next/link";
import { CampaignAPI } from "@/lib/api";
import type { Campaign } from "@/types/api";

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

export default async function CampaignsPage() {
  let featuredItems: Campaign[] = [];
  let regularItems: Campaign[] = [];
  try {
    const [featuredCampaigns, regularCampaigns] = await Promise.all([
      CampaignAPI.featured(6),
      CampaignAPI.list({ status: "active", limit: 24 })
    ]);
    featuredItems = Array.isArray(featuredCampaigns) ? featuredCampaigns : [];
    regularItems = Array.isArray(regularCampaigns) ? regularCampaigns : [];
  } catch (error) {
    console.error("CampaignsPage: failed to load campaigns", error);
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Active Campaigns</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Support amazing student initiatives and help them achieve their fundraising goals
          </p>
        </div>

        {/* Featured Campaigns Section */}
        {featuredItems.length > 0 && (
          <div className="mb-16">
            <div className="flex items-center justify-between mb-8">
    <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">⭐ Featured Campaigns</h2>
                <p className="text-gray-600">Hand-picked campaigns that deserve special attention</p>
              </div>
              <Link 
                href="/spotlight" 
                className="text-[#00AFF0] hover:text-[#0099D6] font-semibold flex items-center gap-2"
              >
                View Spotlight <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>
            
            <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
              {featuredItems.map((campaign: Campaign) => (
                <Link 
                  href={`/campaign/${campaign.id}`} 
                  key={campaign.id} 
                  className="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 overflow-hidden border-2 border-yellow-200"
                >
                  {/* Featured Badge */}
                  <div className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-4 py-2 text-center font-semibold">
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
          </div>
        )}

        {/* All Campaigns Section */}
        <div>
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-bold text-gray-900">All Campaigns</h2>
            <div className="text-sm text-gray-600">
              {regularItems.length} active campaign{regularItems.length !== 1 ? 's' : ''}
            </div>
          </div>
          
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {regularItems.length === 0 ? (
              <div className="col-span-full text-center py-12">
                <div className="bg-white rounded-2xl shadow-lg p-8">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">No Active Campaigns</h3>
                  <p className="text-gray-600 mb-6">Check back soon for new fundraising campaigns!</p>
                  <Link 
                    href="/create-campaign" 
                    className="bg-[#00AFF0] text-white px-6 py-3 rounded-lg font-semibold hover:bg-[#0099D6] transition-colors"
                  >
                    Create First Campaign
                  </Link>
                </div>
              </div>
            ) : (
              regularItems.map((campaign: Campaign) => (
                <Link 
                  href={`/campaign/${campaign.id}`} 
                  key={campaign.id} 
                  className="group bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-300 hover:-translate-y-1 overflow-hidden border border-gray-200"
                >
                  {/* Campaign Image */}
                  <div className="relative">
                    {campaign.image_url ? (
                      <img 
                        alt={campaign.title} 
                        src={getImageUrl(campaign.image_url) || ''} 
                        className="w-full h-40 object-cover" 
                      />
                    ) : (
                      <div className="w-full h-40 bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                        <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                        </svg>
                      </div>
                    )}
                  </div>
                  
                  {/* Campaign Info */}
                  <div className="p-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-1 group-hover:text-[#00AFF0] transition-colors">
                      {campaign.title}
                    </h3>
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">{campaign.description}</p>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">${campaign.current_amount.toLocaleString()} raised</span>
                        <span className="text-gray-600">Goal ${campaign.goal_amount.toLocaleString()}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-[#00AFF0] h-2 rounded-full transition-all duration-500" 
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
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
