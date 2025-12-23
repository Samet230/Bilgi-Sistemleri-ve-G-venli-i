"use client"

import React, { useState, useEffect } from 'react'
import {
  ShieldAlert,
  Activity,
  Database,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  ShieldCheck,
  Cpu,
  RefreshCw
} from 'lucide-react'
import { cn } from '@/lib/utils'
import axios from 'axios'

const API_BASE = "http://localhost:5050"

const StatCard = ({ title, value, icon: Icon, trend, trendValue, color, loading }: any) => (
  <div className="glass-card rounded-3xl p-6 space-y-4 group hover:border-primary/30 transition-all duration-500">
    <div className="flex items-center justify-between">
      <div className={cn("p-2.5 rounded-2xl bg-muted group-hover:bg-primary/10 transition-colors", color)}>
        <Icon size={24} />
      </div>
      {trend && (
        <div className={cn(
          "flex items-center gap-1 text-xs font-bold px-2 py-1 rounded-full",
          trend === 'up' ? "bg-red-500/10 text-red-500" : "bg-green-500/10 text-green-500"
        )}>
          {trend === 'up' ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
          {trendValue}
        </div>
      )}
    </div>
    <div>
      <p className="text-muted-foreground text-sm font-medium">{title}</p>
      <h3 className={cn("text-3xl font-bold tracking-tight mt-1", loading && "animate-pulse text-muted-foreground")}>
        {loading ? "..." : value}
      </h3>
    </div>
  </div>
)

interface Alert {
  id: number
  attack_type: string
  dataset_source: string
  probability: number
  detected_at: string
}

export default function DashboardPage() {
  const [stats, setStats] = useState({ totalLogs: 0, attacks: 0, normal: 0 })
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    setLoading(true)
    try {
      // Fetch aggregated stats from backend (Real Data)
      const response = await axios.get(`${API_BASE}/api/stats`)
      const data = response.data

      setStats({
        totalLogs: data.total_logs,
        attacks: data.total_attacks,
        normal: data.total_logs - data.total_attacks
      })

      setAlerts(data.recent_alerts)

    } catch (error) {
      console.error("Failed to fetch dashboard stats:", error)
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Güvenlik Paneli</h1>
          <p className="text-muted-foreground mt-2">Sistem genelindeki anomali tespiti ve trafik istatistikleri.</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchData}
            className="p-2 rounded-xl bg-muted hover:bg-primary/10 text-muted-foreground hover:text-primary transition-colors"
            title="Yenile"
          >
            <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
          </button>
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-green-500/10 text-green-500 text-sm font-bold border border-green-500/20">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            Sistem Aktif
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Toplam Log"
          value={stats.totalLogs.toLocaleString()}
          icon={Database}
          trend="down"
          trendValue="%12"
          color="text-blue-500"
          loading={loading}
        />
        <StatCard
          title="Tespit Edilen Saldırı"
          value={stats.attacks.toLocaleString()}
          icon={ShieldAlert}
          trend="up"
          trendValue="%24"
          color="text-red-500"
          loading={loading}
        />
        <StatCard
          title="AI Doğruluk"
          value="%100"
          icon={ShieldCheck}
          color="text-green-500"
        />
        <StatCard
          title="Sistem Yükü"
          value="%14"
          icon={Cpu}
          color="text-purple-500"
        />
      </div>

      {/* Main Content Areas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Placeholder for Charts */}
        <div className="lg:col-span-2 glass-card rounded-3xl p-8 h-[400px] flex flex-col items-center justify-center text-center space-y-4 border-dashed">
          <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center text-muted-foreground">
            <TrendingUp size={32} />
          </div>
          <div>
            <h3 className="text-xl font-bold text-muted-foreground">Trafik Trendi</h3>
            <p className="text-sm text-muted-foreground opacity-60">Recharts entegre edilecek...</p>
          </div>
        </div>

        {/* System Logs / Alerts side panel */}
        <div className="glass-card rounded-3xl p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="font-bold flex items-center gap-2">
              <Activity size={18} className="text-primary" />
              Son Uyarılar
            </h3>
            <a href="/reports" className="text-xs text-primary hover:underline">Tümünü Gör</a>
          </div>

          <div className="space-y-4">
            {alerts.length === 0 && !loading && (
              <p className="text-sm text-muted-foreground text-center py-4">Henüz uyarı yok.</p>
            )}
            {alerts.map((alert) => (
              <div key={alert.id} className="flex items-start gap-3 p-3 rounded-2xl bg-muted/30 hover:bg-muted/50 transition-colors cursor-pointer group">
                <div className={cn(
                  "w-2 h-2 rounded-full mt-2 shrink-0 group-hover:scale-125 transition-transform",
                  alert.attack_type === "SALDIRI" ? "bg-red-500" : "bg-yellow-500"
                )} />
                <div className="min-w-0">
                  <p className="text-sm font-semibold truncate">
                    {alert.attack_type === "SALDIRI" ? "Saldırı Tespit Edildi" : "Şüpheli Aktivite"} ({alert.dataset_source})
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">Olasılık: %{(alert.probability * 100).toFixed(1)}</p>
                  <p className="text-[10px] text-muted-foreground/50 mt-1 uppercase">Az Önce</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
