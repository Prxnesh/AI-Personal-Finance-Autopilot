/**
 * Format a number as Indian Rupees currency
 * Uses Indian numbering system (lakhs, crores)
 */
export function formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(amount);
}

export function formatDate(date: string): string {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    });
}

export function formatPercentage(value: number): string {
    return `${value.toFixed(1)}%`;
}

export function getCategoryColor(category: string): string {
    const colors: Record<string, string> = {
        Food: '#f59e0b',
        Rent: '#8b5cf6',
        Transport: '#3b82f6',
        Shopping: '#ec4899',
        Subscriptions: '#10b981',
        Utilities: '#6366f1',
        Income: '#22c55e',
        Entertainment: '#f97316',
        Healthcare: '#ef4444',
        Education: '#06b6d4',
        Other: '#6b7280',
    };
    return colors[category] || colors.Other;
}

export function getConfidenceColor(confidence: number): string {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
}

export function getConfidenceBadge(confidence: number): string {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
}
