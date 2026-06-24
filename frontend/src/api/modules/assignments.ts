import { get, post } from '@/api/http'

export interface QuizQuestion {
  id: string
  stem: string
  options: string[]
  answer: number | null
}

export interface AssignmentSubmissionView {
  content: string
  answers: Record<string, number>
  score: number | null
  total: number | null
  submittedAt: string
}

export interface CourseAssignment {
  id: string
  courseId: string
  type: 'homework' | 'quiz'
  title: string
  publisher: string
  description: string
  deadlineLabel: string | null
  estimatedMinutes: number
  questions: QuizQuestion[]
  submission: AssignmentSubmissionView | null
  createdAt: string
}

export interface CreateAssignmentBody {
  type: 'homework' | 'quiz'
  title: string
  publisher?: string
  description?: string
  deadlineLabel?: string
  estimatedMinutes?: number
  questions?: Array<{ id: string; stem: string; options: string[]; answer: number }>
}

export interface SubmitAssignmentBody {
  studentProfileId: string
  content?: string
  answers?: Record<string, number>
}

export const assignmentsApi = {
  list: async (courseId: string, studentProfileId?: string) =>
    (await get<CourseAssignment[]>(`/courses/${courseId}/assignments`, studentProfileId ? { studentProfileId } : undefined)) ?? [],
  create: async (courseId: string, body: CreateAssignmentBody) =>
    post<CourseAssignment, CreateAssignmentBody>(`/courses/${courseId}/assignments`, body),
  submit: async (assignmentId: string, body: SubmitAssignmentBody) =>
    post<CourseAssignment, SubmitAssignmentBody>(`/assignments/${assignmentId}/submissions`, body),
}
