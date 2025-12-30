"use client"

import React from 'react'
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell
} from 'recharts'

// Traffic Trend Chart
interface TrafficDataPoint {
    time: string
    normal: number
    attack: number
}

interface TrafficChartProps {
    data: TrafficDataPoint[]
    loading?: boolean
}

export function TrafficChart({ data, loading }: TrafficChartProps) {
    if (loading) {
        return (
            <div className="w-full h-full flex items-center justify-center">
                <div className="animate-pulse text-muted-foreground">Yükleniyor...</div>
            </div>
        )
    }

    return (
        <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                    <linearGradient id="colorNormal" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorAttack" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                    </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
                <XAxis
                    dataKey="time"
                    stroke="#a3a3a3"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                />
                <YAxis
                    stroke="#a3a3a3"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                />
                <Tooltip
                    contentStyle={{
                        backgroundColor: '#1f1f1f',
                        border: '1px solid #333',
                        borderRadius: '8px',
                        color: '#fff'
                    }}
                />
                <Area
                    type="monotone"
                    dataKey="normal"
                    name="Normal Trafik"
                    stroke="#3b82f6"
                    fillOpacity={1}
                    fill="url(#colorNormal)"
                    strokeWidth={2}
                />
                <Area
                    type="monotone"
                    dataKey="attack"
                    name="Saldırı"
                    stroke="#ef4444"
                    fillOpacity={1}
                    fill="url(#colorAttack)"
                    strokeWidth={2}
                />
            </AreaChart>
        </ResponsiveContainer>
    )
}

// Attack Distribution Pie Chart
interface AttackDistribution {
    name: string
    value: number
    color: string
}

interface AttackPieChartProps {
    data: AttackDistribution[]
    loading?: boolean
}

const COLORS = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#8b5cf6']

export function AttackPieChart({ data, loading }: AttackPieChartProps) {
    if (loading || data.length === 0) {
        return (
            <div className="w-full h-full flex items-center justify-center">
                <div className="text-muted-foreground text-sm">
                    {loading ? "Yükleniyor..." : "Veri yok"}
                </div>
            </div>
        )
    }

    return (
        <ResponsiveContainer width="100%" height="100%">
            <PieChart>
                <Pie
                    data={data}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    labelLine={false}
                >
                    {data.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color || COLORS[index % COLORS.length]} />
                    ))}
                </Pie>
                <Tooltip
                    contentStyle={{
                        backgroundColor: '#1f1f1f',
                        border: '1px solid #333',
                        borderRadius: '8px',
                        color: '#fff'
                    }}
                />
            </PieChart>
        </ResponsiveContainer>
    )
}

// Skeleton Loader Component
export function ChartSkeleton() {
    return (
        <div className="w-full h-full animate-pulse">
            <div className="h-full bg-muted/20 rounded-xl flex items-center justify-center">
                <div className="text-muted-foreground text-sm">Grafik Yükleniyor...</div>
            </div>
        </div>
    )
}
