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

export default async function SpotlightPage() {
  let items: Campaign[] = [];
  try {
    const campaigns = await CampaignAPI.spotlight(6);
    items = Array.isArray(campaigns) ? campaigns : [];
  } catch (error) {
    console.error("SpotlightPage: failed to load spotlight campaigns", error);
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Header Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">🌟 Student Spotlight</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Celebrating our top-performing student fundraisers and their incredible achievements
          </p>
        </div>

        {/* Spotlight Campaigns Grid */}
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {items.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <div className="bg-gray-50 rounded-2xl p-8 border border-gray-200">
                <div className="w-16 h-16 bg-[#00AFF0] bg-opacity-10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-[#00AFF0]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No Spotlight Campaigns Yet</h3>
                <p className="text-gray-600">Check back soon to see our top-performing student fundraisers!</p>
              </div>
            </div>
          ) : (
            items.map((campaign: Campaign, index: number) => (
              <Link 
                href={`/campaign/${campaign.id}`} 
                key={campaign.id} 
                className="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 overflow-hidden border border-gray-200"
              >
                {/* Ranking Badge */}
                <div className="bg-[#00AFF0] text-white px-4 py-2 text-center font-semibold">
                  #{index + 1} Top Performer
                </div>

                {/* Campaign Image */}
                <div className="mb-4">
                  {campaign.image_url ? (
                    <img 
                      alt={campaign.title} 
                      src={getImageUrl(campaign.image_url) || ''} 
                      className="w-full h-32 object-cover rounded-xl" 
                    />
                  ) : (
                    <div className="w-full h-32 bg-white/20 rounded-xl flex items-center justify-center">
                      <svg className="w-8 h-8 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Donors</span>
                      <span className="font-semibold text-gray-900">{campaign.donor_count}</span>
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
            ))
          )}
        </div>

        {/* Call to Action */}
        {items.length > 0 && (
          <div className="text-center mt-12">
            <div className="bg-gray-50 rounded-2xl p-8 border border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Want to be featured in the spotlight?</h2>
              <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
                Create an amazing campaign, engage your community, and watch your fundraising goals come to life. 
                Top performers automatically appear in our spotlight!
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link 
                  href="/create-campaign" 
                  className="bg-[#00AFF0] text-white px-8 py-3 rounded-lg font-semibold hover:bg-[#0099D6] transition-colors"
                  style={{ color: 'white' }}
                >
                  Create Campaign
                </Link>
                <Link 
                  href="/campaigns" 
                  className="border-2 border-[#00AFF0] text-white bg-[#00AFF0] px-8 py-3 rounded-lg font-semibold hover:bg-[#0099D6] hover:border-[#0099D6] transition-colors"
                  style={{ color: 'white' }}
                >
                  Browse All Campaigns
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


