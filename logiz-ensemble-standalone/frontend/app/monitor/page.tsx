"use client"

import React, { useState, useEffect, useRef } from 'react'
import { Activity, Server, Terminal, Shield, Download, Cpu, Copy, Check, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import axios from 'axios'

const API_BASE = "http://localhost:5050"

interface Log {
    id: string
    timestamp: string
    source: string
    content: string
    analysis: {
        decision: string
        confidence: number
        winning_model: string
        is_attack: boolean
    }
}

interface Agent {
    hostname: string
    ip: string
    last_seen: string
    status: string
}

export default function MonitorPage() {
    const [agents, setAgents] = useState<Agent[]>([])
    const [logs, setLogs] = useState<Log[]>([])
    const [isStreaming, setIsStreaming] = useState(false)
    const [copied, setCopied] = useState(false)
    const logsEndRef = useRef<HTMLDivElement>(null)

    const [error, setError] = useState<string | null>(null)

    // Fetch active agents periodically
    useEffect(() => {
        const fetchAgents = async () => {
            try {
                const res = await axios.get(`${API_BASE}/api/agents`)
                setAgents(res.data.agents)
                setError(null)
            } catch (e: any) {
                const msg = e.response ? `Status: ${e.response.status}` : e.message
                console.error("Agent fetch error", e)
                setError(`API Hatası: ${msg}`)
            }
        }

        fetchAgents()
        const interval = setInterval(fetchAgents, 5000)
        return () => clearInterval(interval)
    }, [])

    // Start SSE Stream
    useEffect(() => {
        const eventSource = new EventSource(`${API_BASE}/api/monitor/stream`)
        setIsStreaming(true)

        eventSource.onmessage = (event) => {
            const parsed = JSON.parse(event.data)
            if (parsed.type === 'logs') {
                const newLogs = parsed.data
                if (newLogs && newLogs.length > 0) {
                    setLogs(prev => {
                        // Keep specific number of logs to prevent memory issues
                        const combined = [...newLogs, ...prev] // Newest first
                        return combined.slice(0, 500)
                    })
                }
            }
        }

        eventSource.onerror = () => {
            setIsStreaming(false)
            eventSource.close()
        }

        return () => {
            eventSource.close()
        }
    }, [])

    const copyAgentScript = () => {
        const script = `
import requests, sys, time, platform
API_URL = "${API_BASE}/api/ingest"
logfile = "/var/log/auth.log" if platform.system() != "Windows" else "C:\\\\Windows\\\\System32\\\\winevt\\\\Logs\\\\Security.evtx"

def follow(thefile):
    thefile.seek(0, 2)
    while True:
        line = thefile.readline()
        if not line: time.sleep(0.1); continue
        yield line

def send_log(line):
    try:
        requests.post(API_URL, json={
            "log": line.strip(), 
            "source": platform.node(), 
            "timestamp": time.time()
        })
    except: pass

if __name__ == "__main__":
    print(f"[*] Agent started. Sending to {API_URL}")
    try:
        with open(logfile, "r") as f:
            for line in follow(f): send_log(line)
    except Exception as e: print(e)
`
        navigator.clipboard.writeText(script.trim())
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-20">
            <div className="flex items-center justify-between shrink-0">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Canlı İzleme</h1>
                    <p className="text-muted-foreground mt-1">Ajan destekli gerçek zamanlı tehdit tespiti.</p>
                </div>
                <div className="flex items-center gap-2">
                    <div className={cn(
                        "px-3 py-1 rounded-full text-xs font-bold flex items-center gap-2",
                        isStreaming ? "bg-green-500/10 text-green-500" : "bg-red-500/10 text-red-500"
                    )}>
                        <div className={cn("w-2 h-2 rounded-full", isStreaming ? "bg-green-500 animate-pulse" : "bg-red-500")} />
                        {isStreaming ? "CANLI AKIŞ AKTİF" : "BAĞLANTI KOPTU"}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-12 gap-6 h-[600px]">
                {/* Left Sidebar: Active Agents */}
                <div className="col-span-3 glass-card rounded-3xl p-6 flex flex-col">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="font-bold flex items-center gap-2">
                            <Server size={18} className="text-primary" />
                            Aktif Ajanlar
                        </h3>
                        <span className="bg-primary/20 text-primary px-2 py-0.5 rounded text-xs font-bold">{agents.length}</span>
                    </div>

                    {error && (
                        <div className="bg-red-500/20 text-red-500 text-xs p-2 rounded mb-3 border border-red-500/50">
                            {error}
                        </div>
                    )}

                    <div className="space-y-3 flex-1 overflow-auto">
                        {agents.length === 0 ? (
                            <div className="text-center py-10 text-muted-foreground bg-muted/30 rounded-xl">
                                <WifiOff size={32} className="mx-auto mb-2 opacity-50" />
                                <p className="text-sm">Bağlı ajan yok</p>
                            </div>
                        ) : (
                            agents.map((agent) => (
                                <div key={agent.hostname} className="bg-muted/50 p-3 rounded-xl border border-border/50">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="font-bold text-sm">{agent.hostname}</span>
                                        <div className="w-2 h-2 rounded-full bg-green-500" />
                                    </div>
                                    <p className="text-xs text-muted-foreground font-mono">{agent.ip}</p>
                                    <p className="text-[10px] text-muted-foreground mt-1">Son görülme: {new Date(agent.last_seen).toLocaleTimeString()}</p>
                                </div>
                            ))
                        )}
                    </div>

                    {/* Quick Install */}
                    <div className="mt-6 pt-6 border-t border-border">
                        <h4 className="text-xs font-bold uppercase text-muted-foreground mb-3">Yeni Ajan Ekle</h4>
                        <div className="bg-black/80 rounded-lg p-3 relative group">
                            <code className="text-[10px] text-green-400 font-mono block overflow-hidden whitespace-pre-wrap max-h-[60px]">
                                python agent.py {API_BASE}
                            </code>
                            <button
                                onClick={copyAgentScript}
                                className="absolute top-2 right-2 p-1.5 bg-white/10 hover:bg-white/20 rounded-md transition-colors text-white"
                                title="Scripti Kopyala"
                            >
                                {copied ? <Check size={14} /> : <Copy size={14} />}
                            </button>
                        </div>
                        <p className="text-[10px] text-muted-foreground mt-2">
                            Bu Python scriptini sunucunuzda çalıştırarak logları buraya yönlendirin.
                        </p>
                    </div>
                </div>

                {/* Main: Log Stream */}
                <div className="col-span-9 glass-card rounded-3xl p-6 flex flex-col relative overflow-hidden">
                    {/* Terminal Header */}
                    <div className="flex items-center justify-between mb-4 shrink-0 relative z-10">
                        <div className="flex items-center gap-2">
                            <Terminal size={20} className="text-primary" />
                            <h3 className="font-bold">Güvenlik Konsolu</h3>
                        </div>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground font-mono">
                            <span>Total: {logs.length}</span>
                            <span>Buffer: 500</span>
                        </div>
                    </div>

                    {/* Logs Area */}
                    <div className="flex-1 overflow-auto space-y-2 font-mono text-xs pr-2 relative z-10">
                        {logs.length === 0 ? (
                            <div className="h-full flex flex-col items-center justify-center text-muted-foreground opacity-30">
                                <Activity size={64} className="mb-4" />
                                <p className="text-lg">Log akışı bekleniyor...</p>
                                <p className="text-sm">Ajanlardan veri gelmeye başladığında burada görünecek.</p>
                            </div>
                        ) : (
                            logs.map((log) => (
                                <div
                                    key={log.id}
                                    className={cn(
                                        "p-3 rounded-lg border-l-[3px] transition-all hover:bg-muted/50",
                                        log.analysis.is_attack
                                            ? "bg-red-500/10 border-red-500"
                                            : "bg-green-500/5 border-green-500"
                                    )}
                                >
                                    <div className="flex items-center justify-between mb-1">
                                        <div className="flex items-center gap-2 text-muted-foreground">
                                            <span className="opacity-70">{new Date(log.timestamp).toLocaleTimeString()}</span>
                                            <span>•</span>
                                            <span className="text-foreground font-bold">{log.source}</span>
                                            <span>•</span>
                                            <span className="opacity-70">auth.log</span>
                                        </div>
                                        <span className={cn(
                                            "px-2 py-0.5 rounded text-[10px] font-bold uppercase",
                                            log.analysis.is_attack ? "bg-red-500 text-white" : "bg-green-500/20 text-green-500"
                                        )}>
                                            {log.analysis.decision}
                                        </span>
                                    </div>

                                    <p className="text-foreground/90 break-all">{log.content}</p>

                                    {log.analysis.is_attack && (
                                        <div className="mt-2 pt-2 border-t border-red-500/20 flex items-center gap-4">
                                            <span className="flex items-center gap-1 text-red-400 font-bold">
                                                <Shield size={12} />
                                                Güven: %{(log.analysis.confidence * 100).toFixed(1)}
                                            </span>
                                            <span className="flex items-center gap-1 text-primary">
                                                <Cpu size={12} />
                                                Model: {log.analysis.winning_model}
                                            </span>
                                        </div>
                                    )}
                                </div>
                            ))
                        )}
                        <div ref={logsEndRef} />
                    </div>

                    {/* Background Overlay */}
                    {logs.length > 0 && logs[0].analysis.is_attack && (
                        <div className="absolute inset-0 bg-red-500/5 pointer-events-none animate-pulse z-0" />
                    )}
                </div>
            </div>

            {/* Setup Guide Section */}
            <div className="glass-card rounded-3xl p-8 mt-6">
                <h3 className="text-xl font-bold flex items-center gap-2 mb-6">
                    <Download size={24} className="text-primary" />
                    Harici Sunucu Bağlantı Kılavuzu
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Step 1: Download */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold">1</div>
                            <h4 className="font-bold">Ajan Scriptini İndirin</h4>
                        </div>
                        <p className="text-sm text-muted-foreground pl-11">
                            Aşağıdaki butona tıklayarak Python ajan scriptini indirin ve sunucunuza aktarın.
                            <br />
                            <a
                                href={`${API_BASE}/api/download/agent`}
                                download="agent.py"
                                className="inline-flex items-center gap-2 mt-3 bg-white text-black px-4 py-2 rounded-lg font-bold hover:bg-gray-200 transition-colors text-xs border border-white/20 shadow-md"
                            >
                                <Download size={16} />
                                agent.py İndir
                            </a>
                        </p>
                    </div>

                    {/* Step 2: Configure IP */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold">2</div>
                            <h4 className="font-bold">IP Adresini Ayarlayın</h4>
                        </div>
                        <p className="text-sm text-muted-foreground pl-11">
                            Script içindeki <code className="bg-muted px-1 rounded">API_URL</code> değişkenini bu bilgisayarın IP adresiyle değiştirin:
                            <br />
                            <code className="text-xs bg-black/50 p-1 rounded mt-1 block w-fit">API_URL = "http://YOUR_WINDOWS_IP:5050/api/ingest"</code>
                        </p>
                    </div>

                    {/* Step 3: Run */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold">3</div>
                            <h4 className="font-bold">Scripti Çalıştırın</h4>
                        </div>
                        <p className="text-sm text-muted-foreground pl-11">
                            Sunucunuzda terminali açın ve scripti başlatın:
                            <br />
                            <code className="text-xs bg-black/50 p-1 rounded mt-1 block w-fit">python3 agent.py</code>
                        </p>
                    </div>

                    {/* Step 4: Verify */}
                    <div className="space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold">4</div>
                            <h4 className="font-bold">Bağlantıyı Kontrol Edin</h4>
                        </div>
                        <p className="text-sm text-muted-foreground pl-11">
                            Script çalıştıktan sonra bu ekranda "Aktif Ajanlar" listesinde sunucunuzu görmelisiniz.
                            <br />
                            <span className="text-yellow-500 text-xs flex items-center gap-1 mt-1">
                                <AlertCircle size={12} />
                                Bağlantı yoksa Windows Güvenlik Duvarı'ndan 5050 portuna izin verin.
                            </span>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}

function WifiOff(props: any) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <line x1="1" y1="1" x2="23" y2="23" />
            <path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55" />
            <path d="M5 12.55a10.94 10.94 0 0 1 5.17-2.39" />
            <path d="M10.71 5.05A16 16 0 0 1 22.58 9" />
            <path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88" />
            <path d="M8.53 16.11a6 6 0 0 1 6.95 0" />
            <line x1="12" y1="20" x2="12.01" y2="20" />
        </svg>
    )
}
