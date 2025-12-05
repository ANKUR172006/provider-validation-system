import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Upload endpoints
export const uploadCSV = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/upload/csv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const uploadPDF = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/upload/pdf', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// Validation endpoints
export const startValidation = async (jobId: string) => {
  const response = await api.post('/validation/start', {
    job_id: jobId,
    file_ids: [],
  })
  return response.data
}

export const getJobStatus = async (jobId: string) => {
  const response = await api.get(`/validation/status/${jobId}`)
  return response.data
}

export const getProviders = async (jobId: string, page: number = 1, pageSize: number = 50) => {
  const response = await api.get(`/validation/providers/${jobId}`, {
    params: { page, page_size: pageSize },
  })
  return response.data
}

export const getProvider = async (providerId: number) => {
  const response = await api.get(`/validation/provider/${providerId}`)
  return response.data
}

// Dashboard endpoints
export const getDashboardStats = async (jobId?: string) => {
  const response = await api.get('/dashboard/stats', {
    params: jobId ? { job_id: jobId } : {},
  })
  return response.data
}

export const downloadResults = async (jobId: string) => {
  const response = await api.get(`/dashboard/download-results?job_id=${jobId}`, {
    responseType: 'blob',
  })
  return response.data
}

// Email endpoints
export const generateEmailTemplate = async (providerId: number, templateType: string = 'review_request') => {
  const response = await api.post('/email/template', {
    provider_id: providerId,
    template_type: templateType,
  })
  return response.data
}


