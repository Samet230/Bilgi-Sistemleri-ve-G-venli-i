"use client"

import React, { useState, useEffect } from 'react'
import { FileText, Search, Calendar, Filter, X, ShieldAlert, CheckCircle2, Cpu, RefreshCw } from 'lucide-react'
import { cn, formatDate } from '@/lib/utils'
import axios from 'axios'

const API_BASE = "http://localhost:5050"

interface Job {
    job_id: string
    filename: string
    total_records: number
    attacks_detected: number
    normal_traffic: number
    attack_percentage: number
    created_at: string
}

interface Attack {
    id: number
    record_index: number
    probability: number
    attack_type: string
    dataset_source: string
    council_votes: string
    winning_model: string
    raw_log_data: string
    detected_at: string
}

export default function ReportsPage() {
    const [jobs, setJobs] = useState<Job[]>([])
    const [loading, setLoading] = useState(true)
    const [searchTerm, setSearchTerm] = useState('')

    // Detail Modal State
    const [selectedJob, setSelectedJob] = useState<Job | null>(null)
    const [attacks, setAttacks] = useState<Attack[]>([])
    const [detailLoading, setDetailLoading] = useState(false)

    const fetchJobs = async () => {
        setLoading(true)
        try {
            const response = await axios.get(`${API_BASE}/api/jobs`)
            if (response.data.jobs) {
                setJobs(response.data.jobs)
            }
        } catch (error) {
            console.error("Failed to fetch jobs:", error)
            // Fallback to empty array
            setJobs([])
        }
        setLoading(false)
    }

    useEffect(() => {
        fetchJobs()
    }, [])

    const openDetail = async (job: Job) => {
        setSelectedJob(job)
        setDetailLoading(true)
        setAttacks([])

        try {
            const response = await axios.get(`${API_BASE}/api/analyze/results/${job.job_id}`)
            if (response.data.attacks) {
                setAttacks(response.data.attacks)
            }
        } catch (error) {
            console.error("Failed to fetch details:", error)
            setAttacks([])
        }

        setDetailLoading(false)
    }

    const closeDetail = () => {
        setSelectedJob(null)
        setAttacks([])
    }

    const filteredJobs = jobs.filter(j =>
        j.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
        j.job_id.toLowerCase().includes(searchTerm.toLowerCase())
    )

    // Parse raw log data for display
    const parseRawLog = (rawLogData: string): Record<string, any> => {
        try {
            return JSON.parse(rawLogData)
        } catch {
            return { raw: rawLogData }
        }
    }

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Saldırı Raporları</h1>
                    <p className="text-muted-foreground mt-2">Tüm analiz geçmişi ve tespit detayları.</p>
                </div>
                <button
                    onClick={fetchJobs}
                    className="p-2 rounded-xl bg-muted hover:bg-primary/10 text-muted-foreground hover:text-primary transition-colors"
                    title="Yenile"
                >
                    <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
                </button>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-4">
                <div className="flex-1 relative">
                    <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
                    <input
                        type="text"
                        placeholder="Dosya veya iş ID'si ara..."
                        className="w-full bg-muted rounded-xl pl-12 pr-4 py-3 text-sm border border-border focus:border-primary outline-none"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
                <button className="flex items-center gap-2 bg-muted rounded-xl px-4 py-3 text-sm border border-border hover:border-primary transition-colors">
                    <Calendar size={16} />
                    Tarih
                </button>
                <button className="flex items-center gap-2 bg-muted rounded-xl px-4 py-3 text-sm border border-border hover:border-primary transition-colors">
                    <Filter size={16} />
                    Filtrele
                </button>
            </div>

            {/* Reports Table */}
            <div className="glass-card rounded-3xl overflow-hidden">
                <table className="w-full">
                    <thead className="bg-muted/50 border-b border-border">
                        <tr>
                            <th className="text-left px-6 py-4 text-sm font-bold">Dosya</th>
                            <th className="text-left px-6 py-4 text-sm font-bold">Kayıt</th>
                            <th className="text-left px-6 py-4 text-sm font-bold">Saldırı</th>
                            <th className="text-left px-6 py-4 text-sm font-bold">Oran</th>
                            <th className="text-left px-6 py-4 text-sm font-bold">Tarih</th>
                            <th className="text-left px-6 py-4 text-sm font-bold">Aksiyon</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td colSpan={6} className="text-center py-12 text-muted-foreground">Yükleniyor...</td>
                            </tr>
                        ) : filteredJobs.length === 0 ? (
                            <tr>
                                <td colSpan={6} className="text-center py-12 text-muted-foreground">
                                    Henüz analiz yapılmamış. Upload sayfasından CSV yükleyin.
                                </td>
                            </tr>
                        ) : (
                            filteredJobs.map((job) => (
                                <tr key={job.job_id} className="border-b border-border hover:bg-muted/20 transition-colors">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <FileText size={18} className="text-primary" />
                                            <span className="font-medium">{job.filename}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-muted-foreground">{job.total_records}</td>
                                    <td className="px-6 py-4">
                                        <span className="text-red-500 font-bold">{job.attacks_detected}</span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={cn(
                                            "px-2 py-1 rounded-full text-xs font-bold",
                                            job.attack_percentage > 50 ? "bg-red-500/10 text-red-500" : "bg-green-500/10 text-green-500"
                                        )}>
                                            %{job.attack_percentage.toFixed(1)}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-muted-foreground text-sm">
                                        {formatDate(job.created_at)}
                                    </td>
                                    <td className="px-6 py-4">
                                        <button
                                            onClick={() => openDetail(job)}
                                            className="text-primary hover:underline text-sm font-bold"
                                        >
                                            Detay
                                        </button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Detail Modal */}
            {selectedJob && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-8">
                    <div className="bg-card border border-border rounded-3xl w-full max-w-5xl max-h-[85vh] overflow-hidden shadow-2xl animate-in fade-in zoom-in-95 duration-300">
                        {/* Modal Header */}
                        <div className="flex items-center justify-between p-6 border-b border-border">
                            <div>
                                <h2 className="text-xl font-bold flex items-center gap-2">
                                    <ShieldAlert className="text-red-500" size={24} />
                                    Saldırı Detayları
                                </h2>
                                <p className="text-sm text-muted-foreground mt-1">{selectedJob.filename} - {selectedJob.job_id}</p>
                            </div>
                            <button
                                onClick={closeDetail}
                                className="p-2 rounded-xl hover:bg-muted transition-colors"
                            >
                                <X size={20} />
                            </button>
                        </div>

                        {/* Summary */}
                        <div className="p-6 border-b border-border bg-muted/30">
                            <div className="grid grid-cols-3 gap-6 text-center">
                                <div>
                                    <p className="text-3xl font-bold text-primary">{selectedJob.total_records}</p>
                                    <p className="text-sm text-muted-foreground">Toplam Kayıt</p>
                                </div>
                                <div>
                                    <p className="text-3xl font-bold text-red-500">{selectedJob.attacks_detected}</p>
                                    <p className="text-sm text-muted-foreground">Saldırı</p>
                                </div>
                                <div>
                                    <p className="text-3xl font-bold text-green-500">{selectedJob.normal_traffic}</p>
                                    <p className="text-sm text-muted-foreground">Normal</p>
                                </div>
                            </div>
                        </div>

                        {/* Attacks List */}
                        <div className="p-6 overflow-auto max-h-[450px]">
                            <h3 className="font-bold mb-4">Tespit Edilen Tehditler ({attacks.length})</h3>

                            {detailLoading ? (
                                <div className="text-center py-8 text-muted-foreground">Yükleniyor...</div>
                            ) : attacks.length === 0 ? (
                                <div className="text-center py-8">
                                    <CheckCircle2 size={48} className="text-green-500 mx-auto mb-4" />
                                    <p className="text-muted-foreground">Bu analizde tespit edilen saldırı yok.</p>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {attacks.map((attack) => {
                                        const logData = parseRawLog(attack.raw_log_data || '{}')
                                        return (
                                            <div
                                                key={attack.id}
                                                className={cn(
                                                    "p-5 rounded-2xl border-l-4 transition-colors",
                                                    attack.attack_type === "SALDIRI"
                                                        ? "bg-red-500/5 border-red-500"
                                                        : "bg-yellow-500/5 border-yellow-500"
                                                )}
                                            >
                                                {/* Background Decoration */}
                                                <div className="absolute top-0 right-0 p-4 opacity-5">
                                                    <ShieldAlert size={120} />
                                                </div>

                                                {/* Top Row: Verdict & Confidence */}
                                                <div className="flex items-start justify-between mb-6 relative z-10">
                                                    <div className="space-y-1">
                                                        <div className="flex items-center gap-2">
                                                            {attack.attack_type === "SALDIRI" ? (
                                                                <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-500 text-white text-sm font-bold shadow-lg shadow-red-500/20">
                                                                    <ShieldAlert size={14} />
                                                                    SALDIRI TESPİT EDİLDİ
                                                                </span>
                                                            ) : (
                                                                <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-yellow-500 text-white text-sm font-bold shadow-lg shadow-yellow-500/20">
                                                                    <ShieldAlert size={14} />
                                                                    ŞÜPHELİ AKTİVİTE
                                                                </span>
                                                            )}
                                                            <span className="text-xs text-muted-foreground font-mono">#{attack.record_index}</span>
                                                        </div>
                                                        <p className="text-2xl font-bold mt-2">
                                                            {logData.attack_type || logData.event_type || 'Bilinmeyen Tehdit'}
                                                        </p>
                                                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                                            <span>Tespit Eden Model:</span>
                                                            <span className="flex items-center gap-1 font-bold text-primary bg-primary/10 px-2 py-0.5 rounded">
                                                                <Cpu size={14} />
                                                                {attack.winning_model || 'ENSEMBLE'}
                                                            </span>
                                                        </div>
                                                    </div>

                                                    <div className="text-right">
                                                        <div className="flex flex-col items-end">
                                                            <span className="text-4xl font-black text-foreground">
                                                                %{(attack.probability * 100).toFixed(1)}
                                                            </span>
                                                            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Güven Skoru</span>
                                                        </div>
                                                    </div>
                                                </div>

                                                {/* Middle Row: Attack Context (Parsed Log) */}
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 relative z-10">
                                                    <div className="bg-card/50 rounded-xl p-4 border border-border/50">
                                                        <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3">Saldırı Bağlamı</h4>
                                                        <div className="space-y-2 text-sm">
                                                            {logData.timestamp && (
                                                                <div className="flex justify-between border-b border-border/50 pb-1">
                                                                    <span className="text-muted-foreground">Zaman:</span>
                                                                    <span className="font-mono">{logData.timestamp}</span>
                                                                </div>
                                                            )}
                                                            {logData.source && (
                                                                <div className="flex justify-between border-b border-border/50 pb-1">
                                                                    <span className="text-muted-foreground">Kaynak:</span>
                                                                    <span className="font-mono font-bold text-red-500">{logData.source}</span>
                                                                </div>
                                                            )}
                                                            {logData.ip && (
                                                                <div className="flex justify-between border-b border-border/50 pb-1">
                                                                    <span className="text-muted-foreground">IP Adresi:</span>
                                                                    <span className="font-mono">{logData.ip}</span>
                                                                </div>
                                                            )}
                                                            {logData.user && (
                                                                <div className="flex justify-between border-b border-border/50 pb-1">
                                                                    <span className="text-muted-foreground">Kullanıcı:</span>
                                                                    <span className="font-mono text-yellow-500">{logData.user}</span>
                                                                </div>
                                                            )}
                                                            {(logData.url || logData.path) && (
                                                                <div className="flex justify-between border-b border-border/50 pb-1">
                                                                    <span className="text-muted-foreground">Hedef:</span>
                                                                    <span className="font-mono max-w-[200px] truncate" title={logData.url || logData.path}>
                                                                        {logData.url || logData.path}
                                                                    </span>
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>

                                                    {/* Technical Evidence */}
                                                    <div className="bg-card/50 rounded-xl p-4 border border-border/50">
                                                        <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-3">Teknik Kanıtlar</h4>
                                                        <div className="space-y-2 text-sm">
                                                            {Object.entries(logData)
                                                                .filter(([k]) => !['timestamp', 'source', 'ip', 'user', 'url', 'path', 'label', 'attack_type', 'event_type'].includes(k))
                                                                .slice(0, 5)
                                                                .map(([key, value]) => (
                                                                    <div key={key} className="flex justify-between border-b border-border/50 pb-1 last:border-0 last:pb-0">
                                                                        <span className="text-muted-foreground capitalize">{key.replace(/_/g, ' ')}:</span>
                                                                        <span className="font-mono text-right truncate max-w-[180px]" title={String(value)}>{String(value)}</span>
                                                                    </div>
                                                                ))}
                                                        </div>
                                                    </div>
                                                </div>

                                            </div>
                                        )
                                    })}
                                </div>
                            )}
                        </div>

                        {/* Modal Footer */}
                        <div className="p-6 border-t border-border flex justify-end gap-4">
                            <button
                                onClick={closeDetail}
                                className="px-6 py-2.5 rounded-xl bg-muted hover:bg-muted/80 font-medium transition-colors"
                            >
                                Kapat
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
