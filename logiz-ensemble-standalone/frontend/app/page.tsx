"use client"

import React from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { ShieldCheck, Activity, BrainCircuit, ChevronRight, BarChart3, Lock } from 'lucide-react'

export default function LandingPage() {
    return (
        <div className="min-h-screen bg-black text-white relative overflow-hidden">

            {/* Background Gradients */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-sky-500/20 rounded-full blur-[120px]" />
                <div className="absolute bottom-[0%] right-[-10%] w-[600px] h-[600px] bg-primary/20 rounded-full blur-[150px]" />
            </div>

            {/* Navbar */}
            <nav className="relative z-10 px-8 py-6 flex items-center justify-between max-w-7xl mx-auto">
                <div className="flex items-center gap-2">
                    <div className="relative">
                        <ShieldCheck className="w-8 h-8 text-primary relative z-10" />
                        <div className="absolute inset-0 bg-primary/50 blur-lg animate-pulse" />
                    </div>
                    <span className="text-2xl font-bold tracking-tight">Anomi AI</span>
                </div>
                <div className="flex gap-6 text-sm font-medium text-muted-foreground">
                    <Link href="/monitor" className="hover:text-primary transition-colors">Canlı İzleme</Link>
                    <Link href="/analysis" className="hover:text-primary transition-colors">Analiz</Link>
                    <Link href="/reports" className="hover:text-primary transition-colors">Raporlar</Link>
                    <Link href="/upload" className="hover:text-primary transition-colors">Yükle</Link>
                </div>
            </nav>

            {/* Hero Section */}
            <main className="relative z-10 max-w-7xl mx-auto px-8 pt-20 pb-16 lg:pt-32">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="max-w-3xl"
                >
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-primary mb-8">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
                        </span>
                        Sistem Aktif ve Koruma Altında
                    </div>

                    <h1 className="text-5xl lg:text-7xl font-extrabold tracking-tight leading-[1.1] mb-6">
                        Yeni Nesil <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-sky-400 to-indigo-500 animate-gradient-x">
                            Yapay Zeka Destekli
                        </span> <br />
                        Siber Güvenlik
                    </h1>

                    <p className="text-lg text-muted-foreground leading-relaxed max-w-xl mb-10">
                        Elektrikli şarj istasyonları (EV) ve kritik altyapılar için Ensemble Learning teknolojisi ile geliştirilmiş,
                        gerçek zamanlı anomali tespiti ve saldırı önleme platformu.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4">
                        <Link href="/dashboard">
                            <button className="group relative px-8 py-4 bg-primary text-primary-foreground font-bold rounded-full text-lg shadow-[0_0_40px_-10px_rgba(34,197,94,0.6)] hover:shadow-[0_0_60px_-10px_rgba(34,197,94,0.8)] transition-all flex items-center gap-3">
                                Güvenlik Paneli
                                <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            </button>
                        </Link>
                        <Link href="/monitor">
                            <button className="px-8 py-4 bg-white/5 text-white border border-white/10 font-bold rounded-full text-lg hover:bg-white/10 transition-all flex items-center gap-3">
                                <Activity className="w-5 h-5 text-sky-400" />
                                Canlı İzleme
                            </button>
                        </Link>
                    </div>
                </motion.div>

                {/* Feature Cards Carousel */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-24"
                >
                    <FeatureCard
                        icon={<BrainCircuit className="w-8 h-8 text-indigo-400" />}
                        title="Ensemble AI Modeli"
                        description="Random Forest, XGBoost ve Isolation Forest algoritmalarının ortak aklı ile %99.8 doğruluk."
                    />
                    <FeatureCard
                        icon={<Activity className="w-8 h-8 text-sky-400" />}
                        title="Gerçek Zamanlı Monitör"
                        description="SSE teknolojisi ile milisaniyelik gecikmeyle tüm istasyon loglarını anlık izleyin."
                    />
                    <FeatureCard
                        icon={<Lock className="w-8 h-8 text-emerald-400" />}
                        title="Saldırı Önleme"
                        description="SQL Injection, DDoS ve Firmware manipülasyonlarını oluştuğu anda tespit eder."
                    />
                </motion.div>
            </main>

            {/* Footer Stats - Decoration */}
            <div className="absolute bottom-0 w-full border-t border-white/10 bg-black/50 backdrop-blur-sm py-6">
                <div className="max-w-7xl mx-auto px-8 flex justify-between text-xs text-muted-foreground uppercase tracking-widest">
                    <div>System Status: Online</div>
                    <div>Latency: 12ms</div>
                    <div>Active Agents: 1</div>
                    <div className="flex gap-2 items-center"><div className="w-2 h-2 bg-green-500 rounded-full"></div>Live</div>
                </div>
            </div>

        </div>
    )
}

function FeatureCard({ icon, title, description }: any) {
    return (
        <div className="group p-6 rounded-3xl bg-white/5 border border-white/10 hover:border-primary/50 hover:bg-white/[0.07] transition-all cursor-default">
            <div className="mb-4 p-3 bg-black/20 rounded-2xl w-fit group-hover:scale-110 transition-transform duration-300">
                {icon}
            </div>
            <h3 className="text-xl font-bold mb-2 text-white/90">{title}</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
        </div>
    )
}
