import Link from 'next/link'
import { ArrowRight, Upload, BarChart3, FileCheck } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Provider Data Validation
          </h1>
          <p className="text-xl text-gray-400 mb-8">
            AI-powered provider data validation and directory management system
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          <Link
            href="/upload"
            className="glass p-8 rounded-2xl hover:glass-strong transition-all transform hover:scale-105"
          >
            <Upload className="w-12 h-12 mb-4 text-blue-400" />
            <h2 className="text-2xl font-semibold mb-2">Upload Data</h2>
            <p className="text-gray-400">Upload CSV or PDF files with provider information</p>
            <ArrowRight className="w-5 h-5 mt-4 text-blue-400" />
          </Link>

          <Link
            href="/dashboard"
            className="glass p-8 rounded-2xl hover:glass-strong transition-all transform hover:scale-105"
          >
            <BarChart3 className="w-12 h-12 mb-4 text-purple-400" />
            <h2 className="text-2xl font-semibold mb-2">Dashboard</h2>
            <p className="text-gray-400">View validation results and analytics</p>
            <ArrowRight className="w-5 h-5 mt-4 text-purple-400" />
          </Link>

          <Link
            href="/dashboard"
            className="glass p-8 rounded-2xl hover:glass-strong transition-all transform hover:scale-105"
          >
            <FileCheck className="w-12 h-12 mb-4 text-green-400" />
            <h2 className="text-2xl font-semibold mb-2">Review</h2>
            <p className="text-gray-400">Review and manage provider records</p>
            <ArrowRight className="w-5 h-5 mt-4 text-green-400" />
          </Link>
        </div>
      </div>
    </div>
  )
}


