import type { Meta, StoryObj } from '@storybook/vue3-vite'
import StatusPill from './StatusPill.vue'

const meta = {
  title: 'Product/StatusPill',
  component: StatusPill,
  tags: ['autodocs'],
  argTypes: {
    tone: {
      control: 'select',
      options: ['ok', 'warn', 'danger', 'info', 'muted'],
    },
  },
  args: {
    status: '可发布',
    tone: 'ok',
  },
} satisfies Meta<typeof StatusPill>

export default meta
type Story = StoryObj<typeof meta>

export const Ready: Story = {
  args: {
    status: '可发布',
    tone: 'ok',
  },
}

export const ReviewRequired: Story = {
  args: {
    status: '待复核',
    tone: 'warn',
  },
}

export const Blocked: Story = {
  args: {
    status: '需处理',
    tone: 'danger',
  },
}

export const AllStates: Story = {
  render: () => ({
    components: { StatusPill },
    template: `
      <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
        <StatusPill status="可发布" tone="ok" />
        <StatusPill status="待复核" tone="warn" />
        <StatusPill status="需处理" tone="danger" />
        <StatusPill status="生成中" tone="info" />
        <StatusPill status="未开始" tone="muted" />
      </div>
    `,
  }),
}
