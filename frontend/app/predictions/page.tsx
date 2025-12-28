'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { predictionsAPI } from '@/lib/api';
import { formatCurrency, formatDate, getConfidenceColor, getConfidenceBadge } from '@/lib/utils';

export default function PredictionsPage() {
    const { user, loading: authLoading } = useAuth();
    const router = useRouter();
    const [predictions, setPredictions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/login');
        } else if (user) {
            loadPredictions();
        }
    }, [user, authLoading, router]);

    const loadPredictions = async () => {
        try {
            const response = await predictionsAPI.getAll();
            setPredictions(response.data);
        } catch (err) {
            console.error('Failed to load predictions:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleGenerate = async () => {
        setGenerating(true);
        try {
            await predictionsAPI.generate();
            setTimeout(async () => {
                await loadPredictions();
                setGenerating(false);
            }, 2000);
        } catch (err) {
            console.error('Failed to generate predictions:', err);
            setGenerating(false);
        }
    };

    const getPredictionIcon = (type: string) => {
        switch (type) {
            case 'expense':
                return '📉';
            case 'income':
                return '📈';
            case 'savings':
                return '💰';
            case 'category':
                return '📊';
            default:
                return '🔮';
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
                    <h1 className="text-4xl font-bold gradient-text">Predictions</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        AI-powered forecasts of your future finances
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
                        '🔄 Regenerate Predictions'
                    )}
                </button>
            </div>

            {loading ? (
                <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                    <p className="mt-4 text-gray-600 dark:text-gray-400">Loading predictions...</p>
                </div>
            ) : predictions.length === 0 ? (
                <div className="card text-center py-12">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <h3 className="mt-4 text-xl font-semibold text-gray-700 dark:text-gray-300">
                        No predictions yet
                    </h3>
                    <p className="mt-2 text-gray-500 dark:text-gray-400">
                        Upload transactions and click "Generate Predictions" to see forecasts
                    </p>
                </div>
            ) : (
                <div className="space-y-8">
                    {/* Main Predictions */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {predictions
                            .filter(p => ['expense', 'income', 'savings'].includes(p.prediction_type))
                            .map((prediction) => (
                                <div
                                    key={prediction.id}
                                    className={`card ${prediction.prediction_type === 'income'
                                            ? 'bg-gradient-to-br from-green-500 to-emerald-600'
                                            : prediction.prediction_type === 'savings'
                                                ? 'bg-gradient-to-br from-blue-500 to-purple-600'
                                                : 'bg-gradient-to-br from-orange-500 to-red-600'
                                        } text-white`}
                                >
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-sm opacity-90 capitalize">{prediction.prediction_type}</p>
                                            <p className="text-3xl font-bold mt-2">{formatCurrency(prediction.predicted_value)}</p>
                                            <p className="text-xs opacity-75 mt-1">
                                                {new Date(prediction.target_month).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                                            </p>
                                        </div>
                                        <div className="text-4xl opacity-50">{getPredictionIcon(prediction.prediction_type)}</div>
                                    </div>
                                    <div className="mt-4 pt-4 border-t border-white/20">
                                        <p className="text-xs opacity-90">{prediction.method_used}</p>
                                    </div>
                                </div>
                            ))}
                    </div>

                    {/* Detailed Explanations */}
                    <div className="grid grid-cols-1 gap-6">
                        {predictions.map((prediction) => (
                            <div key={prediction.id} className="card">
                                <div className="flex items-start space-x-4">
                                    <div className="text-4xl">{getPredictionIcon(prediction.prediction_type)}</div>
                                    <div className="flex-1">
                                        <div className="flex items-start justify-between">
                                            <div>
                                                <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 capitalize">
                                                    {prediction.prediction_type} Prediction
                                                    {prediction.category && `: ${prediction.category}`}
                                                </h3>
                                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                                    {new Date(prediction.target_month).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                                                </p>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                                                    {formatCurrency(prediction.predicted_value)}
                                                </p>
                                                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getConfidenceColor(prediction.confidence)}`}>
                                                    {getConfidenceBadge(prediction.confidence)} Confidence
                                                </span>
                                            </div>
                                        </div>

                                        <div className="mt-4 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                                            <h4 className="text-sm font-semibold text-purple-900 dark:text-purple-200 mb-2">
                                                📊 Explanation
                                            </h4>
                                            <p className="text-sm text-purple-800 dark:text-purple-300">
                                                {prediction.explanation}
                                            </p>
                                        </div>

                                        <div className="mt-3 flex flex-wrap gap-2">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200">
                                                {prediction.method_used}
                                            </span>
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200">
                                                {Math.round(prediction.confidence * 100)}% confidence
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
