import { asArray, asObject, get, post } from '@/api/http'
import type { Course, CreateCourseRequest, LearningResource, ResourceType } from '@/types/api'

function normalizeCourse(value: unknown, fallback: Course): Course {
  const course = asObject<Course>(value, fallback)
  return {
    ...fallback,
    ...course,
    id: course.id || fallback.id,
    title: course.title || fallback.title || '未命名课程',
    department: course.department || fallback.department || '-',
    description: course.description || fallback.description || '暂无课程描述',
    creditHours: Number(course.creditHours || fallback.creditHours || 0),
    syllabusJson: course.syllabusJson || fallback.syllabusJson || '',
    createdAt: course.createdAt || fallback.createdAt || '',
    updatedAt: course.updatedAt || fallback.updatedAt || '',
  }
}

function normalizeResource(value: unknown, index: number): LearningResource {
  const resource = asObject<LearningResource>(value, {
    id: `resource-${index + 1}`,
    courseId: '',
    sourceTaskId: '',
    title: `学习资源 ${index + 1}`,
    resourceType: '',
    resourceTypeName: '',
    modality: '',
    targetLevel: '',
    estimatedMinutes: 0,
    content: '',
    createdAt: '',
    updatedAt: '',
  })
  return {
    ...resource,
    id: resource.id || `resource-${index + 1}`,
    title: resource.title || `学习资源 ${index + 1}`,
    resourceTypeName: resource.resourceTypeName || resource.resourceType || '资源',
    modality: resource.modality || '文本',
    targetLevel: resource.targetLevel || '-',
    estimatedMinutes: Number(resource.estimatedMinutes || 0),
    content: resource.content || '',
  }
}

function normalizeResourceType(value: unknown, index: number): ResourceType {
  const type = asObject<ResourceType>(value, { code: `RESOURCE_${index + 1}`, displayName: `资源类型 ${index + 1}` })
  return {
    code: type.code || `RESOURCE_${index + 1}`,
    displayName: type.displayName || type.code || `资源类型 ${index + 1}`,
  }
}

export const coursesApi = {
  list: async () =>
    asArray<unknown>(await get<unknown>('/courses')).map((item, index) =>
      normalizeCourse(item, {
        id: `course-${index + 1}`,
        title: `课程 ${index + 1}`,
        department: '',
        description: '',
        creditHours: 0,
        syllabusJson: '',
        createdAt: '',
        updatedAt: '',
      }),
    ),
  create: async (body: CreateCourseRequest) =>
    normalizeCourse(await post<unknown, CreateCourseRequest>('/courses', body), {
      id: '',
      createdAt: '',
      updatedAt: '',
      ...body,
    }),
  get: async (courseId: string) =>
    normalizeCourse(await get<unknown>(`/courses/${courseId}`), {
      id: courseId,
      title: '未命名课程',
      department: '',
      description: '',
      creditHours: 0,
      syllabusJson: '',
      createdAt: '',
      updatedAt: '',
    }),
  resources: async (courseId: string) =>
    asArray<unknown>(await get<unknown>(`/courses/${courseId}/resources`)).map((item, index) => normalizeResource(item, index)),
  resourceTypes: async () => asArray<unknown>(await get<unknown>('/resource-types')).map((item, index) => normalizeResourceType(item, index)),
}
