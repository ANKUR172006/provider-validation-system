'use client'

import { useState } from 'react'
import { X, Mail, CheckCircle, AlertCircle, XCircle } from 'lucide-react'
import { generateEmailTemplate } from '@/lib/api'
import toast from 'react-hot-toast'
import { motion, AnimatePresence } from 'framer-motion'

interface ProviderDetailModalProps {
  provider: any
  onClose: () => void
}

export default function ProviderDetailModal({ provider, onClose }: ProviderDetailModalProps) {
  const [emailTemplate, setEmailTemplate] = useState<any>(null)
  const [generatingEmail, setGeneratingEmail] = useState(false)

  const handleGenerateEmail = async () => {
    setGeneratingEmail(true)
    try {
      const template = await generateEmailTemplate(provider.id, 'review_request')
      setEmailTemplate(template)
      toast.success('Email template generated')
    } catch (error) {
      toast.error('Failed to generate email template')
    } finally {
      setGeneratingEmail(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard')
  }

  return (
    <AnimatePresence>
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="glass-strong rounded-2xl p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        >
          <div className="flex justify-between items-start mb-6">
            <h2 className="text-3xl font-bold">{provider.name}</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-red-500/20 rounded-lg transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Confidence Score */}
          <div className="glass rounded-xl p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold">Overall Confidence</h3>
              <span className="text-2xl font-bold text-blue-400">
                {(provider.confidence_overall * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-4">
              <div
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-4 rounded-full transition-all"
                style={{ width: `${provider.confidence_overall * 100}%` }}
              />
            </div>
          </div>

          {/* Status Badges */}
          <div className="flex gap-3 mb-6">
            {provider.is_validated && (
              <div className="flex items-center gap-2 px-4 py-2 bg-green-500/20 text-green-400 rounded-lg">
                <CheckCircle className="w-4 h-4" />
                Validated
              </div>
            )}
            {provider.needs_review && (
              <div className="flex items-center gap-2 px-4 py-2 bg-yellow-500/20 text-yellow-400 rounded-lg">
                <AlertCircle className="w-4 h-4" />
                Needs Review
              </div>
            )}
            {provider.is_suspicious && (
              <div className="flex items-center gap-2 px-4 py-2 bg-red-500/20 text-red-400 rounded-lg">
                <XCircle className="w-4 h-4" />
                Suspicious
              </div>
            )}
          </div>

          {/* Original vs Validated Data */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="glass rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4">Original Data</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="text-gray-400">Name</p>
                  <p>{provider.name || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-gray-400">NPI</p>
                  <p>{provider.npi || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-gray-400">Phone</p>
                  <p>{provider.phone || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-gray-400">Address</p>
                  <p>{provider.address || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-gray-400">Specialty</p>
                  <p>{provider.specialty || 'N/A'}</p>
                </div>
              </div>
            </div>

            <div className="glass rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4">Validated Data</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="text-gray-400">Name</p>
                  <p className="flex items-center gap-2">
                    {provider.validated_name || provider.name || 'N/A'}
                    {provider.validated_name && (
                      <span className="text-xs text-green-400">✓ Validated</span>
                    )}
                  </p>
                </div>
                <div>
                  <p className="text-gray-400">Phone</p>
                  <p className="flex items-center gap-2">
                    {provider.validated_phone || provider.phone || 'N/A'}
                    {provider.validated_phone && (
                      <span className="text-xs text-green-400">✓ Validated</span>
                    )}
                  </p>
                </div>
                <div>
                  <p className="text-gray-400">Address</p>
                  <p className="flex items-center gap-2">
                    {provider.validated_address || provider.address || 'N/A'}
                    {provider.validated_address && (
                      <span className="text-xs text-green-400">✓ Validated</span>
                    )}
                  </p>
                </div>
                <div>
                  <p className="text-gray-400">Specialty</p>
                  <p className="flex items-center gap-2">
                    {provider.validated_specialty || provider.specialty || 'N/A'}
                    {provider.validated_specialty && (
                      <span className="text-xs text-green-400">✓ Validated</span>
                    )}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Confidence Scores */}
          <div className="glass rounded-xl p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">Field Confidence Scores</h3>
            <div className="space-y-3">
              {[
                { label: 'Name', value: provider.confidence_name },
                { label: 'Phone', value: provider.confidence_phone },
                { label: 'Address', value: provider.confidence_address },
                { label: 'Specialty', value: provider.confidence_specialty },
                { label: 'Email', value: provider.confidence_email },
              ].map((field) => (
                <div key={field.label}>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm">{field.label}</span>
                    <span className="text-sm text-gray-400">{(field.value * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all"
                      style={{ width: `${field.value * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Issues */}
          {provider.issues && provider.issues.length > 0 && (
            <div className="glass rounded-xl p-6 mb-6 border-l-4 border-yellow-500">
              <h3 className="text-lg font-semibold mb-4 text-yellow-400">Issues Identified</h3>
              <ul className="space-y-2">
                {provider.issues.map((issue: string, index: number) => (
                  <li key={index} className="flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{issue}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Validation Notes */}
          {provider.validation_notes && (
            <div className="glass rounded-xl p-6 mb-6">
              <h3 className="text-lg font-semibold mb-2">Validation Notes</h3>
              <p className="text-sm text-gray-400">{provider.validation_notes}</p>
            </div>
          )}

          {/* Email Template */}
          <div className="glass rounded-xl p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Email Template</h3>
              <button
                onClick={handleGenerateEmail}
                disabled={generatingEmail}
                className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg transition-colors disabled:opacity-50"
              >
                <Mail className="w-4 h-4" />
                {generatingEmail ? 'Generating...' : 'Generate Email'}
              </button>
            </div>

            {emailTemplate && (
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-400 mb-1">Subject</p>
                  <div className="glass-strong rounded-lg p-3 flex justify-between items-center">
                    <p className="text-sm">{emailTemplate.subject}</p>
                    <button
                      onClick={() => copyToClipboard(emailTemplate.subject)}
                      className="text-xs text-blue-400 hover:text-blue-300"
                    >
                      Copy
                    </button>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-400 mb-1">Body</p>
                  <div className="glass-strong rounded-lg p-3">
                    <pre className="text-sm whitespace-pre-wrap font-sans">{emailTemplate.body}</pre>
                    <button
                      onClick={() => copyToClipboard(emailTemplate.body)}
                      className="mt-2 text-xs text-blue-400 hover:text-blue-300"
                    >
                      Copy Body
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}


