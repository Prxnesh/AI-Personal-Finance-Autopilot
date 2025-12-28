'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { dashboardAPI, insightsAPI, predictionsAPI } from '@/lib/api';
import FileUpload from '@/components/FileUpload';
import DashboardCharts from '@/components/DashboardCharts';

export default function DashboardPage() {
    const { user, loading: authLoading } = useAuth();
    const router = useRouter();
    const [dashboardData, setDashboardData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/login');
        } else if (user) {
            loadDashboard();
        }
    }, [user, authLoading, router]);

    const loadDashboard = async () => {
        try {
            setLoading(true);
            const response = await dashboardAPI.getData();
            setDashboardData(response.data);
        } catch (err: any) {
            if (err.response?.status !== 401) {
                setError('Failed to load dashboard data');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleUploadSuccess = async () => {
        // Refresh dashboard and regenerate insights/predictions
        await loadDashboard();

        // Trigger insights and predictions generation in background
        try {
            await insightsAPI.generate();
            await predictionsAPI.generate();
        } catch (err) {
            console.error('Failed to generate insights/predictions:', err);
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
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-4xl font-bold gradient-text">Dashboard</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        Your financial overview at a glance
                    </p>
                </div>
            </div>

            <FileUpload onUploadSuccess={handleUploadSuccess} />

            {loading ? (
                <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                    <p className="mt-4 text-gray-600 dark:text-gray-400">Loading dashboard...</p>
                </div>
            ) : error ? (
                <div className="card bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                    <p className="text-red-800 dark:text-red-200">{error}</p>
                </div>
            ) : dashboardData ? (
                <DashboardCharts data={dashboardData} />
            ) : (
                <div className="card text-center py-12">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <h3 className="mt-4 text-xl font-semibold text-gray-700 dark:text-gray-300">
                        No data yet
                    </h3>
                    <p className="mt-2 text-gray-500 dark:text-gray-400">
                        Upload your bank statement to get started
                    </p>
                </div>
            )}
        </div>
    );
}
