import { asArray, asObject, del, get, post, postForm } from '@/api/http'
import type { UploadAsset } from '@/types/api'

function normalizeUpload(value: unknown, index = 0): UploadAsset {
  const asset = asObject<UploadAsset>(value, {
    id: `upload-${index + 1}`,
    originalFilename: `资料 ${index + 1}`,
    contentType: '',
    sizeBytes: 0,
    storagePath: '',
    purpose: 'course-material',
    courseId: '',
    uploaderRole: 'student',
    materialType: 'FILE',
    parseStatus: 'STORED',
    parseMessage: '',
    extractedTextPreview: '',
    knowledgePointsJson: '[]',
    courseDraftJson: '{}',
    createdAt: '',
  })
  return {
    ...asset,
    id: asset.id || `upload-${index + 1}`,
    originalFilename: asset.originalFilename || `资料 ${index + 1}`,
    sizeBytes: Number(asset.sizeBytes || 0),
    purpose: asset.purpose || 'course-material',
    uploaderRole: asset.uploaderRole || 'student',
    materialType: asset.materialType || 'FILE',
    parseStatus: asset.parseStatus || 'STORED',
    parseMessage: asset.parseMessage || '',
    extractedTextPreview: asset.extractedTextPreview || '',
    knowledgePointsJson: asset.knowledgePointsJson || '[]',
    courseDraftJson: asset.courseDraftJson || '{}',
    createdAt: asset.createdAt || '',
  }
}

export const uploadsApi = {
  uploadCourseMaterial: async (file: File, options: { courseId?: string; role?: string } = {}) => {
    const body = new FormData()
    body.append('file', file)
    if (options.courseId) body.append('courseId', options.courseId)
    body.append('role', options.role || 'student')
    return normalizeUpload(await postForm<unknown>('/uploads/course-materials', body))
  },
  listCourseMaterials: async (courseId?: string) =>
    asArray<unknown>(await get<unknown>('/uploads/course-materials', courseId ? { courseId } : undefined)).map((item, index) =>
      normalizeUpload(item, index),
    ),
  reparseCourseMaterial: async (assetId: string) => normalizeUpload(await post<unknown>(`/uploads/course-materials/${assetId}/reparse`)),
  deleteCourseMaterial: async (assetId: string) => del<void>(`/uploads/course-materials/${assetId}`),
}
