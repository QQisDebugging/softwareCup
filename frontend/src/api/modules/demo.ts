import { asApiRecord, asArray, asObject, get, post } from '@/api/http'
import type { ContestReadinessReport, ContestRequirementEvidence } from '@/types/api'

const emptyReadinessReport: ContestReadinessReport = {
  generatedAt: '',
  scope: '',
  overallScore: 0,
  summary: '',
  metrics: {},
  requirements: [],
  demoHighlights: [],
  recommendedDemoFlow: [],
}

function normalizeRequirement(value: unknown, index: number): ContestRequirementEvidence {
  const requirement = asObject<ContestRequirementEvidence>(value, {
    requirementCode: `REQ-${index + 1}`,
    category: '赛题要求',
    title: `要求 ${index + 1}`,
    status: 'PENDING',
    score: 0,
    target: '',
    actual: '',
    evidenceEndpoints: [],
    evidenceNotes: [],
  })
  return {
    ...requirement,
    requirementCode: requirement.requirementCode || `REQ-${index + 1}`,
    category: requirement.category || '赛题要求',
    title: requirement.title || `要求 ${index + 1}`,
    status: requirement.status || 'PENDING',
    score: Number(requirement.score || 0),
    target: requirement.target || '',
    actual: requirement.actual || '',
    evidenceEndpoints: asArray<string>(requirement.evidenceEndpoints),
    evidenceNotes: asArray<string>(requirement.evidenceNotes),
  }
}

function normalizeReadinessReport(value: unknown): ContestReadinessReport {
  const report = asObject<ContestReadinessReport>(value, emptyReadinessReport)
  return {
    ...emptyReadinessReport,
    ...report,
    generatedAt: report.generatedAt || '',
    scope: report.scope || '全局演示范围',
    overallScore: Number(report.overallScore || 0),
    summary: report.summary || '后端未生成评委报告，请启动 Spring Boot 后端并刷新。',
    metrics: asObject(report.metrics, {}),
    requirements: asArray<unknown>(report.requirements).map(normalizeRequirement),
    demoHighlights: asArray<string>(report.demoHighlights),
    recommendedDemoFlow: asArray<string>(report.recommendedDemoFlow),
  }
}

export const demoApi = {
  readinessReport: (params: { studentProfileId?: string; courseId?: string; taskId?: string }) =>
    get<unknown>('/demo/readiness-report', params).then(normalizeReadinessReport),
  scenarioPlan: async (body: unknown) => asApiRecord(await post<unknown, unknown>('/demo/scenario-plans', body)),
}
