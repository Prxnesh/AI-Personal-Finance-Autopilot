'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { transactionAPI } from '@/lib/api';
import { formatCurrency, formatDate, getCategoryColor } from '@/lib/utils';

const CATEGORIES = ['Food', 'Rent', 'Transport', 'Shopping', 'Subscriptions', 'Utilities', 'Income', 'Entertainment', 'Healthcare', 'Education', 'Other'];

export default function TransactionsPage() {
    const { user, loading: authLoading } = useAuth();
    const router = useRouter();
    const [transactions, setTransactions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [editingId, setEditingId] = useState<number | null>(null);
    const [selectedCategory, setSelectedCategory] = useState('');

    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/login');
        } else if (user) {
            loadTransactions();
        }
    }, [user, authLoading, router]);

    const loadTransactions = async () => {
        try {
            const response = await transactionAPI.getAll(100, 0);
            setTransactions(response.data);
        } catch (err) {
            console.error('Failed to load transactions:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleEditCategory = (transaction: any) => {
        setEditingId(transaction.id);
        setSelectedCategory(transaction.category);
    };

    const handleSaveCategory = async (transactionId: number) => {
        try {
            await transactionAPI.updateCategory(transactionId, selectedCategory);
            await loadTransactions();
            setEditingId(null);
        } catch (err) {
            console.error('Failed to update category:', err);
        }
    };

    const handleCancelEdit = () => {
        setEditingId(null);
        setSelectedCategory('');
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
                <h1 className="text-4xl font-bold gradient-text">Transactions</h1>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                    View and categorize your transactions
                </p>
            </div>

            {loading ? (
                <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                    <p className="mt-4 text-gray-600 dark:text-gray-400">Loading transactions...</p>
                </div>
            ) : transactions.length === 0 ? (
                <div className="card text-center py-12">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <h3 className="mt-4 text-xl font-semibold text-gray-700 dark:text-gray-300">
                        No transactions yet
                    </h3>
                    <p className="mt-2 text-gray-500 dark:text-gray-400">
                        Upload a bank statement to see your transactions
                    </p>
                </div>
            ) : (
                <div className="card overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                            <thead className="bg-gray-50 dark:bg-gray-800">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Date</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Description</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Category</th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Amount</th>
                                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                                {transactions.map((transaction) => (
                                    <tr key={transaction.id} className="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                                            {formatDate(transaction.date)}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">
                                            {transaction.description}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                                            {editingId === transaction.id ? (
                                                <select
                                                    value={selectedCategory}
                                                    onChange={(e) => setSelectedCategory(e.target.value)}
                                                    className="input text-sm py-1"
                                                >
                                                    {CATEGORIES.map((cat) => (
                                                        <option key={cat} value={cat}>{cat}</option>
                                                    ))}
                                                </select>
                                            ) : (
                                                <span
                                                    className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium"
                                                    style={{
                                                        backgroundColor: getCategoryColor(transaction.category) + '20',
                                                        color: getCategoryColor(transaction.category),
                                                    }}
                                                >
                                                    {transaction.category}
                                                    {transaction.user_overridden && (
                                                        <span className="ml-1" title="Manually categorized">✏️</span>
                                                    )}
                                                </span>
                                            )}
                                        </td>
                                        <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-semibold ${transaction.is_credit ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                                            }`}>
                                            {transaction.is_credit ? '+' : '-'}{formatCurrency(transaction.amount)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-center text-sm">
                                            {editingId === transaction.id ? (
                                                <div className="flex justify-center space-x-2">
                                                    <button
                                                        onClick={() => handleSaveCategory(transaction.id)}
                                                        className="text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300"
                                                    >
                                                        Save
                                                    </button>
                                                    <button
                                                        onClick={handleCancelEdit}
                                                        className="text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-300"
                                                    >
                                                        Cancel
                                                    </button>
                                                </div>
                                            ) : (
                                                <button
                                                    onClick={() => handleEditCategory(transaction)}
                                                    className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                                                >
                                                    Edit
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
