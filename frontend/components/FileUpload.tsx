'use client';

import React, { useState } from 'react';
import { transactionAPI } from '@/lib/api';

interface FileUploadProps {
    onUploadSuccess?: () => void;
}

export default function FileUpload({ onUploadSuccess }: FileUploadProps) {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
    const [dragActive, setDragActive] = useState(false);

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleFile = (file: File) => {
        const validTypes = ['text/csv', 'application/pdf', 'application/vnd.ms-excel'];
        const fileExt = file.name.split('.').pop()?.toLowerCase();

        if (!validTypes.includes(file.type) && !['csv', 'pdf'].includes(fileExt || '')) {
            setMessage({ type: 'error', text: 'Invalid file type. Please upload a CSV or PDF file.' });
            return;
        }

        setFile(file);
        setMessage(null);
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setMessage(null);

        try {
            const response = await transactionAPI.upload(file);
            setMessage({
                type: 'success',
                text: response.data.message,
            });
            setFile(null);
            if (onUploadSuccess) {
                onUploadSuccess();
            }
        } catch (error: any) {
            setMessage({
                type: 'error',
                text: error.response?.data?.detail || 'Failed to upload file. Please try again.',
            });
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="card">
            <h2 className="text-2xl font-bold mb-4 gradient-text">Upload Bank Statement</h2>

            <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-all ${dragActive
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                    }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    accept=".csv,.pdf"
                    onChange={handleChange}
                />

                <label htmlFor="file-upload" className="cursor-pointer">
                    <div className="mb-4">
                        <svg
                            className="mx-auto h-12 w-12 text-gray-400"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                            />
                        </svg>
                    </div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        {file ? file.name : 'Drop your bank statement here or click to browse'}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                        Supported formats: CSV, PDF
                    </p>
                </label>
            </div>

            {file && (
                <div className="mt-4">
                    <button
                        onClick={handleUpload}
                        disabled={uploading}
                        className="btn btn-primary w-full"
                    >
                        {uploading ? (
                            <span className="flex items-center justify-center">
                                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Uploading...
                            </span>
                        ) : (
                            'Upload & Process'
                        )}
                    </button>
                </div>
            )}

            {message && (
                <div
                    className={`mt-4 p-4 rounded-lg ${message.type === 'success'
                            ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200 border border-green-200 dark:border-green-800'
                            : 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200 border border-red-200 dark:border-red-800'
                        }`}
                >
                    {message.text}
                </div>
            )}
        </div>
    );
}
