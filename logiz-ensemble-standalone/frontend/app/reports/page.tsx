"use client"

import React, { useState, useEffect } from 'react'
import { FileText, Search, Calendar, Filter, X, ShieldAlert, CheckCircle2, Cpu, RefreshCw, Download, FileDown } from 'lucide-react'
import { cn, formatDate } from '@/lib/utils'
import axios from 'axios'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

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

    // Helper to load font from URL
    const loadFont = async (url: string): Promise<string> => {
        const response = await fetch(url)
        const buffer = await response.arrayBuffer()
        return arrayBufferToBase64(buffer)
    }

    const arrayBufferToBase64 = (buffer: ArrayBuffer): string => {
        let binary = ''
        const bytes = new Uint8Array(buffer)
        const len = bytes.byteLength
        for (let i = 0; i < len; i++) {
            binary += String.fromCharCode(bytes[i])
        }
        return window.btoa(binary)
    }

    // Generate Professional PDF Report with Turkish Support
    const generatePDF = async (job: Job) => {
        try {
            // Fetch attack details
            const response = await axios.get(`${API_BASE}/api/analyze/results/${job.job_id}`)
            const jobAttacks: Attack[] = response.data.attacks || []

            // Initialize PDF
            const doc = new jsPDF()

            // Load local Roboto font (supports Turkish characters)
            try {
                const fontResponse = await fetch('/roboto.ttf')
                const fontBuffer = await fontResponse.arrayBuffer()
                const fontBase64 = btoa(
                    new Uint8Array(fontBuffer).reduce((data, byte) => data + String.fromCharCode(byte), '')
                )
                doc.addFileToVFS('Roboto-Regular.ttf', fontBase64)
                doc.addFont('Roboto-Regular.ttf', 'Roboto', 'normal')
                doc.setFont('Roboto')
            } catch (fontError) {
                console.warn('Could not load Roboto font, using Helvetica as fallback:', fontError)
                doc.setFont('helvetica')
            }

            // --- DESIGN & LAYOUT ---

            // 1. Branding Header
            doc.setFillColor(30, 41, 59) // Dark Slate
            doc.rect(0, 0, 210, 40, 'F')

            doc.setFontSize(24)
            doc.setTextColor(255, 255, 255)
            doc.text('Anomi AI', 14, 20)

            doc.setFontSize(10)
            doc.setTextColor(148, 163, 184)
            doc.text('Gelişmiş Anomali Tespit Raporu', 14, 28)

            doc.text(new Date().toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' }), 195, 20, { align: 'right' })

            // 2. Job Summary Card
            const startY = 55

            // Left Column (File Info)
            doc.setFontSize(12)
            doc.setTextColor(30, 41, 59)
            doc.setFont('Roboto', 'normal')
            doc.text('Analiz Özeti', 14, startY)

            doc.setFontSize(10)
            doc.setTextColor(71, 85, 105)
            doc.setFontSize(10)
            doc.setTextColor(71, 85, 105)

            doc.text('Dosya Adı:', 14, startY + 8)
            doc.setTextColor(0)
            doc.text(job.filename, 40, startY + 8)

            doc.setTextColor(71, 85, 105)
            doc.text('İşlem ID:', 14, startY + 14)
            doc.setTextColor(0)
            doc.text(job.job_id, 40, startY + 14)

            // Right Column (Stats)
            const rightColX = 120
            doc.setFillColor(241, 245, 249) // Light Gray Bg
            doc.roundedRect(rightColX - 5, startY - 5, 80, 25, 3, 3, 'F')

            doc.setFontSize(9)
            doc.setTextColor(100)
            doc.text('TOPLAM KAYIT', rightColX, startY)
            doc.setFontSize(14)
            doc.setTextColor(30, 41, 59)
            doc.text(job.total_records.toString(), rightColX, startY + 7)

            doc.setFontSize(9)
            doc.setTextColor(100)
            doc.text('TESPİT EDİLEN TEHDİT', rightColX + 40, startY)
            doc.setFontSize(14)
            doc.setTextColor(220, 38, 38) // Red for attacks
            doc.text(job.attacks_detected.toString(), rightColX + 40, startY + 7)

            // 3. Detailed Findings Table
            doc.setFontSize(12)
            doc.setTextColor(30, 41, 59)
            doc.text('Tespit Edilen Tehditler ve Anormallikler', 14, startY + 40)

            if (jobAttacks.length > 0) {
                const tableBody = jobAttacks.map((attack, idx) => [
                    (idx + 1).toString(),
                    attack.attack_type || 'Şarj İstasyonu Anomalisi',
                    `%${(attack.probability * 100).toFixed(1)}`,
                    attack.winning_model || 'ENSEMBLE',
                    attack.dataset_source || '-',
                    (attack.detected_at || '').split('T')[1]?.split('.')[0] || '-'
                ])

                autoTable(doc, {
                    startY: startY + 45,
                    head: [['#', 'Tehdit Tipi', 'Güven Skoru', 'Tespit Modeli', 'Kaynak', 'Saat']],
                    body: tableBody,
                    styles: {
                        font: 'Roboto',
                        fontSize: 9,
                        cellPadding: 4,
                        textColor: [51, 65, 85]
                    },
                    headStyles: {
                        fillColor: [30, 41, 59],
                        textColor: 255,
                        fontStyle: 'bold'
                    },
                    alternateRowStyles: {
                        fillColor: [248, 250, 252]
                    },
                    columnStyles: {
                        0: { cellWidth: 10 },
                        2: { fontStyle: 'bold', textColor: [220, 38, 38] } // Confidence red
                    },
                    margin: { left: 14, right: 14 }
                })
            } else {
                doc.setDrawColor(34, 197, 94) // Green border
                doc.setFillColor(240, 253, 244) // Light green bg
                doc.roundedRect(14, startY + 45, 182, 15, 2, 2, 'FD')
                doc.setFontSize(10)
                doc.setTextColor(21, 128, 61)
                doc.text('Bu analizde herhangi bir tehdit veya anomali tespit edilmemiştir.', 20, startY + 54)
            }

            // 4. Footer
            const totalPages = doc.getNumberOfPages()
            for (let i = 1; i <= totalPages; i++) {
                doc.setPage(i)
                doc.setFontSize(8)
                doc.setTextColor(148, 163, 184)
                doc.text(
                    `Anomi Ensemble AI - Güvenlik Raporu - Sayfa ${i} / ${totalPages}`,
                    105,
                    doc.internal.pageSize.height - 10,
                    { align: 'center' }
                )
            }

            // Save
            doc.save(`Anomi_Guvenlik_Raporu_${job.job_id}.pdf`)

        } catch (error) {
            console.error('PDF generation error:', error)
            alert('PDF oluşturulamadı. Konsolu kontrol edin.')
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
                <a
                    href={`${API_BASE}/api/export/attacks`}
                    className="flex items-center gap-2 px-3 py-2 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-500 text-sm font-medium transition-colors"
                    title="Saldırıları CSV olarak indir"
                >
                    <Download size={16} />
                    Saldırı Raporu
                </a>
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
                                        <div className="flex items-center gap-2">
                                            <button
                                                onClick={() => openDetail(job)}
                                                className="text-primary hover:underline text-sm font-bold"
                                            >
                                                Detay
                                            </button>
                                            <button
                                                onClick={() => generatePDF(job)}
                                                className="flex items-center gap-1 text-red-500 hover:text-red-400 text-sm font-bold transition-colors"
                                                title="PDF İndir"
                                            >
                                                <FileDown size={14} />
                                                PDF
                                            </button>
                                        </div>
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
                            <h3 className="font-bold mb-4">
                                Tespit Edilen Tehditler
                                <span className="text-muted-foreground ml-2 text-sm font-normal">
                                    (Toplam: {selectedJob.attacks_detected} - Gösterilen: İlk {attacks.length})
                                </span>
                            </h3>

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
                                                            {attack.attack_type || 'Şarj İstasyonu Anomalisi'}
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
