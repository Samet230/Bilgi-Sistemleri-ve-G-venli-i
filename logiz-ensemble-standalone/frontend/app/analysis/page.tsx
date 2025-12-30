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

            // Send as TXT to handle commas correctly in raw log
            const blob = new Blob([query], { type: 'text/plain' })
            const formData = new FormData()
            formData.append('file', blob, 'single_query.txt')

            const response = await axios.post(`${API_BASE}/api/analyze/upload`, formData)

            if (response.data.success) {
                setResult({
                    decision: response.data.results.attacks_detected > 0 ? 'SALDIRI' : 'NORMAL',
                    model: response.data.results.model_used,
                    attacks: response.data.results.attacks_detected,
                    normal: response.data.results.normal_traffic,
                    detailed_logs: response.data.results.detailed_logs
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

                {/* Hızlı Analiz için Özet Kısım Kaldırıldı (Kullanıcı İsteği) */}

                {/* Detailed Logs View - Now Primary */}
                {result && result.detailed_logs && result.detailed_logs.length > 0 && (
                    <div className="space-y-4 animate-in slide-in-from-bottom-2 duration-500">
                        {/* <h3 className="text-lg font-bold px-1">Detaylı Analiz Raporu</h3> - Başlık da kaldırılabilir, direkt kart gösterilsin */}
                        {result.detailed_logs.map((log: any, idx: number) => (
                            <div key={idx} className={cn(
                                "rounded-3xl p-8 border-2 shadow-2xl transition-all",
                                log.attack_detected
                                    ? "bg-red-500/10 border-red-500/50 shadow-red-900/20"
                                    : "bg-green-500/10 border-green-500/50 shadow-green-900/20"
                            )}>
                                {/* Header */}
                                <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-6 mb-8 border-b border-white/10 pb-6">
                                    <div className="flex items-center gap-4">
                                        {log.attack_detected ? (
                                            <div className="p-4 rounded-full bg-red-500/20 text-red-500 animate-pulse">
                                                <AlertCircle size={40} />
                                            </div>
                                        ) : (
                                            <div className="p-4 rounded-full bg-green-500/20 text-green-500">
                                                <CheckCircle2 size={40} />
                                            </div>
                                        )}

                                        <div>
                                            <h2 className={cn(
                                                "text-3xl font-black uppercase tracking-tight",
                                                log.attack_detected ? "text-red-500" : "text-green-500"
                                            )}>
                                                {log.attack_detected ? "TEHDİT TESPİT EDİLDİ!" : "GÜVENLİ İŞLEM"}
                                            </h2>
                                            <div className="flex items-center gap-3 mt-2">
                                                <span className="text-lg text-foreground font-semibold">
                                                    Karar: {log.decision}
                                                </span>
                                                <span className="text-white/20">|</span>
                                                <span className="text-lg text-foreground font-semibold">
                                                    Güven Skoru:
                                                    <span className={cn(
                                                        "ml-2 px-3 py-1 rounded-lg text-white",
                                                        log.confidence > 0.8 ? "bg-green-600" : "bg-yellow-600"
                                                    )}>
                                                        %{(log.confidence * 100).toFixed(1)}
                                                    </span>
                                                </span>
                                                <span className="text-white/20">|</span>
                                                <span className="text-sm text-muted-foreground font-mono">
                                                    Model: {log.winning_model}
                                                </span>
                                            </div>

                                            {/* Reason / Explanation */}
                                            <div className="mt-4 p-4 rounded-xl bg-white/5 border border-white/10 max-w-2xl">
                                                <div className="flex items-center gap-2 mb-1">
                                                    <Zap size={14} className={log.attack_detected ? "text-red-400" : "text-green-400"} />
                                                    <h5 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Analiz Nedeni</h5>
                                                </div>
                                                <p className="text-base font-medium text-foreground">
                                                    {log.reason || "Yapay zeka modelleri tarafından değerlendirildi."}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Raw Data Table */}
                                <div className="bg-black/40 rounded-2xl p-6 border border-white/5">
                                    <h4 className="flex items-center gap-2 text-sm font-bold text-muted-foreground uppercase tracking-widest mb-6">
                                        <Search size={16} />
                                        Log İçeriği ve Öznitelikler
                                    </h4>
                                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-x-12 gap-y-4">
                                        {Object.entries(log.raw_data).map(([key, value]) => (
                                            <div key={key} className="group flex flex-col border-b border-white/5 pb-2 hover:bg-white/5 transition-colors px-3 rounded-lg">
                                                <span className="text-xs text-muted-foreground font-bold mb-1 opacity-70 group-hover:opacity-100 transition-opacity">{key}</span>
                                                <span className="font-mono text-base text-foreground break-all">{String(value)}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ))}
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
