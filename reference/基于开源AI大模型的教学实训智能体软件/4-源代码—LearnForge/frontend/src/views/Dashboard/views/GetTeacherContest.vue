<template>
    <v-container>
        <v-alert v-if="error" type="error" dismissible>{{ error }}</v-alert>

        <v-row>
            <v-col v-for="contest in contests" :key="contest.contest_id" cols="12">
                <v-card class="mb-3">
                    <v-card-title>
                        {{ contest.contest_name }}
                    
                        <v-btn icon @click="confirmDelete(contest)" size="small" variant="flat">
                            <v-icon color="red">mdi-delete</v-icon>
                        </v-btn>
                    </v-card-title>
                    <v-card-text>
                        <div><strong>竞赛编号:</strong> {{ contest.contest_id }}</div>
                        <div><strong>发布时间:</strong> {{ formattedSubmissionDate(contest.publish_date) }}</div>
                        <div><strong>题目类型:</strong> {{ contest.question_type }}</div>
                    </v-card-text>
                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn color="primary" @click="openDialog(contest)">查看题目</v-btn>
                        <v-btn color="primary" @click="goToDetail(contest.contest_id)">查看提交情况</v-btn>
                    </v-card-actions>
                </v-card>
            </v-col>
        </v-row>

        <v-dialog v-model="dialog" fullscreen hide-overlay transition="dialog-bottom-transition">
            <v-card>
                <v-toolbar dark color="primary">
                    <v-btn icon dark @click="closeDialog">
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                    <v-toolbar-title>题目详情</v-toolbar-title>
                </v-toolbar>
                <v-card-text>
                    <v-container>
                        <template v-if="selectedAssignment">
                            <v-row>
                                <component :is="currentComponent" :questionsJson="selectedAssignment.question_json" />
                            </v-row>
                        </template>
                    </v-container>
                </v-card-text>
            </v-card>
        </v-dialog>

        <v-dialog v-model="deleteDialog" max-width="500px">
            <v-card>
                <v-card-title class="headline">确认删除</v-card-title>
                <v-card-text>您确定要删除竞赛 "{{ selectedContestToDelete?.contest_name }}" 吗？</v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="red" @click="deleteContest">删除</v-btn>
                    <v-btn color="grey" @click="closeDeleteDialog">取消</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-container>
</template>

<script>
import moment from 'moment';
import axios from '@/utils/axiosConfig';
import ChoiceQuestionListTeacher from '@/components/ChoiceQuestionListTeacher.vue';
import JudgeQuestionListTeacher from '@/components/JudgeQuestionListTeacher.vue';
import BriefQuestionListTeacher from '@/components/BriefQuestionListTeacher.vue';

export default {
    components: {
        ChoiceQuestionListTeacher,
        JudgeQuestionListTeacher,
        BriefQuestionListTeacher
    },
    data() {
        return {
            contests: [],
            tno: localStorage.getItem("username") || "2000001",
            error: '',
            dialog: false,
            deleteDialog: false,
            selectedAssignment: null,
            selectedContestToDelete: null
        };
    },
    created() {
        this.fetchContestDetail();
    },
    computed: {
        currentComponent() {
            if (!this.selectedAssignment) return null;
            switch (this.selectedAssignment.question_type) {
                case '选择题':
                    return 'ChoiceQuestionListTeacher';
                case '判断题':
                    return 'JudgeQuestionListTeacher';
                case '问答题':
                    return 'BriefQuestionListTeacher';
                default:
                    return null;
            }
        }
    },
    methods: {
        formattedSubmissionDate(submissionDate) {
            return moment(submissionDate).format('YYYY-MM-DD HH:mm');
        },
        goToDetail(contestId) {
            this.$router.push({ name: 'ContestDetail', params: { contest_id: contestId } });
        },
        openDialog(contest) {
            this.selectedAssignment = contest;
            this.dialog = true;
        },
        closeDialog() {
            this.dialog = false;
            this.selectedAssignment = null;
        },
        confirmDelete(contest) {
            this.selectedContestToDelete = contest;
            this.deleteDialog = true;
        },
        closeDeleteDialog() {
            this.deleteDialog = false;
            this.selectedContestToDelete = null;
        },
        async deleteContest() {
            try {
                await axios.post(`${this.$backendUrl}/api/deleteContest`, {
                    contest_id: this.selectedContestToDelete.contest_id,
                    tno: localStorage.getItem('username')
                },{
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }});
                this.contests = this.contests.filter(contest => contest.contest_id !== this.selectedContestToDelete.contest_id);
                this.closeDeleteDialog();
            } catch (error) {
                this.error = '删除竞赛失败，请稍后再试';
            }
        },
        async fetchContestDetail() {
            try {
                const response = await axios.get(`${this.$backendUrl}/api/getTeacherContests`, {
                    params: { tno: this.tno }
                });
                this.contests = response.data;
            } catch (error) {
                this.error = '获取竞赛详情失败，请稍后再试';
            }
        }
    }
};
</script>

<style scoped>
.v-container {
    max-width: 800px;
    margin: auto;
}
</style>
