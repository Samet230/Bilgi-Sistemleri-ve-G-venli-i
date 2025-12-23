"use client"

import React, { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
    LayoutDashboard,
    Upload,
    ShieldAlert,
    Activity,
    Settings,
    Search,
    ChevronLeft,
    ChevronRight,
    LogOut,
    Zap
} from 'lucide-react'
import { cn } from '@/lib/utils'

const SidebarItem = ({ icon: Icon, label, href, active, collapsed }: {
    icon: any,
    label: string,
    href: string,
    active: boolean,
    collapsed: boolean
}) => (
    <Link
        href={href}
        className={cn(
            "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative",
            active
                ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
        )}
    >
        <Icon size={20} className={cn("shrink-0", active ? "scale-110" : "group-hover:scale-110 transition-transform")} />
        {!collapsed && <span className="font-medium">{label}</span>}
        {collapsed && (
            <div className="absolute left-full ml-4 px-2 py-1 bg-black text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50">
                {label}
            </div>
        )}
    </Link>
)

export default function Sidebar() {
    const [collapsed, setCollapsed] = useState(false)
    const pathname = usePathname()

    const items = [
        { icon: LayoutDashboard, label: 'Panel', href: '/' },
        { icon: Upload, label: 'Dosya Yükle', href: '/upload' },
        { icon: Activity, label: 'Canlı İzleme', href: '/monitor' },
        { icon: ShieldAlert, label: 'Saldırı Raporları', href: '/reports' },
        { icon: Search, label: 'Analiz', href: '/analysis' },
    ]

    return (
        <aside
            className={cn(
                "fixed left-0 top-0 h-full bg-card border-r border-border flex flex-col transition-all duration-300 z-40",
                collapsed ? "w-20" : "w-64"
            )}
        >
            <div className="p-6 flex items-center justify-between">
                {!collapsed && (
                    <div className="flex items-center gap-2 font-bold text-xl tracking-tight text-primary">
                        <Zap className="fill-primary" />
                        <span>LogIz AI</span>
                    </div>
                )}
                <button
                    onClick={() => setCollapsed(!collapsed)}
                    className="p-1.5 rounded-lg bg-muted hover:bg-primary/20 text-muted-foreground hover:text-primary transition-colors"
                >
                    {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
                </button>
            </div>

            <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto custom-scrollbar">
                {items.map((item) => (
                    <SidebarItem
                        key={item.href}
                        {...item}
                        active={pathname === item.href}
                        collapsed={collapsed}
                    />
                ))}
            </nav>

            <div className="p-4 mt-auto border-t border-border">
                <div className={cn(
                    "bg-muted/50 rounded-2xl p-3 flex items-center gap-3",
                    collapsed ? "justify-center" : ""
                )}>
                    <div className="w-8 h-8 rounded-full grad-blue flex items-center justify-center text-white font-bold text-xs shrink-0">
                        SŞ
                    </div>
                    {!collapsed && (
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold truncate">Samet Şahin</p>
                            <p className="text-xs text-muted-foreground truncate">Admin</p>
                        </div>
                    )}
                    {!collapsed && (
                        <button className="text-muted-foreground hover:text-destructive transition-colors">
                            <LogOut size={16} />
                        </button>
                    )}
                </div>
            </div>
        </aside>
    )
}
