<template>
  <v-container class="fill-height">
    <v-responsive class="align-centerfill-height mx-auto">
      <div class="text-center">
        <h1 class="text-h5 font-weight-bold">教师工具</h1>
      </div>

      <div class="py-4" />

      <v-row>
        <v-col cols="12" sm="6" md="6" class="mb-4">
          <v-card class="custom-card" prepend-icon="mdi-widgets-outline" @click="navigateToCourseOutlineGenerator">
            <div class="card-img">
              <img src="@/assets/1.jpg" alt="课程大纲生成" />
            </div>
            <div class="card-content">课程大纲生成</div>
            <v-overlay opacity=".06" scrim="primary" contained model-value persistent />
          </v-card>
        </v-col>



        <v-col cols="12" sm="6" md="6" class="mb-4">
          <v-card class="custom-card" prepend-icon="mdi-magnify-scan" @click="navigateToDocAnalysis">
            <div class="card-img">
              <img src="@/assets/2.png" alt="文档解析" />
            </div>
            <div class="card-content">文档解析</div>
            <v-overlay opacity=".06" scrim="primary" contained model-value persistent />
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" sm="6" md="6" class="mb-4">
          <v-card class="custom-card" prepend-icon="mdi-magnify-scan" @click="navigateToImageProblemSolve">
            <div class="card-img">
              <img src="@/assets/4.jpg" alt="拍照答题" />
            </div>
            <div class="card-content">拍照答题</div>
            <v-overlay opacity=".06" scrim="primary" contained model-value persistent />
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="6" class="mb-4">
          <v-card class="custom-card" prepend-icon="mdi-microsoft-powerpoint" variant="text"
            @click="navigateToPPTGenerater">
            <div class="card-img">
              <img src="@/assets/3.jpg" alt="PPT生成" />
            </div>
            <div class="card-content">PPT生成</div>
            <v-overlay opacity=".06" scrim="primary" contained model-value persistent />
          </v-card>
        </v-col>

        <!-- <v-col cols="6">
            <v-card append-icon="mdi-open-in-new" class="py-4" color="surface-variant" prepend-icon="mdi-text-box-outline"
              rel="noopener noreferrer" rounded="lg" subtitle="" target="_blank" title="代码解析" variant="text"
              @click="navigateToCodeAnalysis">
              <v-overlay opacity=".06" scrim="primary" contained model-value persistent />
            </v-card>
          </v-col>
          <v-col cols="6">
            <v-card append-icon="mdi-open-in-new" class="py-4" color="surface-variant" prepend-icon="mdi-text-box-outline"
              rel="noopener noreferrer" rounded="lg" subtitle="" target="_blank" title="SQL语句生成" variant="text"
              @click="navigateToSqlGenerate">
              <v-overlay opacity=".06" scrim="primary" contained model-value persistent />
            </v-card>
          </v-col>
  
          <v-col cols="6">
            <v-card append-icon="mdi-open-in-new" class="py-4" color="surface-variant" prepend-icon="mdi-widgets-outline"
              rel="noopener noreferrer" rounded="lg" subtitle="" target="_blank" title="问题答疑" variant="text">
              <v-overlay opacity=".06" scrim="primary" contained model-value persistent />
            </v-card>
          </v-col> -->
      </v-row>
    </v-responsive>
  </v-container>
</template>


<script>
export default {
  methods: {
    navigateToEnglishExamDesign() {
      this.$router.push({ name: "EnglishExamDesign" });
    },
    navigateToCourseOutlineGenerator() {
      this.$router.push({ name: "CourseOutlineGenerator" });
    },
    navigateToCodeExamDesign() {
      this.$router.push({ name: "CodeExamDesign" });
    },
    navigateToDocAnalysis() {
      this.$router.push({ name: "DocAnalysis" });
    },
    navigateToPPTGenerater() {
      this.$router.push({ name: "PPTGenerater" });
    },
    navigateToImageProblemSolve() {
      this.$router.push({ name: "ImageProblemSolve" });
    },
  },

  data: () => ({}),
};
</script>

<style scoped>
.fill-height {
  height: 100vh;
}

.custom-card {
  cursor: pointer;
  border-radius: 15px;
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s, background-color 0.3s;
  box-shadow: none;
}

.custom-card .card-img {
  background-color: #f6f6f7;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.custom-card .card-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.custom-card .card-content {
  /* background-color: #e7ecf6; */
  padding: 16px;
  text-align: center;
  font-size: 16px;
  font-weight: bold;
}

.custom-card:hover {
  transform: translateY(-5px);
}
</style>