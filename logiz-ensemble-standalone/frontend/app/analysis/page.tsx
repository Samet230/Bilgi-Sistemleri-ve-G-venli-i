"use client"

import React, { useState } from 'react'
import { Search, Zap, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import axios from 'axios'

const API_BASE = "http://localhost:5050"

export default function AnalysisPage() {
    const [query, setQuery] = useState('')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<any>(null)
    const [error, setError] = useState<string | null>(null)

    const runAnalysis = async () => {
        if (!query.trim()) return

        setLoading(true)
        setError(null)
        setResult(null)

        try {
            // Analyze a single log entry
            // In a full implementation, this would call a specific endpoint
            // For now, we simulate by using a temporary file upload

            const blob = new Blob([`message\n${query}`], { type: 'text/csv' })
            const formData = new FormData()
            formData.append('file', blob, 'single_query.csv')

            const response = await axios.post(`${API_BASE}/api/analyze/upload`, formData)

            if (response.data.success) {
                setResult({
                    decision: response.data.results.attacks_detected > 0 ? 'SALDIRI' : 'NORMAL',
                    model: response.data.results.model_used,
                    attacks: response.data.results.attacks_detected,
                    normal: response.data.results.normal_traffic
                })
            } else {
                setError(response.data.error || 'Analiz hatası')
            }
        } catch (e: any) {
            setError(e.message || 'Sunucu bağlantı hatası')
        }

        setLoading(false)
    }

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Hızlı Analiz</h1>
                <p className="text-muted-foreground mt-2">Tek bir log satırını veya mesajı anında analiz edin.</p>
            </div>

            {/* Search/Input */}
            <div className="glass-card rounded-3xl p-6 space-y-6">
                <div className="flex items-center gap-4">
                    <div className="flex-1 relative">
                        <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
                        <input
                            type="text"
                            placeholder="Analiz etmek istediğiniz log satırını girin... (örn: SQL Injection attempt from 192.168.1.1)"
                            className="w-full bg-muted rounded-xl pl-12 pr-4 py-4 text-sm border border-border focus:border-primary outline-none"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && runAnalysis()}
                        />
                    </div>
                    <button
                        onClick={runAnalysis}
                        disabled={loading || !query.trim()}
                        className={cn(
                            "flex items-center gap-2 bg-primary text-white rounded-xl px-8 py-4 font-bold shadow-lg shadow-primary/20 transition-all",
                            (loading || !query.trim()) && "opacity-50 cursor-not-allowed"
                        )}
                    >
                        {loading ? (
                            <>
                                <Loader2 size={18} className="animate-spin" />
                                Analiz...
                            </>
                        ) : (
                            <>
                                <Zap size={18} className="fill-white" />
                                Analiz Et
                            </>
                        )}
                    </button>
                </div>

                {/* Result */}
                {result && (
                    <div className={cn(
                        "p-6 rounded-2xl border-2 flex items-center gap-4",
                        result.decision === 'SALDIRI' ? "bg-red-500/10 border-red-500/30" : "bg-green-500/10 border-green-500/30"
                    )}>
                        {result.decision === 'SALDIRI' ? (
                            <AlertCircle className="text-red-500" size={32} />
                        ) : (
                            <CheckCircle2 className="text-green-500" size={32} />
                        )}
                        <div>
                            <h3 className={cn(
                                "text-xl font-bold",
                                result.decision === 'SALDIRI' ? "text-red-500" : "text-green-500"
                            )}>
                                {result.decision === 'SALDIRI' ? '🚨 Tehdit Tespit Edildi!' : '✅ Güvenli'}
                            </h3>
                            <p className="text-sm text-muted-foreground mt-1">
                                Model: {result.model} | Saldırı: {result.attacks} | Normal: {result.normal}
                            </p>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="p-4 rounded-2xl bg-destructive/10 border border-destructive/20 text-destructive text-sm">
                        {error}
                    </div>
                )}
            </div>

            {/* Quick Examples */}
            <div className="glass-card rounded-3xl p-6">
                <h3 className="font-bold mb-4">Örnek Sorgular</h3>
                <div className="flex flex-wrap gap-2">
                    {[
                        "SQL Injection attempt from 192.168.1.1",
                        "Normal user login successful",
                        "Brute force SSH attack detected",
                        "GET /api/health 200 OK"
                    ].map((example) => (
                        <button
                            key={example}
                            onClick={() => setQuery(example)}
                            className="px-4 py-2 rounded-xl bg-muted/50 hover:bg-muted text-sm transition-colors"
                        >
                            {example}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    )
}
