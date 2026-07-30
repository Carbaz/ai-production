"use client"

import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { useAuth } from '@clerk/nextjs';
import { fetchEventSource } from '@microsoft/fetch-event-source';

export default function Product() {
    const { getToken } = useAuth();
    const [idea, setIdea] = useState<string>('…loading');
    const [error, setError] = useState(false);

    const generateIdea = async () => {
        let buffer = '';
        setIdea('…loading');
        setError(false);
        const jwt = await getToken();
        if (!jwt) {
            setIdea('Authentication required');
            return;
        }

        try {
            await fetchEventSource('/api', {
                headers: { Authorization: `Bearer ${jwt}` },
                onmessage(ev) {
                    buffer += ev.data;
                    setIdea(buffer);
                },
                onerror(err) {
                    console.error('SSE error:', err);
                    setError(true);
                    setIdea('Unable to generate an idea. Please try again.');
                    throw err;
                }
            });
        } catch (err) {
            console.error('SSE request failed:', err);
        }
    };

    useEffect(() => {
        generateIdea();
    }, []); // Empty dependency array - run once on mount

    return (
        <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
            <div className="container mx-auto px-4 py-12">
                {/* Header */}
                <header className="text-center mb-12">
                    <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
                        Business Idea Generator
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400 text-lg">
                        AI-powered innovation at your fingertips
                    </p>
                </header>

                {/* Content Card */}
                <div className="max-w-3xl mx-auto">
                    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 backdrop-blur-lg bg-opacity-95">
                        {idea === '…loading' ? (
                            <div className="flex items-center justify-center py-12">
                                <div className="animate-pulse text-gray-400">
                                    Generating your business idea...
                                </div>
                            </div>
                        ) : (
                            <div className="markdown-content text-gray-700 dark:text-gray-300">
                                <ReactMarkdown
                                    remarkPlugins={[remarkGfm, remarkBreaks]}
                                >
                                    {idea}
                                </ReactMarkdown>
                                {error && (
                                    <button
                                        type="button"
                                        onClick={generateIdea}
                                        className="mt-6 rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white shadow hover:bg-blue-700"
                                    >
                                        Reintentar
                                    </button>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </main>
    );
}
