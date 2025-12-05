'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X, CheckCircle } from 'lucide-react'
import { uploadCSV, uploadPDF, startValidation } from '@/lib/api'
import toast from 'react-hot-toast'
import { useRouter } from 'next/navigation'
import { useAppStore } from '@/lib/store'

export default function UploadPage() {
  const [uploading, setUploading] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<Array<{ name: string; jobId: string; type: string }>>([])
  const router = useRouter()
  const setCurrentJobId = useAppStore((state) => state.setCurrentJobId)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      try {
        setUploading(true)
        let result

        if (file.name.endsWith('.csv')) {
          result = await uploadCSV(file)
        } else if (file.name.endsWith('.pdf')) {
          result = await uploadPDF(file)
        } else {
          toast.error('Only CSV and PDF files are supported')
          continue
        }

        setUploadedFiles((prev) => [
          ...prev,
          { name: file.name, jobId: result.file_id, type: file.name.endsWith('.csv') ? 'CSV' : 'PDF' },
        ])

        toast.success(`${file.name} uploaded successfully`)
        setCurrentJobId(result.file_id)

        // Start validation automatically
        try {
          await startValidation(result.file_id)
          toast.success('Validation started')
        } catch (error) {
          toast.error('Failed to start validation')
        }
      } catch (error: any) {
        toast.error(`Failed to upload ${file.name}: ${error.message}`)
      } finally {
        setUploading(false)
      }
    }
  }, [setCurrentJobId])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/pdf': ['.pdf'],
    },
    multiple: true,
  })

  const removeFile = (index: number) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          Upload Provider Data
        </h1>

        <div
          {...getRootProps()}
          className={`glass rounded-2xl p-12 border-2 border-dashed transition-all cursor-pointer ${
            isDragActive ? 'border-blue-400 glass-strong' : 'border-gray-600'
          }`}
        >
          <input {...getInputProps()} />
          <div className="text-center">
            <Upload className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            {isDragActive ? (
              <p className="text-xl text-blue-400">Drop files here...</p>
            ) : (
              <>
                <p className="text-xl mb-2">Drag & drop files here, or click to select</p>
                <p className="text-gray-400">Supports CSV and PDF files</p>
              </>
            )}
          </div>
        </div>

        {uploadedFiles.length > 0 && (
          <div className="mt-8 glass rounded-2xl p-6">
            <h2 className="text-2xl font-semibold mb-4">Uploaded Files</h2>
            <div className="space-y-3">
              {uploadedFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between glass-strong rounded-lg p-4"
                >
                  <div className="flex items-center gap-3">
                    <File className="w-5 h-5 text-blue-400" />
                    <div>
                      <p className="font-medium">{file.name}</p>
                      <p className="text-sm text-gray-400">{file.type} • Job ID: {file.jobId.slice(0, 8)}...</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <button
                      onClick={() => removeFile(index)}
                      className="p-2 hover:bg-red-500/20 rounded-lg transition-colors"
                    >
                      <X className="w-4 h-4 text-red-400" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <button
              onClick={() => router.push('/dashboard')}
              className="mt-6 w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white py-3 rounded-lg font-semibold hover:opacity-90 transition-opacity"
            >
              View Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  )
}


