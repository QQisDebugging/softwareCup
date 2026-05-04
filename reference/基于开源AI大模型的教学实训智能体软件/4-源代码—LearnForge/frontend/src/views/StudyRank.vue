<template>
  <v-container>
    <v-card variant="flat">
      <v-card-title class="d-flex align-center pe-2">
        <v-icon icon="mdi-video-input-component"></v-icon> &nbsp; 排行榜

        <v-spacer></v-spacer>

        <v-text-field v-model="search" density="compact" label="搜索" prepend-inner-icon="mdi-magnify"
          variant="solo-filled" flat hide-details single-line></v-text-field>
      </v-card-title>

      <v-divider></v-divider>
      <v-card-text>
        <v-data-table :headers="headers" :items="filteredLeaderboard" :items-per-page="100" class="elevation-1" 
          item-value="name" no-data-text="。。。">
          <template v-slot:item.rank="{ item, index }">
            <p class="d-flex justify-center align-center" :class=" item.idx < 4 ? 'big-chip' : ''">
    {{ item.idx === 1 ? '🥇' : item.idx === 2 ? '🥈' : item.idx === 3 ? '🥉' : item.idx }}
          </p>

          </template>
          <template v-slot:item.request_times="{ item }">
            <v-chip color="green">{{ item.request_times }}</v-chip>
          </template>
          <template v-slot:item.space="{ item }">
            <v-btn class="me-2" color="" prepend-icon="mdi-archive-minus-outline" size="small" variant="outlined"
              @click="goToHomePage(item.user_id)">
              访问
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import axios from '@/utils/axiosConfig';

export default {
  data() {
    return {
      search: '',
      leaderboard: [],
      headers: [
        { title: '', value: 'rank', sortable: false },
        { title: '姓名', value: 'name', sortable: true },
        { title: '班级', value: 'major', sortable: true },
        { title: '个性签名', value: 'description', sortable: false },
        { title: '逗币', value: 'request_times', sortable: true },
        { title: '空间', value: 'space', sortable: false }
      ]
    };
  },
  mounted() {
    this.fetchLeaderboard();
  },
  computed: {
    filteredLeaderboard() {
      return this.leaderboard.filter(student => {
        return (
          student.name.toLowerCase().includes(this.search.toLowerCase()) ||
          student.major.toLowerCase().includes(this.search.toLowerCase()) ||
          student.description.toLowerCase().includes(this.search.toLowerCase())
        );
      });
    }
  },
  methods: {
    fetchLeaderboard() {
      axios
        .get(`${this.$backendUrl}/api/getRank`)
        .then((response) => {
          this.leaderboard = response.data;
        })
        .catch((error) => {
          console.error('Error fetching leaderboard:', error);
        });
    },
    goToHomePage(studentId) {
      this.$router.push({ name: 'User', params: { user_id: studentId } });
    },
  },
};
</script>

<style scoped>
.big-chip {
  font-size: 30px; /* 调整为你需要的大小 */
  height: 48px;    /* 调整高度，使其与内容大小匹配 */
  padding: 0 12px; /* 调整内边距，使内容不至于过于紧凑 */
}
</style>
