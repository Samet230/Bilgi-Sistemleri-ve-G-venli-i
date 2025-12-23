import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
}

export function formatBytes(bytes: number, decimals = 2) {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const dm = decimals < 0 ? 0 : decimals
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

export function formatDate(date: Date | string) {
    return new Date(date).toLocaleDateString('tr-TR', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

export function getThreatColor(severity: string) {
    const colors = {
        CRITICAL: 'text-red-500 bg-red-500/10 border-red-500/20',
        HIGH: 'text-orange-500 bg-orange-500/10 border-orange-500/20',
        MEDIUM: 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20',
        LOW: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
        INFO: 'text-gray-400 bg-gray-400/10 border-gray-400/20',
    }
    return colors[severity as keyof typeof colors] || colors.INFO
}
