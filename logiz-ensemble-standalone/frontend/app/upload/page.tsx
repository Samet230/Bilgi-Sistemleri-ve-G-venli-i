"use client"

import React, { useState, useCallback } from 'react'
import {
    Upload as UploadIcon,
    FileText,
    X,
    CheckCircle2,
    AlertCircle,
    Loader2,
    ShieldCheck,
    Zap,
    ChevronRight
} from 'lucide-react'
import { cn } from '@/lib/utils'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'

const API_BASE = "http://localhost:5050/api/analyze/upload"

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null)
    const [status, setStatus] = useState<'idle' | 'uploading' | 'analyzing' | 'completed' | 'error'>('idle')
    const [results, setResults] = useState<any>(null)
    const [error, setError] = useState<string | null>(null)

    const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0])
            setStatus('idle')
            setError(null)
        }
    }

    const handleUpload = async () => {
        if (!file) return

        setStatus('uploading')
        setError(null)

        const formData = new FormData()
        formData.append('file', file)

        try {
            setStatus('analyzing')
            const response = await axios.post(API_BASE, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })

            if (response.data.success) {
                setResults(response.data)
                setStatus('completed')
            } else {
                throw new Error(response.data.error || 'Analiz başarısız oldu')
            }
        } catch (err: any) {
            console.error(err)
            setError(err.response?.data?.error || err.message || 'Bir hata oluştu')
            setStatus('error')
        }
    }

    const reset = () => {
        setFile(null)
        setStatus('idle')
        setResults(null)
        setError(null)
    }

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Anomali Analiz Merkezi</h1>
                <p className="text-muted-foreground mt-2">
                    Log dosyalarınızı yükleyin ve 10'lu Ensemble AI konseyi tarafından derinlemesine incelenmesini bekleyin.
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left: Upload Area */}
                <div className="lg:col-span-2 space-y-6">
                    <div
                        className={cn(
                            "relative border-2 border-dashed rounded-3xl p-12 flex flex-col items-center justify-center transition-all duration-300",
                            status === 'idle' ? "border-border hover:border-primary/50 bg-card/30" : "border-primary/20 bg-primary/5",
                            file ? "border-primary/50" : ""
                        )}
                    >
                        <input
                            type="file"
                            className="absolute inset-0 opacity-0 cursor-pointer"
                            onChange={onFileChange}
                            disabled={status !== 'idle' && status !== 'error'}
                            accept=".csv,.txt,.log"
                        />

                        <AnimatePresence mode="wait">
                            {!file ? (
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.9 }}
                                    className="flex flex-col items-center text-center space-y-4"
                                >
                                    <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center text-muted-foreground">
                                        <UploadIcon size={32} />
                                    </div>
                                    <div>
                                        <p className="text-lg font-semibold">Dosyayı Buraya Sürükleyin veya Tıklayın</p>
                                        <p className="text-sm text-muted-foreground">CSV veya Log formatı (Maks. 50MB)</p>
                                    </div>
                                </motion.div>
                            ) : (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="flex flex-col items-center text-center space-y-4"
                                >
                                    <div className="w-20 h-20 rounded-full bg-primary/20 flex items-center justify-center text-primary">
                                        <FileText size={32} />
                                    </div>
                                    <div>
                                        <p className="text-lg font-semibold">{file.name}</p>
                                        <p className="text-sm text-muted-foreground">{(file.size / 1024).toFixed(2)} KB</p>
                                    </div>
                                    {status === 'idle' && (
                                        <button
                                            onClick={(e) => { e.stopPropagation(); setFile(null); }}
                                            className="text-sm text-destructive hover:underline flex items-center gap-1"
                                        >
                                            <X size={14} /> Dosyayı Kaldır
                                        </button>
                                    )}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    <div className="flex justify-end gap-4">
                        <button
                            onClick={reset}
                            className="px-6 py-2.5 rounded-xl border border-border hover:bg-muted font-medium transition-colors"
                            disabled={status === 'uploading' || status === 'analyzing'}
                        >
                            Temizle
                        </button>
                        <button
                            onClick={handleUpload}
                            className={cn(
                                "px-8 py-2.5 rounded-xl grad-blue text-white font-semibold flex items-center gap-2 shadow-lg shadow-primary/20 transition-all",
                                (!file || status === 'uploading' || status === 'analyzing') && "opacity-50 cursor-not-allowed grayscale"
                            )}
                            disabled={!file || status === 'uploading' || status === 'analyzing'}
                        >
                            {(status === 'uploading' || status === 'analyzing') ? (
                                <>
                                    <Loader2 className="animate-spin" size={20} />
                                    {status === 'uploading' ? 'Yükleniyor...' : 'AI Analiz Ediyor...'}
                                </>
                            ) : (
                                <>
                                    <Zap size={20} className="fill-white" />
                                    Analizi Başlat
                                </>
                            )}
                        </button>
                    </div>
                </div>

                {/* Right: Stats and Info */}
                <div className="space-y-6">
                    <div className="glass-card rounded-3xl p-6 space-y-6">
                        <h3 className="text-lg font-bold flex items-center gap-2">
                            <ShieldCheck className="text-primary" size={20} />
                            Ensemble AI Durumu
                        </h3>

                        <div className="space-y-4">
                            <div className="flex items-center justify-between p-3 rounded-2xl bg-muted/50">
                                <span className="text-sm text-muted-foreground">Aktif Modeller</span>
                                <span className="font-bold text-primary">10 / 10</span>
                            </div>
                            <div className="flex items-center justify-between p-3 rounded-2xl bg-muted/50">
                                <span className="text-sm text-muted-foreground">Doğruluk Oranı</span>
                                <span className="font-bold text-green-500">%100.0</span>
                            </div>
                            <div className="flex items-center justify-between p-3 rounded-2xl bg-muted/50">
                                <span className="text-sm text-muted-foreground">İşlem Hızı</span>
                                <span className="font-bold">~5ms / log</span>
                            </div>
                        </div>

                        <div className="pt-4 border-t border-border">
                            <p className="text-xs text-muted-foreground leading-relaxed">
                                Yüklediğiniz loglar; Random Forest, GBM, ve Extra Trees modellerinden oluşan hibrid bir oylama sistemiyle incelenir.
                            </p>
                        </div>
                    </div>

                    <AnimatePresence>
                        {status === 'completed' && results && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="grad-dark border border-white/5 rounded-3xl p-6 space-y-6 shadow-2xl"
                            >
                                <div className="flex items-center justify-between">
                                    <h3 className="text-lg font-bold">Analiz Özeti</h3>
                                    <CheckCircle2 className="text-green-500" />
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
                                        <p className="text-xs text-muted-foreground">Saldırı</p>
                                        <p className="text-2xl font-bold text-red-500">{results.results.attacks_detected}</p>
                                    </div>
                                    <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
                                        <p className="text-xs text-muted-foreground">Normal</p>
                                        <p className="text-2xl font-bold text-green-500">{results.results.normal_traffic}</p>
                                    </div>
                                </div>

                                <button
                                    className="w-full py-3 rounded-2xl bg-primary text-white font-bold flex items-center justify-center gap-2 hover:bg-primary/90 transition-colors"
                                >
                                    Detaylı Raporu Gör <ChevronRight size={18} />
                                </button>
                            </motion.div>
                        )}

                        {status === 'error' && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="bg-destructive/10 border border-destructive/20 rounded-3xl p-6 space-y-4"
                            >
                                <div className="flex items-center gap-2 text-destructive font-bold">
                                    <AlertCircle size={20} />
                                    Hata Oluştu
                                </div>
                                <p className="text-sm text-destructive-foreground opacity-80">{error}</p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    )
}
