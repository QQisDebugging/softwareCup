import { get, post } from '@/api/http'
import type { Course, CreateCourseRequest, LearningResource, ResourceType } from '@/types/api'

export const coursesApi = {
  list: () => get<Course[]>('/courses'),
  create: (body: CreateCourseRequest) => post<Course, CreateCourseRequest>('/courses', body),
  get: (courseId: string) => get<Course>(`/courses/${courseId}`),
  resources: (courseId: string) => get<LearningResource[]>(`/courses/${courseId}/resources`),
  resourceTypes: () => get<ResourceType[]>('/resource-types'),
}
