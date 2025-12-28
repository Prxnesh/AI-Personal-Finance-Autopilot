'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { recommendationsAPI } from '@/lib/api';
import { formatCurrency, getConfidenceColor, getConfidenceBadge } from '@/lib/utils';

export default function RecommendationsPage() {
    const { user, loading: authLoading } = useAuth();
    const router = useRouter();
    const [recommendations, setRecommendations] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/login');
        } else if (user) {
            loadRecommendations();
        }
    }, [user, authLoading, router]);

    const loadRecommendations = async () => {
        try {
            const response = await recommendationsAPI.getAll();
            setRecommendations(response.data);
        } catch (err) {
            console.error('Failed to load recommendations:', err);
        } finally {
            setLoading(false);
        }
    };

    const getRecommendationIcon = (type: string) => {
        switch (type) {
            case 'budget_limit':
                return '🎯';
            case 'subscription_review':
                return '🔄';
            case 'safe_to_spend':
                return '💳';
            case 'savings_opportunity':
                return '💰';
            default:
                return '💡';
        }
    };

    const getRecommendationColor = (type: string) => {
        switch (type) {
            case 'budget_limit':
                return 'from-blue-500 to-indigo-600';
            case 'subscription_review':
                return 'from-yellow-500 to-orange-600';
            case 'safe_to_spend':
                return 'from-green-500 to-emerald-600';
            case 'savings_opportunity':
                return 'from-purple-500 to-pink-600';
            default:
                return 'from-gray-500 to-gray-600';
        }
    };

    if (authLoading || !user) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                    <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-4xl font-bold gradient-text">Recommendations</h1>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                    Actionable advice to improve your financial health
                </p>
            </div>

            {loading ? (
                <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                    <p className="mt-4 text-gray-600 dark:text-gray-400">Loading recommendations...</p>
                </div>
            ) : recommendations.length === 0 ? (
                <div className="card text-center py-12">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <h3 className="mt-4 text-xl font-semibold text-gray-700 dark:text-gray-300">
                        No recommendations yet
                    </h3>
                    <p className="mt-2 text-gray-500 dark:text-gray-400">
                        Upload transactions to receive personalized financial advice
                    </p>
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-6">
                    {recommendations.map((rec, index) => (
                        <div key={index} className="card hover:shadow-2xl transition-shadow">
                            <div className="flex items-start space-x-4">
                                <div className={`flex-shrink-0 w-16 h-16 bg-gradient-to-br ${getRecommendationColor(rec.type)} rounded-xl flex items-center justify-center text-3xl`}>
                                    {getRecommendationIcon(rec.type)}
                                </div>

                                <div className="flex-1">
                                    <div className="flex items-start justify-between">
                                        <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                                            {rec.title}
                                        </h3>
                                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getConfidenceColor(rec.confidence)}`}>
                                            {getConfidenceBadge(rec.confidence)} Confidence
                                        </span>
                                    </div>

                                    <p className="mt-2 text-gray-700 dark:text-gray-300">
                                        {rec.description}
                                    </p>

                                    <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                                        <h4 className="text-sm font-semibold text-green-900 dark:text-green-200 mb-2 flex items-center">
                                            <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                                            </svg>
                                            Why this matters
                                        </h4>
                                        <p className="text-sm text-green-800 dark:text-green-300">
                                            {rec.rationale}
                                        </p>
                                    </div>

                                    {rec.estimated_impact > 0 && (
                                        <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                                            <div className="flex items-center justify-between">
                                                <span className="text-sm font-medium text-blue-900 dark:text-blue-200">
                                                    💵 Estimated Impact
                                                </span>
                                                <span className="text-lg font-bold text-blue-900 dark:text-blue-100">
                                                    {formatCurrency(rec.estimated_impact)}/year
                                                </span>
                                            </div>
                                        </div>
                                    )}

                                    <div className="mt-4 flex flex-wrap gap-2">
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200 capitalize">
                                            {rec.type.replace('_', ' ')}
                                        </span>
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200">
                                            {Math.round(rec.confidence * 100)}% confidence
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
