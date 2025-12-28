'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { insightsAPI } from '@/lib/api';
import { formatCurrency, formatDate, getConfidenceColor, getConfidenceBadge } from '@/lib/utils';

export default function InsightsPage() {
    const { user, loading: authLoading } = useAuth();
    const router = useRouter();
    const [insights, setInsights] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/login');
        } else if (user) {
            loadInsights();
        }
    }, [user, authLoading, router]);

    const loadInsights = async () => {
        try {
            const response = await insightsAPI.getAll();
            setInsights(response.data);
        } catch (err) {
            console.error('Failed to load insights:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleGenerate = async () => {
        setGenerating(true);
        try {
            await insightsAPI.generate();
            // Wait a bit for processing
            setTimeout(async () => {
                await loadInsights();
                setGenerating(false);
            }, 2000);
        } catch (err) {
            console.error('Failed to generate insights:', err);
            setGenerating(false);
        }
    };

    const getInsightIcon = (type: string) => {
        switch (type) {
            case 'anomaly':
                return '⚠️';
            case 'trend':
                return '📈';
            case 'subscription':
                return '🔄';
            case 'pattern':
                return '🎯';
            default:
                return '💡';
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
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-4xl font-bold gradient-text">AI Insights</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        Discover patterns and anomalies in your spending
                    </p>
                </div>
                <button
                    onClick={handleGenerate}
                    disabled={generating}
                    className="btn btn-primary"
                >
                    {generating ? (
                        <span className="flex items-center">
                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Generating...
                        </span>
                    ) : (
                        '🔄 Regenerate Insights'
                    )}
                </button>
            </div>

            {loading ? (
                <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                    <p className="mt-4 text-gray-600 dark:text-gray-400">Loading insights...</p>
                </div>
            ) : insights.length === 0 ? (
                <div className="card text-center py-12">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    <h3 className="mt-4 text-xl font-semibold text-gray-700 dark:text-gray-300">
                        No insights yet
                    </h3>
                    <p className="mt-2 text-gray-500 dark:text-gray-400">
                        Upload transactions and click "Generate Insights" to discover patterns
                    </p>
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-6">
                    {insights.map((insight) => (
                        <div key={insight.id} className="card hover:shadow-2xl transition-shadow">
                            <div className="flex items-start space-x-4">
                                <div className="text-4xl">{getInsightIcon(insight.insight_type)}</div>
                                <div className="flex-1">
                                    <div className="flex items-start justify-between">
                                        <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                                            {insight.title}
                                        </h3>
                                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getConfidenceColor(insight.confidence)}`}>
                                            {getConfidenceBadge(insight.confidence)} Confidence
                                        </span>
                                    </div>

                                    <p className="mt-2 text-gray-700 dark:text-gray-300">
                                        {insight.description}
                                    </p>

                                    <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                                        <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-200 mb-2">
                                            💭 AI Reasoning
                                        </h4>
                                        <p className="text-sm text-blue-800 dark:text-blue-300">
                                            {insight.reasoning}
                                        </p>
                                    </div>

                                    {insight.period_start && insight.period_end && (
                                        <p className="mt-3 text-xs text-gray-500 dark:text-gray-400">
                                            Period: {formatDate(insight.period_start)} - {formatDate(insight.period_end)}
                                        </p>
                                    )}

                                    <div className="mt-3 flex flex-wrap gap-2">
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200">
                                            {insight.insight_type}
                                        </span>
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200">
                                            {Math.round(insight.confidence * 100)}% confidence
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
