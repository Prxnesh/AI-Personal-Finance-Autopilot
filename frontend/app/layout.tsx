import { AuthProvider } from '@/lib/auth-context';
import Navbar from '@/components/Navbar';
import '@/styles/globals.css';

export const metadata = {
    title: 'AI Personal Finance Autopilot',
    description: 'AI-powered personal finance management',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className="min-h-screen bg-gray-50 dark:bg-gray-900">
                <AuthProvider>
                    <Navbar />
                    <main className="container mx-auto px-6 py-8">
                        {children}
                    </main>
                </AuthProvider>
            </body>
        </html>
    );
}
