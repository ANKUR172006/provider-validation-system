'use client'

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getDashboardStats, getProviders, getJobStatus, downloadResults } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Download, RefreshCw, Search, Filter } from 'lucide-react'
import toast from 'react-hot-toast'
import ProviderDetailModal from '@/components/ProviderDetailModal'
import { motion } from 'framer-motion'

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']

export default function DashboardPage() {
  const currentJobId = useAppStore((state) => state.currentJobId)
  const [selectedProvider, setSelectedProvider] = useState<any>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')

  const { data: stats, refetch: refetchStats } = useQuery({
    queryKey: ['dashboard-stats', currentJobId],
    queryFn: () => getDashboardStats(currentJobId || undefined),
    enabled: !!currentJobId,
    refetchInterval: 2000,
  })

  const { data: jobStatus } = useQuery({
    queryKey: ['job-status', currentJobId],
    queryFn: () => getJobStatus(currentJobId!),
    enabled: !!currentJobId,
    refetchInterval: 2000,
  })

  const { data: providersData, refetch: refetchProviders } = useQuery({
    queryKey: ['providers', currentJobId],
    queryFn: () => getProviders(currentJobId!, 1, 100),
    enabled: !!currentJobId,
    refetchInterval: 2000,
  })

  const handleDownload = async () => {
    if (!currentJobId) return
    try {
      const blob = await downloadResults(currentJobId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `validation_results_${currentJobId}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      toast.success('Results downloaded successfully')
    } catch (error) {
      toast.error('Failed to download results')
    }
  }

  const filteredProviders = providersData?.providers?.filter((p: any) => {
    const matchesSearch = !searchTerm || 
      p.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.npi?.includes(searchTerm) ||
      p.specialty?.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesFilter = filterStatus === 'all' ||
      (filterStatus === 'validated' && p.is_validated) ||
      (filterStatus === 'review' && p.needs_review) ||
      (filterStatus === 'suspicious' && p.is_suspicious)
    
    return matchesSearch && matchesFilter
  }) || []

  const validationStatusData = stats?.validation_status ? Object.entries(stats.validation_status).map(([name, value]) => ({
    name,
    value,
  })) : []

  const specialtyData = stats?.specialty_distribution ? Object.entries(stats.specialty_distribution).map(([name, value]) => ({
    name,
    value,
  })) : []

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Dashboard
          </h1>
          <div className="flex gap-3">
            <button
              onClick={() => { refetchStats(); refetchProviders() }}
              className="glass px-4 py-2 rounded-lg hover:glass-strong transition-all flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            <button
              onClick={handleDownload}
              className="glass px-4 py-2 rounded-lg hover:glass-strong transition-all flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Download
            </button>
          </div>
        </div>

        {jobStatus && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass rounded-2xl p-6 mb-8"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-semibold mb-2">Validation Status</h3>
                <p className="text-gray-400">
                  {jobStatus.status} • {jobStatus.processed_providers} / {jobStatus.total_providers} providers
                </p>
              </div>
              <div className="w-64">
                <div className="w-full bg-gray-700 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all"
                    style={{ width: `${jobStatus.progress_percentage}%` }}
                  />
                </div>
                <p className="text-sm text-gray-400 mt-1">{jobStatus.progress_percentage.toFixed(1)}% complete</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass rounded-2xl p-6"
          >
            <p className="text-gray-400 mb-2">Total Providers</p>
            <p className="text-3xl font-bold">{stats?.total_providers || 0}</p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass rounded-2xl p-6"
          >
            <p className="text-gray-400 mb-2">Auto-Validated</p>
            <p className="text-3xl font-bold text-green-400">{stats?.auto_validated || 0}</p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="glass rounded-2xl p-6"
          >
            <p className="text-gray-400 mb-2">Needs Review</p>
            <p className="text-3xl font-bold text-yellow-400">{stats?.needs_review || 0}</p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="glass rounded-2xl p-6"
          >
            <p className="text-gray-400 mb-2">Avg Confidence</p>
            <p className="text-3xl font-bold text-blue-400">
              {stats?.average_confidence ? (stats.average_confidence * 100).toFixed(1) : 0}%
            </p>
          </motion.div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5 }}
            className="glass rounded-2xl p-6"
          >
            <h3 className="text-xl font-semibold mb-4">Validation Status</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={validationStatusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {validationStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6 }}
            className="glass rounded-2xl p-6"
          >
            <h3 className="text-xl font-semibold mb-4">Specialty Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={specialtyData.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }} />
                <Bar dataKey="value" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Providers Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="glass rounded-2xl p-6"
        >
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold">Providers</h3>
            <div className="flex gap-3">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="glass pl-10 pr-4 py-2 rounded-lg w-64"
                />
              </div>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="glass px-4 py-2 rounded-lg"
              >
                <option value="all">All</option>
                <option value="validated">Validated</option>
                <option value="review">Needs Review</option>
                <option value="suspicious">Suspicious</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left p-3">Name</th>
                  <th className="text-left p-3">NPI</th>
                  <th className="text-left p-3">Specialty</th>
                  <th className="text-left p-3">Confidence</th>
                  <th className="text-left p-3">Status</th>
                  <th className="text-left p-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredProviders.map((provider: any) => (
                  <tr
                    key={provider.id}
                    className="border-b border-gray-800 hover:glass-strong transition-all cursor-pointer"
                    onClick={() => setSelectedProvider(provider)}
                  >
                    <td className="p-3">{provider.name}</td>
                    <td className="p-3 text-gray-400">{provider.npi || 'N/A'}</td>
                    <td className="p-3 text-gray-400">{provider.specialty || provider.validated_specialty || 'N/A'}</td>
                    <td className="p-3">
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-gray-700 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                            style={{ width: `${(provider.confidence_overall || 0) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm">{(provider.confidence_overall || 0) * 100}%</span>
                      </div>
                    </td>
                    <td className="p-3">
                      {provider.is_validated && (
                        <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-sm">Validated</span>
                      )}
                      {provider.needs_review && (
                        <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 rounded text-sm">Review</span>
                      )}
                      {provider.is_suspicious && (
                        <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-sm">Suspicious</span>
                      )}
                    </td>
                    <td className="p-3">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setSelectedProvider(provider)
                        }}
                        className="text-blue-400 hover:text-blue-300"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>

      {selectedProvider && (
        <ProviderDetailModal
          provider={selectedProvider}
          onClose={() => setSelectedProvider(null)}
        />
      )}
    </div>
  )
}


