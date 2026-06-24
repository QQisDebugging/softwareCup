# 智学工坊 · 前端设计系统重构总规划（执行手册）

本文档是"智学工坊"前端重构的总体规划与执行规范。旨在拉齐团队认知，将一个技术可用型的原型产品，打磨至比肩 Linear、Notion、Vercel 的顶级生产力工具水准。

> **怎么用这份文档**：这是一份**执行手册**，不是愿景文档。目标读者是"coding 能力 OK、但审美一般"的工程师。每一阶段都写明了：改哪个文件、删哪一段、换成什么、用什么颜色/字号/间距、怎么验证。**凡是没写"由你判断"的地方，就照抄数值，不要自己发挥审美。**

---

# 第一部分 · 设计哲学与底层规范

## 🎯 核心设计哲学 (Design Philosophy)

1. **界面服务于任务 (UI Disappears into the Task)**：产品 UI 不是用来炫技的。摒弃一切无谓的装饰（斑马纹渐变、毫无意义的玻璃拟态、为了包裹数据而强行嵌套的卡片）。让工具隐形。
2. **排版即设计 (Typography is Design)**：在数据密集型的教育/工作台场景中，通过字重（Weight）、字号对比（Contrast）、颜色层级（Muted/Ink）来区分信息，而不是画框。
3. **克制的高级感 (Restrained Elegance)**：使用统一的低透明度锐利阴影、平滑的物理缓动曲线与极致纯净的背景色。

## 🛠️ 底层规范 (Design Tokens & Rules)

### 颜色系统 (Color System - OKLCH)
抛弃传统的 Hex/RGB，全面采用 OKLCH 构建感知均匀的色彩体系。
> **禁令**：绝不在产品工作区使用纯黑底色的高反差或廉价的"紫粉渐变"来标榜 AI。纯白或极致极微偏色的浅灰是唯一解。

品牌主色已**确定为深湖蓝 Teal**（hue ≈ 195），而非旧的 Indigo/Violet（268）。

### 交互与动效 (Motion)
重度工作台不需要慢吞吞的芭蕾舞，需要的是干脆利落的物理反馈。
*   **统一曲线 (Timing Function)**: `cubic-bezier(0.16, 1, 0.3, 1)`（Expo Ease-Out），即 `--ease-out`。
*   **时长**: 按钮、状态切换控制在 150ms - 250ms。
*   **骨架过渡**: 收起转圈式的 Spinner，涉及大模型请求或页面长载入时，一律使用带有高光跑马灯效果的骨架屏（Skeleton）。

### 组件反模式清理 (Anti-Patterns to Remove)
*   🚫 **Cards inside Cards (嵌套卡片)**：背景里有卡片，卡片里还有卡片包着数据。**解决**：拍平。用分割线（Rule/Line）和空白（Whitespace）来切分模块。
*   🚫 **Giant Borders & Shadows (厚重边框和弥散阴影)**：`box-shadow: 0 16px 40px` 等过于夸张的悬浮阴影将被彻底删除。**解决**：统一使用极淡二阶阴影 `var(--shadow-sm/md)`，搭配坚实的 `1px solid var(--line)`。
*   🚫 **Fluid Typography in UI (UI中流式排版)**：工具 UI 不要随着窗口平滑缩放字号（Clamp）。**解决**：使用固定的 rem 缩放比例（Base: 13/14px，Headers 18/24px），确保像素级对齐。

---

# 第二部分 · Token 体系（单一真相源 = design-system.css）

所有颜色用 **OKLCH**。字号用**固定 rem**（**禁止** `clamp()` 流式字号）。阴影 blur ≤ 8px。

## 2.1 颜色（直接用这些变量，不要写裸 hex）

| 用途 | 变量 | 值 |
|---|---|---|
| 品牌主色 | `--primary` | `oklch(0.46 0.10 195)` |
| 主色悬停 | `--primary-hover` | `oklch(0.40 0.10 195)` |
| 主色按下 | `--primary-active` | `oklch(0.36 0.09 195)` |
| 主色淡底 | `--primary-soft` | `oklch(0.94 0.035 195)` |
| 主色上的文字 | `--primary-contrast` | `oklch(0.99 0 0)` |
| 页面背景 | `--bg` | `oklch(0.995 0.004 195)` |
| 面板/卡片底 | `--surface` | `oklch(0.985 0.006 195)` |
| 面板悬停 | `--surface-hover` | `oklch(0.97 0.01 195)` |
| 侧栏底 | `--sidebar` | `oklch(0.972 0.008 200)` |
| 正文 | `--ink` | `oklch(0.24 0.022 195)` |
| 标题/强调 | `--ink-strong` | `oklch(0.18 0.02 195)` |
| 二级文本 | `--muted` | `oklch(0.47 0.016 195)` |
| 三级/caption | `--subtle` | `oklch(0.58 0.014 195)` |
| 分隔线 | `--line` | `oklch(0.92 0.008 195)` |
| 强分隔线 | `--line-strong` | `oklch(0.86 0.012 195)` |
| 成功 | `--success` / `--success-soft` | `oklch(0.55 0.12 155)` / `oklch(0.95 0.04 155)` |
| 警告 | `--warning` / `--warning-soft` | `oklch(0.60 0.13 70)` / `oklch(0.96 0.05 70)` |
| 危险 | `--danger` / `--danger-soft` | `oklch(0.55 0.18 25)` / `oklch(0.95 0.04 25)` |
| 信息(教师徽标) | `--info` / `--info-soft` | `oklch(0.52 0.11 240)` / `oklch(0.95 0.035 240)` |

> 旧别名 `--green`/`--amber`/`--red`/`--cyan`/`--shadow`/`--ease-out` 已在 design-system 末尾补齐，可继续用。

## 2.2 字号（固定 rem，1.125 比例）

```
--fs-xs: 0.75rem    /* 12px caption / pill */
--fs-sm: 0.8125rem  /* 13px 正文/按钮/nav */
--fs-base: 0.875rem /* 14px 默认正文 */
--fs-md: 1rem       /* 16px 小标题 */
--fs-lg: 1.125rem   /* 18px section 标题 / topbar h1 */
--fs-xl: 1.25rem    /* 20px */
--fs-2xl: 1.5rem    /* 24px 页面级大标题 */
--fs-3xl: 1.875rem  /* 30px 仅登录页 hero */
行高: --lh-tight 1.25 / --lh-normal 1.5 / --lh-relaxed 1.7
```

## 2.3 间距 / 圆角 / 阴影 / 动效

```
间距: --space-1..7 = 4/8/12/16/20/24/32px
圆角: --radius-xs 4 / -sm 6 / -md 8 / -lg 10 / -xl 12 / -pill 999
阴影: --shadow-sm / --shadow-md（design-system 里 blur 均 ≤6px，禁再放大）
动效: --t-fast 150ms / --t-base 200ms / --t-slow 250ms，曲线 --ease-out = cubic-bezier(0.16,1,0.3,1)
聚焦环: --focus-ring = 0 0 0 3px oklch(0.46 0.10 195 / 0.18)
```

---

# 第三部分 · 进度与执行路线

## 0. 当前进度快照（Phase 1 已完成）

| 阶段 | 状态 | 说明 |
|---|---|---|
| Phase 0 | ✅ 完成 | design-system.css 已建立为单一真相源（约 1300 行，teal/OKLCH） |
| **Phase 1** | ✅ **完成** | AppShell 浅色竖向侧栏 + 细顶栏 + 角色徽标；登录页统一；旧 shell 冲突已清理 |
| Phase 2 | ⬜ 待做 | Dashboard / Teacher 仪表盘降噪（高密度任务面板，删 hero 和假指标） |
| Phase 3 | ⬜ 待做 | LearningView（AI 助教对话）/ GenerationView（长任务）产品化 |
| Phase 4 | ⬜ 待做 | Courses / CourseBuilder / Profiles 列表密度与角色差异 |
| Phase 5 | ⬜ 待做 | AgentsView / TaskDetailView / ReadinessView（删比赛大屏风格） |
| Phase 6 | ⬜ 待做 | 图标线宽统一 + 动效规范 + 表单微组件质感 |

### Phase 1 已完成的具体改动（供接手者核对）

1. **`frontend/src/components/AppShell.vue`**：顶栏 `<header class="topbar">` 从只有标题，改为标题（`.topbar-title`）+ 右侧 `.role-badge`（学生 teal / 教师 blue，带 `GraduationCap`/`Users` 图标）。侧栏已是浅色竖向（brand + 角色化 nav + course-context + identity-chip + 登出）。
2. **`frontend/src/styles/main.css`**：
   - 删除了两份重复的"Gen-3 横向顶栏"shell 覆盖块（原约 1874–2127 行，出现两次）——这块曾把侧栏强行翻成顶部横向导航。
   - 删除了"Gen-1 深色侧栏 foundation"（原 63–193 行：`.sidebar { background: var(--surface-ink) }`、深色 nav、`.sidebar-foot`、`.mini-stack` 等死代码）。
   - 删除了"Gen-2 渐变润色"里的 shell 冲突：`.workspace` 渐变背景、`.topbar` 厚阴影、`.sidebar` 深色渐变、`.button` 的 `border-radius:999px` pill 和渐变背景。
   - `:root` token 从 indigo（268 hue）整体改为 teal（195 hue），与 design-system 对齐。
3. **`frontend/src/styles/design-system.css`**：加固登录页文本颜色——显式给 `.login-brand`、`.login-copy`、`.login-copy .home-eyebrow` 设定 ink/primary 色，防止 main.css/premium-product.css 里残留的白色 hero 文字泄露。
4. **验证**：`npm run build` 通过；`node probe-styles.mjs` 确认 `.app-shell` = `grid 248px 1192px`、`.sidebar` 浅色 `oklch(0.972 0.008 200)` flex-column、`.button` 扁平 teal `border-radius:8px`（非 pill）、`.role-badge` 存在、`--primary` = `oklch(0.46 0.10 195)`。

> **登录页探针显示 `__missing__` 是正常的**：探针在 `/` 路由清除登录态后，路由守卫仍把已登录态重定向。登录页样式已通过 design-system 加固，build 通过即可。要肉眼确认登录页，用浏览器打开 → 退出登录 → 看 `/`。

## 1. 设计方向（不要再改）

- **品牌主色**：深湖蓝 Teal，`oklch(0.46 0.10 195)`。**禁止** indigo/purple/violet、禁止荧光色。
- **导航骨架**：浅色竖向侧栏（248px）+ 细顶栏。**禁止**深色侧栏、禁止横向顶部导航。
- **气质**：工具隐形于任务（Linear / Notion / Vercel）。**禁止**比赛大屏、AI 紫蓝渐变、幽灵卡片、大阴影、营销 hero。
- **角色边界**：学生与教师的入口、页面、动作必须清晰分离，不混在一起。

## 2. 角色边界（路由 + 导航，已落地，勿动）

学生侧栏 nav（`AppShell.vue` 的 `studentNav`）：我的学习 `/dashboard`、我的课程 `/courses`、自定义课程 `/course-builder`、学习画像 `/profiles`、资源生成 `/generation`、AI 助教 `/learning`。

教师侧栏 nav（`teacherNav`）：教学工作台 `/teacher`、班级画像 `/profiles`、课程空间 `/courses`、课程建设 `/course-builder`、资源审核 `/generation`、智能体协同 `/agents`、发布质检 `/quality`。

- 学生独有路由：`/dashboard`、`/learning`。教师独有：`/teacher`、`/agents`、`/quality`。
- 共享路由（`/courses`、`/course-builder`、`/profiles`、`/generation`）在视图内部用 `const isTeacher = computed(() => app.role === 'teacher')` 区分标题、动作、数据边界。
- **`router/index.ts` 的角色门禁不要改**，除非发现明确 bug。

## 3. 旧 CSS 迁移策略（重要）

三个旧文件仍在 `main.ts` 中导入，顺序为：
```ts
import './styles/main.css'
import './styles/product-final.css'
import './styles/premium-product.css'
import './styles/design-system.css' // 最后导入，级联胜出
```

**策略**：design-system.css 是真相源。旧文件里**页面命名空间规则**（`.course-*`、`.profile-*`、`.teacher-*`、`.task-*`、`.agent-*`、`.learning-*` 等）暂时保留，逐步迁移到 design-system 或组件 scoped style 后再删。**优先清理旧文件里的 foundation 冲突段**（token、button、shell、card、gradient、shadow、clamp 字体）。

### 已清理（Phase 1）
- main.css：`:root` token（indigo→teal）、Gen-1 深色侧栏 foundation、Gen-2 shell 渐变、Gen-3 横向顶栏覆盖（两份）。

### 仍待清理（Phase 2–5 随页面改造一起做）
- main.css `.contest-hero` / `.contest-eyebrow` / `.score-ring` / `.contest-score-card` / `.contest-chip-row`（约 944–1097 行，**深色渐变比赛大屏**）—— Phase 5 删。
- main.css `.home-hero`（约 8870–9020 行，**营销 hero**，渐变 + 大 clamp 字体）—— Phase 2 删。
- main.css `.dashboard-workbench` / `.dashboard-workbench-head`（约 9066–9090 行，被各 view 当 hero 用）—— Phase 2 起逐步替换为 `.section-panel` + `.section-head`。
- premium-product.css `.login-shell`/`.login-stage` 暗色 hero（963–1191 行）—— 已被 design-system 压住，Phase 3+ 可删。
- product-final.css 的 `.login-stage`（419–488 行）—— 同上。

**验证每次清理**：改完跑 `npm run build`；启动 `npm run dev`，用学生/教师预设账号登录逐页目检。

---

## Phase 2：Dashboard / Teacher 降噪

**目标**：把首页和教师台从"营销 hero + 假指标卡 + 多层嵌套"改成"高密度任务面板 + 状态列表 + 下一步行动"。

**反模式清单（看到就删/改）**：
- ❌ `.home-hero` / `.dashboard-workbench-head` 里的大标题 + 长描述段 + clamp 字体 → ✅ 用 `.section-head`（h2 18px + p 13px muted）。
- ❌ 装饰性 `.metric-tile` 大数字（如"班级掌握度 78%"占满一卡）→ ✅ 改成表格行或紧凑 `.status-pill` 列表；数字保留但缩小到 `--fs-md`。
- ❌ 嵌套卡片（卡里套卡）→ ✅ 拍平，用 `1px solid var(--line)` 分隔线 + 空白。
- ❌ `.home-course-context-main`、`.teacher-command-core` 这种"主舞台"大块 → ✅ 拆成窄信息条。

### 2.1 DashboardView.vue（学生主页，600 行）

**现状结构**（顶层 section）：
1. `section.dashboard-workbench.student-home-workbench.span-12` — hero：h2 课程标题 + p 描述 + `.home-launchpad`（`.home-course-rail` + `.home-course-context-main` + `.home-context-stack`）
2. `.learning-work-strip.home-status-strip.span-12` — 4 个状态项
3. `.home-panel.span-8` 课程模块地图
4. `.home-panel.span-4` 今日待办
5. `.home-panel.span-7` 学习任务路径
6. `.home-panel.span-5` AI 助教入口
7. `.home-panel.span-7` 资源书架
8. `.home-panel.span-5` 学习反馈
9. `.home-panel.span-12` 学习证据链
10. `.home-panel.span-12` 最近生成任务

**改造步骤**：

**A. 删 hero，换成紧凑页头。** 把第 1 个 section 整段替换为：
```vue
<section class="section-panel span-12">
  <div class="section-head">
    <div>
      <h2>{{ homeMission.courseTitle }}</h2>
      <p>{{ homeMission.courseMeta }} · 下一步：{{ homeMission.focus }}</p>
    </div>
    <div class="row-actions">
      <RouterLink class="button" to="/learning"><MessageCircleQuestion :size="16" />继续学习</RouterLink>
      <RouterLink class="ghost-button" to="/generation"><Sparkles :size="16" />生成资源</RouterLink>
    </div>
  </div>
  <!-- 课程切换从"大卡片 rail"改成行内 chips -->
  <div class="row-actions" style="margin-bottom: var(--space-3)">
    <button v-for="course in courseSwitchCards" :key="course.id"
      type="button" :class="['chip', { active: course.active }]"
      @click="switchCourse(course.id)">
      {{ course.title }}
    </button>
  </div>
</section>
```
- 删除 `.home-launchpad`、`.home-course-rail`、`.home-course-context-main`、`.home-context-stack` 的**模板标记**（这些类的 CSS 在 main.css，模板不用了就成死代码，CSS 后续统一清）。

**B. 状态条保留但降噪。** 第 2 个 `.home-status-strip`：保留 4 项，但确保它用 `display:grid; grid-template-columns: repeat(4,1fr)` + 每项 `<span>` label `--fs-xs muted` / `<strong>` `--fs-md ink-strong` / `<small>` `--fs-xs muted`，**不要**大数字。如 main.css 里 `.learning-work-strip` 有大字号/渐变，在 design-system.css 末尾追加覆盖：
```css
.learning-work-strip { display:grid; grid-template-columns: repeat(4,minmax(0,1fr)); gap: var(--space-3); padding: var(--space-4); background: var(--surface); border:1px solid var(--line); border-radius: var(--radius-lg); }
.learning-work-strip strong { font-size: var(--fs-md); }
.learning-work-strip span, .learning-work-strip small { color: var(--muted); }
```

**C. 其余 `.home-panel` 改用 SectionPanel 组件。** 把 `<section class="home-panel learning-work-panel home-xxx-panel span-N">` 全部改成 `<SectionPanel :span="N">`（项目已有 `SectionPanel.vue` 组件，带 title/subtitle prop + `.section-head`）。每个面板内的列表（`.course-module-list`、`.today-action-list`、`.learning-task-list`、`.resource-shelf-list` 等）保留为**行列表**：每行 = 图标 18px + `<strong>` `--fs-sm` + `<small>` `--fs-xs muted` + 右侧 `StatusPill`。行之间用 `border-bottom: 1px solid var(--line)` 分隔，**不要**卡片套卡片。

**D. 假指标降级。** `learningWorkItems` 的 4 项里"掌握度 XX%"这种，value 用 `--fs-md`，不要 `--fs-3xl`。

**保留**：`courseModules`、`todayQueue`、`pathNodes`、`resourceShelf`、`tasks` 这些**真实数据列表**是核心，保留逻辑，只改呈现密度。

### 2.2 TeacherView.vue（教师工作台，632 行）

**现状**：hero `.dashboard-workbench-head` + `.teacher-command-core`（home-eyebrow + h3 + 大段）+ `dl.teacher-control-metrics`（4 个大数字）+ 4 个 `.metric-tile.teacher-kpi-tile.span-3`（班级掌握度/参与度/风险学生/资源缺口）+ 一堆 `.teacher-*-panel` SectionPanel。

**改造步骤**：

**A. 删双重 hero。** 顶部只留一个 `.section-head`（h2 课程标题 + p 一句话）。删除 `.teacher-command-core`（home-eyebrow "课程运营" + 大 h3 + 段落）和 `.teacher-control-metrics` 的 `<dl>` 大数字条。如果 `topic`（分析主题）有用，放进 `.section-head` 的 p 里。

**B. 假指标卡 → 横条。** 4 个 `.metric-tile.teacher-kpi-tile.span-3` 改成一行紧凑横条：
```vue
<div class="teacher-kpi-strip">
  <div><span>班级掌握度</span><strong>{{ classMasteryDisplay }}</strong></div>
  <div><span>参与度</span><strong>{{ participationDisplay }}</strong></div>
  <div><span>风险学生</span><strong>{{ riskCount }}</strong></div>
  <div><span>资源缺口</span><strong>{{ gapCount }}</strong></div>
</div>
```
design-system.css 追加：
```css
.teacher-kpi-strip { display:grid; grid-template-columns: repeat(4,minmax(0,1fr)); gap: var(--space-3); padding: var(--space-4); background: var(--surface); border:1px solid var(--line); border-radius: var(--radius-lg); }
.teacher-kpi-strip strong { display:block; margin-top:4px; font-size: var(--fs-lg); color: var(--ink-strong); font-variant-numeric: tabular-nums; }
.teacher-kpi-strip span { font-size: var(--fs-xs); color: var(--muted); }
```

**C. 12 个 `.teacher-*-panel` 保留 SectionPanel 结构，但每页别超过 6–8 个。** 合并同类：诊断 + 班级学情分析 → 一个"班级学情"面板；3 个 chart 面板（掌握度图/风险分布/资源缺口）可保留但确保用 `ChartPanel` 组件、高度 ≤ 240px；风险学生 + 干预分组 + 资源缺口 → 各自一个**列表**面板（行 = 学生名 + StatusPill + 一句话），不要网格卡。`.teacher-review-gates`（教师复核要求）保留为 gate 列表。

**D. 角色**：TeacherView 全程教师视角，不需要 isTeacher 分支。

### 2.3 Phase 2 验证
```powershell
cd D:\softwareCup\frontend
npm run build   # 必须通过
npm run dev     # 登录学生账号看 /dashboard，登录教师看 /teacher，目检：无大 hero、无假指标大卡、列表紧凑
```

---

## Phase 3：LearningView / GenerationView 产品化

### 3.1 LearningView.vue（AI 助教，1180 行，**有 bug**）

**现状**：9 个 section。核心是 section #5（`span-7 learning-tutor-panel`）的 `.learning-chat-shell`：
- `.tutor-prompt-dock`（快捷问题按钮）
- `.tutor-thread` 里**只有 2 个硬编码 article**（一条用户 + 一条 AI），**且 AI article 内有两份重复的 `<div class="chat-bubble user">` 渲染 `form.question`（约 931–932 行）——这是 copy-paste bug，要删一份**。
- `.tutor-composer`（textarea + 发送按钮）
- **无流式/打字机**，只有 `<LoadingBlock text="正在生成辅导回答">`。
- markdown 用 `<MarkdownView>`，但**没设阅读宽度**（65–75ch）。
- 工具调用展示在 section #1 的 `.learning-agent-runway`（4 步），不在气泡内。

**改造步骤（参考 ai-elements skill）**：

**A. 修 bug。** 删掉 `.tutor-message-assistant` 内重复的那份 `<div class="chat-bubble user">`。

**B. 把"单轮硬编码"改成"消息数组"。** 在 `<script setup>` 加：
```ts
interface ChatMessage { role: 'user' | 'assistant'; content: string; status?: 'streaming' | 'done'; sources?: string[] }
const messages = ref<ChatMessage[]>([])
```
发送时 push 用户消息 + 一条 `status:'streaming'` 的 assistant 占位；拿到 `tutoringResult` 后把占位更新为 `status:'done'` + markdown。模板：
```vue
<div class="tutor-thread">
  <article v-for="(m,i) in messages" :key="i" :class="['tutor-message', m.role==='user'?'tutor-message-user':'tutor-message-assistant']">
    <div class="tutor-avatar">{{ m.role==='user'?'我':'AI' }}</div>
    <div class="chat-bubble">
      <LoadingBlock v-if="m.status==='streaming'" text="正在生成辅导回答" />
      <MarkdownView v-else :content="m.content" />
      <div v-if="m.sources?.length" class="tutor-sources">
        <span class="chip" v-for="s in m.sources" :key="s">{{ s }}</span>
      </div>
    </div>
  </article>
</div>
```

**C. 阅读宽度 65–75ch。** design-system.css 已有 `.markdown-body { max-width: 75ch }`。确保 `<MarkdownView>` 渲染的容器带 `.markdown-body` 类，或在 `.learning-chat-shell .chat-bubble` 上加 `max-width: 72ch`。

**D. 消息状态 + 工具调用。** 把 `.learning-agent-runway`（4 步证据检索/辅导生成/随堂测评/画像更新）做成**气泡上方的折叠工具条**，每步一个 `StatusPill`，点击展开看 detail。不要把工具步骤做成大卡片。

**E. 输入区。** `.tutor-composer` 保留 textarea + 发送按钮。发送按钮 loading 时禁用并显示 spinner（用 design-system 的 `.spinner`）。

**F. 删 section #1 的 hero（`.dashboard-workbench.learning-workbench` + `.learning-command-band` 大块）。** 换成 `.section-head`（h2 "AI 助教" + p 课程·画像·mission）+ 一个折叠的"会话上下文"区。

**G. 保留**：section #6 随堂测评、#7 批改、#8 学习效果、#9 学习记录——这些是真实功能，只降噪（SectionPanel + 列表），别删逻辑。

### 3.2 GenerationView.vue（长任务，820 行）

**现状**：7 个 section。hero `.generation-workbench` + `.generation-command-band`（agent-console + course-rail + package-board）+ form（资源类型 picker + 预设模板）+ scope 面板 + 审核队列 + 任务记录。

**改造步骤**：

**A. 长任务必须有 skeleton。** 当前只用 `<LoadingBlock>`。在提交后、任务列表区用 `.skeleton` 占位行（design-system 已有 `.skeleton` + shimmer 动画）：
```vue
<div v-if="submitting" class="resource-production-grid">
  <div v-for="n in 3" :key="n" class="resource-production-card">
    <div class="skeleton" style="height:14px;width:60%"></div>
    <div class="skeleton" style="height:10px;width:40%;margin-top:8px"></div>
    <div class="skeleton" style="height:8px;margin-top:12px"></div>
  </div>
</div>
```

**B. 资源类型选择去重。** `.resource-type-picker`（section #3 的按钮网格）和 `.generation-agent-actions` 里的 `<select v-model="form.resourceType">`（section #1）**是重复控件**，只保留 picker 网格，删 select。

**C. 进度展示。** `.resource-production-card` 的 `.progress-track`/`.progress-fill` 保留（design-system 标准）。状态用 `StatusPill`，不要自造彩色块。`.generation-agent-runway`（4 步）同 LearningView，做成折叠工具条。

**D. 删 hero。** `.dashboard-workbench.generation-workbench` + `.generation-command-band` 大块换成 `.section-head` + 折叠上下文。

**E. 角色差异**：标题 teacher "班级资源包" / student "学习资源"；section #5 审核队列仅 teacher（`v-if="isTeacher"` 已有）。

### 3.3 Phase 3 验证
`npm run build`；登录学生 → `/learning` 发问看对话流式 + markdown 宽度；`/generation` 提交看 skeleton + 进度条；教师 → `/generation` 看审核队列。

---

## Phase 4：Courses / CourseBuilder / Profiles

三个 view 共同模式：都是 `.dashboard-workbench.xxx-workbench.span-12` hero 开头 + `*-command-band`（course-rail + overview-lane + metric-list）+ SectionPanel 列表。

### 4.1 通用改造（三个 view 都做）
- **删 hero**：`.dashboard-workbench-head` + `*-overview-lane`（`.xxx-overview-copy` + `.xxx-context-strip` + `dl.xxx-metric-list`）→ 换成 `.section-head`（h2 + p 一句话）+ 行内课程切换 chips（同 Phase 2.1A）。
- **假指标 `dl.xxx-metric-list`（4 个 KPI）→ 紧凑横条**（同 TeacherView 2.2B 的 `.teacher-kpi-strip` 模式）。
- **课程切换 rail**（`.course-switch-rail`/`.builder-course-rail`/`.profile-*`）→ 行内 chips 或窄下拉，不要竖向大卡片 rail。

### 4.2 CoursesView.vue
- `.courseware-workspace`（outline + reader + rail 三栏）**保留**，这是真实工作区。降噪：reader 用 `.markdown-body`；outline 模块列表用行（index + 标题 + StatusPill）；action rail 的 KPI（`.courseware-action-stack` 3 卡）降级为横条。
- `.course-archive-panel` 的 `.split-row`（课程目录 timeline + 资源 library）保留列表密度。
- 角色：标题 teacher "课程空间" / student "我的课程"；`publishedOnly: !isTeacher` 已有。

### 4.3 CourseBuilderView.vue
- 模块最多，hero + 6 个 `*-lane/queue/strip` 装饰区（`.builder-overview-lane`/`.builder-action-queue`/`.builder-readiness-strip`/`.builder-next-actions`/`.builder-check-grid`/`.context-grid`）。**合并降噪**：overview-lane 删；action-queue + readiness-strip 合并成一个"课程就绪"列表面板；next-actions 保留为 3 行行动列表。
- 上传区 `.upload-studio`（dropzone + inspector）保留；文件列表 `.upload-file-list` 用行。
- 草稿编辑 `.course-draft-workspace`（form + preview）保留，确保用 `.form-grid` + `.field`。
- 角色：标题 teacher "课程建设" / student "自定义课程"；模板 `visibleCourseBuildTemplates` 过滤掉教师班级模板（学生）。

### 4.4 ProfilesView.vue
- hero `.profile-overview-lane` + `.profile-metric-list`（4 KPI）→ 删，换 `.section-head` + kpi-strip。
- `.profile-current-panel` 里的 `.profile-hero` + `.profile-score-card`（大百分比"画像覆盖度"）→ 降级为横条数字，**不要**大百分比卡。
- `.profile-dimensions-panel` 的 8 个 `.dimension-coverage-card` 保留为**网格**（这是维度覆盖核心），但卡片用 `.section-panel` 风格（flat，无大阴影）。
- `.profile-directory-grid`（档案目录卡）→ teacher 列全部学生、student 只列自己（`visibleProfiles` 已有过滤）。
- 对话采集 `.profile-dialogue-console` + 抽取 `.profile-extraction-form` 保留。
- 角色：h2 teacher "班级画像" / student "学习画像"；学生姓名输入框 student 只读（已有）。

### 4.5 Phase 4 验证
`npm run build`；学生/教师分别走 `/courses`、`/course-builder`、`/profiles`，确认标题、动作、数据边界按角色切换；列表紧凑、无大 hero。

---

## Phase 5：AgentsView / TaskDetailView / ReadinessView（**删比赛大屏**）

### 5.1 ReadinessView.vue（**重点**，326 行，比赛演示大屏风格）

**现状**：
1. `SectionPanel.span-12` 标题"发布质检"
2. **`section.contest-hero.span-12`** —— 比赛大屏 hero：`.contest-eyebrow` + h2 readiness 判定 + p + `.score-ring`（大 `<strong>` overallScore + "质量分"）
3. 6 个 `.metric-tile.span-2`（多智能体/资源类型/任务完成/学习路径/学习事件/内容审核）
4. `.span-8` 需求完成度（`.requirement-grid` + `.requirement-card`）
5. `.span-4` 建议处理顺序
6. `.span-6` 可用能力与建议
7. `.span-6` 元数据

**对应 CSS（main.css 约 944–1097 行）的违规点**：
- `.contest-hero`：`color:#fff`、`background: linear-gradient(135deg, rgba(14,116,144,.24), rgba(15,138,85,.1)), #17233a`（深色渐变）、`box-shadow: var(--shadow)`。
- `.contest-hero .button`：`background:#f6ad37`（琥珀色 CTA）。
- `.contest-hero h2`：`font-size:30px`。
- `.contest-eyebrow`：绿色半透明 pill。
- `.score-ring`：`aspect-ratio:1` + `.score-ring strong { font-size:42px }`（庆祝性大分）。

**改造步骤（改成产品级发布质检：gates + 证据链 + 风险项 + 可执行动作）**：

**A. 删 contest-hero，换成 gate 头。** 把第 2 个 section 整段替换：
```vue
<section class="section-panel span-12">
  <div class="section-head">
    <div>
      <h2>发布质检 · {{ readinessLevel }}</h2>
      <p>{{ qualitySummary || '点击"重新生成"按当前画像、课程、资源任务范围生成发布质检结果。' }}</p>
    </div>
    <div class="row-actions">
      <StatusPill :status="readinessLevel" :tone="readinessTone" />
      <button class="ghost-button" @click="regenerate"><RefreshCw :size="16" />重新生成</button>
    </div>
  </div>
  <!-- 质量分从"大圆环"降级为横条数字 -->
  <div class="readiness-score-strip">
    <div><span>质量分</span><strong>{{ report?.overallScore ?? '-' }}</strong></div>
    <div v-for="m in metricCards" :key="m.label"><span>{{ m.label }}</span><strong>{{ m.value }}<small> / {{ m.target }}</small></strong></div>
  </div>
</section>
```
design-system.css 追加：
```css
.readiness-score-strip { display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: var(--space-3); margin-top: var(--space-4); }
.readiness-score-strip > div { padding: var(--space-3) var(--space-4); background: var(--surface); border:1px solid var(--line); border-radius: var(--radius-md); }
.readiness-score-strip strong { display:block; margin-top:4px; font-size: var(--fs-lg); color: var(--ink-strong); font-variant-numeric: tabular-nums; }
.readiness-score-strip span { font-size: var(--fs-xs); color: var(--muted); }
.readiness-score-strip small { color: var(--subtle); font-size: var(--fs-xs); }
```
- **删除模板里 `.contest-hero`、`.contest-eyebrow`、`.score-ring` 的所有标记。**
- **删除 6 个 `.metric-tile.span-2`**（已并入 `.readiness-score-strip`）。

**B. 需求完成度做成 gates。** `.span-8` 的 `.requirement-grid` 改成**gate 列表**：每项 = 名称 + StatusPill（pass/fail）+ 证据 chip + 一句话风险说明。不要网格卡，用行列表（border-bottom 分隔）。
```vue
<ul class="gate-list">
  <li v-for="r in requirements" :key="r.name" class="gate-row">
    <StatusPill :status="r.status" :tone="r.tone" />
    <div class="gate-main">
      <strong>{{ r.name }}</strong>
      <small>{{ r.evidence || '缺证据' }}</small>
    </div>
  </li>
</ul>
```
design-system.css：
```css
.gate-list { display:grid; gap:0; }
.gate-row { display:grid; grid-template-columns: auto minmax(0,1fr); gap: var(--space-3); align-items:start; padding: var(--space-3) 0; border-bottom:1px solid var(--line); }
.gate-row:last-child { border-bottom:0; }
.gate-main strong { display:block; color: var(--ink-strong); font-size: var(--fs-sm); }
.gate-main small { color: var(--muted); font-size: var(--fs-xs); }
```

**C. 建议处理顺序 / 可用能力 / 元数据** 保留 SectionPanel，内容做成**可执行动作列表**（每条 = 动作 + 去哪做 + StatusPill），不要装饰 chip row。

**D. 删 CSS。** 改完 ReadinessView 后，删 main.css 约 944–1097 行的 `.contest-hero`/`.contest-eyebrow`/`.contest-score-card`/`.contest-chip-row`/`.score-ring`/`.score-weight-*`/`.gold-roadmap`/`.roadmap-card` 整段（确认全局无其他引用后）。用 grep 确认：
```
grep -rn "contest-hero\|contest-eyebrow\|score-ring\|contest-score-card" frontend/src
```
若只剩 main.css，删之。

### 5.2 TaskDetailView.vue（632 行）
- hero `.dashboard-workbench.task-workbench` + `.task-command-panel`（3 栏 workbench）保留 workbench 布局，但删 `.dashboard-workbench-head` 的大 hero，换 `.section-head`。
- `.task-evidence-grid` 的 4 个 `.metric-tile`（出现两次）→ 降级为横条（同前）。
- `.task-stage-lane`（6 stage 卡 + 各自进度条）保留，这是真实进度，降噪即可（卡用 flat）。
- `.timeline`/`.timeline-item`（处理记录、实时进度、审核）保留——timeline 是 design-system 标准类。
- `.resource-publish-strip` + `<MarkdownView>` 保留，确保 markdown 用 `.markdown-body`。

### 5.3 AgentsView.vue（教师智能体协同）
- hero `.dashboard-workbench.agents-workbench` 删大 hero，换 `.section-head`。
- `.orchestration-board`（6 stage 卡）保留为**生产线流程**，卡用 flat `.section-panel` 风格。
- `.agent-tool-grid`（18 工具卡）保留但确保密度（每卡 = 标题 + StatusPill + 一句话，无大阴影）。
- `.agent-composer`（输入 + 运行）保留；`.agent-review-panel` + `.agent-artifact-panel`（timeline）保留。
- 无假指标卡（AgentsView 本就没有 metric-tile），主要降噪 hero + 确保卡 flat。

### 5.4 Phase 5 验证
`npm run build`；教师 → `/quality` 确认**无深色渐变 hero、无大圆环分数**，是 gate 列表 + 横条分数；`/tasks/:id`、`/agents` 目检 flat、无比赛风。

---

## Phase 6：图标 + 动效 + 表单微组件

### 6.1 图标（lucide-vue-next）
- **统一 stroke-width 1.5**。lucide 默认 2，需显式传 `:stroke-width="1.5"`，或全局在 `main.ts` 设默认（lucide-vue-next 支持 `<script setup>` 内无法全局设，需每处传，或在最外层包一层）。
- **尺寸规范**：nav 图标 18–19px（AppShell 已用 19）；普通 UI/列表图标 16px；按钮内图标 16px；hero/大区域 17–20px。
- **不要**混用 emoji 或其他图标库。

### 6.2 动效
- **仅用于状态变化和空间连续性**：按钮 hover/active、状态切换、列表进入。时长 150–250ms，曲线 `var(--ease-out)`。
- **长任务用 skeleton**，不要 spinner（除非 ≤200ms 的即时操作）。
- **支持 `prefers-reduced-motion`**：design-system.css 末尾已有 `@media (prefers-reduced-motion: reduce)` 全局降级到 0.01ms，保留。
- **禁止**：飞行入场、视差、大型 stagger、自动轮播。

### 6.3 表单与微组件质感（沿用旧 Phase 4 愿景，design-system 已落地）
- **高级表单**：`.field` 的 input/select/textarea 已统一——默认 `1px solid var(--line-strong)`，hover 转 `--muted`，focus 转 `--primary` + `--focus-ring`。圆角 `--radius-sm`。**不要再加厚边框**。
- **状态胶囊 (StatusPill)**：已定义，padding 左右 10px、高 24px、`--fs-xs`、`font-weight 650`。语义色 `ok/warn/danger/info/muted`，底色超低透明度 soft + 主色字，**不可做成浑浊中性灰**。
- **按钮**：`.button`（teal 实心）、`.ghost-button`（描边 hover 转 primary-soft）、`.icon-button`（38px 方形）。深浅色系不要再自造。
- **Empty States**：`.empty-state`（居中虚线框）/ `.empty-guide`（左对齐带下一步行动引导）。空状态要"提供下一步行动引导"，不是"暂无数据"了事。

---

# 第四部分 · 验证清单（每阶段必跑）

```powershell
cd D:\softwareCup\frontend

# 1. 类型 + 构建（必须通过）
npm run build

# 2. 启动开发服务器
npm run dev

# 3. 探针（确认 design-system 压住旧 CSS）
node probe-styles.mjs
# 若端口不是 5173：$env:PROBE_URL="http://127.0.0.1:5173"; node probe-styles.mjs
```

**目检角色矩阵**（每阶段至少走一遍）：
| 页面 | 学生账号 zhang.student/student@2026 | 教师账号 li.teacher/teacher@2026 |
|---|---|---|
| /dashboard | ✅ 学生主页 | （重定向到 /teacher） |
| /teacher | （重定向） | ✅ 教学工作台 |
| /learning | ✅ AI 助教 | （重定向） |
| /courses | 我的课程 | 课程空间 |
| /course-builder | 自定义课程 | 课程建设 |
| /profiles | 学习画像（只读自己） | 班级画像（全部学生） |
| /generation | 资源生成 | 资源审核 |
| /agents | （重定向） | 智能体协同 |
| /quality | （重定向） | 发布质检 |

**每阶段交付前自检**：
- [ ] `npm run build` 通过
- [ ] 无大 hero / 营销渐变 / 比赛 hero
- [ ] 无装饰性大数字卡（假指标）
- [ ] 列表紧凑、用分隔线而非嵌套卡
- [ ] 颜色全用 token 变量，无裸 hex
- [ ] 字号固定 rem，无 clamp
- [ ] 学生/教师边界清晰
- [ ] 更新本文档对应阶段的"已完成"勾选

---

# 第五部分 · 旧 CSS 待清理登记表（随阶段推进勾选）

| 文件 | 段落 | 行号(约) | 状态 | 处理阶段 |
|---|---|---|---|---|
| main.css | `:root` token | 1–35 | ✅ 已清(teal) | Phase 1 |
| main.css | Gen-1 深色侧栏 foundation | 原 63–193 | ✅ 已删 | Phase 1 |
| main.css | Gen-2 shell 渐变/按钮 pill | 原 1205–1278 | ✅ 已删 | Phase 1 |
| main.css | Gen-3 横向顶栏覆盖(×2) | 原 1865–2127 | ✅ 已删 | Phase 1 |
| main.css | `.home-hero` 营销 hero | 8870–9020 | ⬜ 待删 | Phase 2 |
| main.css | `.dashboard-workbench*` hero | 9066–9090 | ⬜ 待迁移 | Phase 2–4 |
| main.css | `.contest-*`/`.score-ring` 比赛 | 944–1097 | ⬜ 待删 | Phase 5 |
| main.css | `.home-launchpad`/`.home-course-context-main` | 1713/4774/5227/6447/11251 | ⬜ 模板弃用后删 | Phase 2 |
| premium-product.css | `.login-*` 暗色 hero | 963–1191 | ⬜ 已被压住，可删 | Phase 3+ |
| product-final.css | `.login-stage` | 419–488 | ⬜ 已被压住，可删 | Phase 3+ |

> 删除任何旧 CSS 段前，先 `grep -rn "类名" frontend/src` 确认无引用，再删。

---

# 附录 A：设计系统组件类速查（design-system.css 已提供，直接用）

- 布局：`.page-grid`、`.span-3..span-12`、`.split-row`、`.section-panel`、`.section-head`
- 按钮：`.button`（teal 实心）、`.ghost-button`（描边）、`.icon-button`（38px 方形）
- 表单：`.form-grid`、`.field`、`.field-error`、`.field-help`、`.password-field`、`.required-mark`
- 状态：`.status-pill.ok/.warn/.danger/.info/.muted`、`.role-badge.is-student/.is-teacher`
- 数据：`.metric-tile`、`.table-wrap`/`table`、`.clickable-row`、`.timeline`/`.timeline-item`/`.timeline-index`/`.timeline-body`
- 反馈：`.notice`/`.error-notice`/`.warn-notice`、`.empty-state`、`.empty-guide`、`.loading-block`、`.spinner`、`.skeleton`、`.progress-track`/`.progress-fill`
- 文本：`.markdown-body`（75ch）、`.chip`、`.compact-list`、`.json-block`
- Shell：`.app-shell`、`.sidebar`、`.brand`、`.nav-list`/`.nav-item`、`.workspace`、`.topbar`、`.page-scroll`、`.course-context`、`.identity-chip`
- 登录：`.login-shell`/`.login-stage`/`.login-copy`/`.login-card`/`.auth-tabs`/`.account-login-form`/`.preset-account-row`/`.role-register-row`/`.login-submit`

---

# 附录 B：绝对禁止清单（看到就停）

- ❌ 任何 `linear-gradient` 用作背景装饰（登录页 radial primary-soft 除外，已定义）
- ❌ 任何 `box-shadow` blur > 8px 或多层弥散大阴影
- ❌ 任何 `clamp()` 字号
- ❌ 任何裸 hex 颜色（必须走 token 变量）
- ❌ indigo/purple/violet/荧光色
- ❌ 深色侧栏 / 横向顶部导航
- ❌ 卡片嵌套卡片（拍平用分隔线）
- ❌ 比赛大屏、庆祝性大分数圆环、琥珀/金色 CTA
- ❌ emoji 图标、混用图标库
- ❌ 自动轮播、视差、大型入场动画
- ❌ 把学生和教师的入口/页面/动作混在同一个无分支的区块里

---
*(本文档为动态更新文档，随着重构阶段逐步确认和打钩)*
