'use client';

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid, LineChart, Line } from 'recharts';
import { formatCurrency, getCategoryColor } from '@/lib/utils';

interface CategoryData {
    category: string;
    total: number;
    count: number;
    percentage: number;
}

interface CashflowData {
    date: string;
    income: number;
    expenses: number;
    balance: number;
}

interface DashboardData {
    current_month: {
        month: string;
        total_income: number;
        total_expenses: number;
        net_savings: number;
        categories: CategoryData[];
    };
    cashflow_trend: CashflowData[];
    top_categories: CategoryData[];
}

interface DashboardChartsProps {
    data: DashboardData;
}

export default function DashboardCharts({ data }: DashboardChartsProps) {
    const { current_month, cashflow_trend, top_categories } = data;

    // Prepare data for pie chart
    const pieData = current_month.categories.map(cat => ({
        name: cat.category,
        value: cat.total,
    }));

    // Prepare data for income vs expenses
    const incomeExpenseData = [
        { name: 'Income', amount: current_month.total_income, fill: '#22c55e' },
        { name: 'Expenses', amount: current_month.total_expenses, fill: '#ef4444' },
    ];

    return (
        <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="card bg-gradient-to-br from-green-500 to-emerald-600 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm opacity-90">Total Income</p>
                            <p className="text-3xl font-bold mt-2">{formatCurrency(current_month.total_income)}</p>
                        </div>
                        <svg className="w-12 h-12 opacity-50" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clipRule="evenodd" />
                        </svg>
                    </div>
                </div>

                <div className="card bg-gradient-to-br from-red-500 to-pink-600 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm opacity-90">Total Expenses</p>
                            <p className="text-3xl font-bold mt-2">{formatCurrency(current_month.total_expenses)}</p>
                        </div>
                        <svg className="w-12 h-12 opacity-50" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM7 9a1 1 0 000 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                        </svg>
                    </div>
                </div>

                <div className={`card bg-gradient-to-br ${current_month.net_savings >= 0 ? 'from-blue-500 to-purple-600' : 'from-orange-500 to-red-600'} text-white`}>
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm opacity-90">Net Savings</p>
                            <p className="text-3xl font-bold mt-2">{formatCurrency(current_month.net_savings)}</p>
                        </div>
                        <svg className="w-12 h-12 opacity-50" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
                        </svg>
                    </div>
                </div>
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Category Breakdown */}
                <div className="card">
                    <h3 className="text-xl font-bold mb-4">Spending by Category</h3>
                    {pieData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                                    outerRadius={80}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {pieData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={getCategoryColor(entry.name)} />
                                    ))}
                                </Pie>
                                <Tooltip formatter={(value: number) => formatCurrency(value)} />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    ) : (
                        <p className="text-gray-500 text-center py-12">No data available</p>
                    )}
                </div>

                {/* Income vs Expenses */}
                <div className="card">
                    <h3 className="text-xl font-bold mb-4">Income vs Expenses</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={incomeExpenseData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip formatter={(value: number) => formatCurrency(value)} />
                            <Bar dataKey="amount" fill="#8884d8">
                                {incomeExpenseData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.fill} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Cashflow Trend */}
                <div className="card lg:col-span-2">
                    <h3 className="text-xl font-bold mb-4">Cashflow Trend</h3>
                    {cashflow_trend.length > 0 ? (
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={cashflow_trend}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="date" />
                                <YAxis />
                                <Tooltip formatter={(value: number) => formatCurrency(value)} />
                                <Legend />
                                <Line type="monotone" dataKey="income" stroke="#22c55e" strokeWidth={2} name="Income" />
                                <Line type="monotone" dataKey="expenses" stroke="#ef4444" strokeWidth={2} name="Expenses" />
                                <Line type="monotone" dataKey="balance" stroke="#3b82f6" strokeWidth={2} name="Balance" />
                            </LineChart>
                        </ResponsiveContainer>
                    ) : (
                        <p className="text-gray-500 text-center py-12">No data available</p>
                    )}
                </div>
            </div>
        </div>
    );
}
