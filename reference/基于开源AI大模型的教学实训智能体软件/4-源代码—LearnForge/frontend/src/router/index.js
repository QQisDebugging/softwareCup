
import { createRouter, createWebHashHistory, createWebHistory } from 'vue-router';
import debounce from 'lodash/debounce';

const routes = [
  { path: '/', redirect: '/aboutUs' },
  {
    path: '/login',
    name: 'Login',  
    component: () => import('@/views/Login.vue'),
    meta: { }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: {  }
  },
  {
    path: '/forum/index',
    name: 'Forum',
    component: () => import('@/views/Forum/index.vue'),
    meta: {requiresAuth: true }
  },
  {
    path: '/studentArea',
    name: 'StudentArea',
    component: () => import('@/views/StudentArea.vue'),
    meta: {requiresAuth: true }
  },
  {
    path: '/aboutUs',
    name: 'Profile',
    component: () => import('@/views/About.vue'),
    meta: { keepAlive: false }
  },
  {
    path: '/codeAnalysis',
    name: 'CodeAnalysis',
    component: () => import('@/views/CodeAnalysis.vue'),
    meta: {requiresAuth: true }
  },
  {
    path: '/codeCorrect',
    name: 'CodeCorrect',
    component: () => import('@/views/CodeCorrect.vue'),
    meta: {requiresAuth: true }
  },
  {
    path: '/sqlGenerate',
    name: 'SqlGenerate',
    component: () => import('@/views/SqlGenerate.vue'),
    meta: {requiresAuth: true }
  },
  {
    path: '/courseOutlineGenerator',
    name: 'CourseOutlineGenerator',
    component: () => import('@/views/CourseOutlineGenerator.vue'),
    meta: {requiresAuth: true }
  },
  {
    path: '/teacherArea',
    name: 'TeacherArea',
    component: () => import('@/views/TeacherArea.vue'),
    meta: {requiresAuth: true }
  },
  {
    path: '/englishExamDesign',
    name: 'EnglishExamDesign',
    component: () => import('@/views/EnglishExamDesign.vue'),
    meta: {requiresAuth: true }
  },
  {
    path: '/chatAust',
    name: 'ChatAust',
    component: () => import('@/views/ChatAust.vue'),
    meta: {requiresAuth: true }
  },
  {
    path: '/codeExamDesign',
    name: 'CodeExamDesign',
    component: () => import('@/views/CodeExamDesign.vue'),
    meta: {requiresAuth: true }
  },
  {
    path: '/codeBasicSkill',
    name: 'CodeBasicSkill',
    component: () => import('@/views/CodeBasicSkill.vue'),
    meta: {requiresAuth: false }
  },
  {
    path: '/dailyTest',
    name: 'DailyTest',
    component: () => import('@/views/DailyTest/dailyTest.vue'),
    meta: {requiresAuth: false }
  },
  {
    path: '/studyRank',
    name: 'StudyRank',
    component: () => import('@/views/StudyRank.vue'),
    meta: {requiresAuth: false }
  },
  {
    path: '/dailyTestDone',
    name: 'done',
    component: () => import('@/views/DailyTest/done.vue'),
    props: true,
    meta: {requiresAuth: false }
  },
  {
    path: '/docAnalysis',
    name: 'DocAnalysis',
    component: () => import('@/views/DocAnalysis.vue'),
    props: true,
    meta: {requiresAuth: false }
  },
  {
    path: '/pptGenerater',
    name: 'PPTGenerater',
    component: () => import('@/views/PPTGenerater.vue'),
    props: true,
    meta: {requiresAuth: false }
  },
  {
    path: '/imageProblemSolve',
    name: 'ImageProblemSolve',
    component: () => import('@/views/ImageProblemSolve.vue'),
    props: true,
    meta: {requiresAuth: false }
  },
  {
    path: '/codeHelper',
    name: 'CodeHelper',
    component: () => import('@/views/CodeHelper.vue'),
    props: true,
    meta: {requiresAuth: false }
  },
  {
    path: '/flowChartGenerate',
    name: 'FlowChartGenerate',
    component: () => import('@/views/FlowChartGenerate.vue'),
    props: true,
    meta: {requiresAuth: false }
  },
  {
    path: '/studentAccount',
    name: 'StudentAccount',
    component: () => import('@/views/Dashboard/StudentAccount.vue'),
    props: true,
    meta: {requiresAuth: true },
  },
  {
    path: '/getStudetWork',
    name: 'GetStudetWork',
    component: () => import('@/views/Dashboard/views/GetStudetWork.vue'),
    props: true,
    meta: {requiresAuth: true},
  },
  {
    path: '/getStudetActivity',
    name: 'GetStudetActivity',
    component: () => import('@/views/Dashboard/views/GetStudetActivity.vue'),
    props: true,
    meta: {requiresAuth: true},
  },
  {
    path: '/getStudetContest',
    name: 'GetStudetContest',
    component: () => import('@/views/Dashboard/views/GetStudetContest.vue'),
    props: true,
    meta: {requiresAuth: true},
  },
  {
    path: '/contestDetail/:contest_id',
    name: 'StudentContestDetail',
    component: () => import('@/views/Dashboard/views/ContestDetail.vue'),
    props: true,
    meta: {requiresAuth: false},
  },
  {
    path: '/workDetail/:assignment_id',
    name: 'StudentWorkDetail',
    component: () => import('@/views/Dashboard/views/WorkDetail.vue'),
    props: true,
    meta: {requiresAuth: false},
  },
  {
    path: '/test',
    name: 'test',
    component: () => import('@/views/test.vue'),
    props: true,
    meta: {requiresAuth: false},
  },
  {
    path: '/user/:user_id',
    name: 'User',
    component: () => import('@/views/UserPage/user.vue'),
    props: true,
    meta: {requiresAuth: false},
  },
  
  {
    path: '/activityDetail/:activity_id',
    name: 'StudentActivityDetail',
    component: () => import('@/views/Dashboard/views/ActivityDetail.vue'),
    props: true,
    meta: {requiresAuth: false},
  },
   {
        path: '/submitAssignment/:activity_id',
        name: 'SubmitAssignment',
        component: () => import('@/views/Dashboard/views/SubmitAssignment.vue'),
        props: true,
        meta: {requiresAuth: false},
      },
      {
        path: '/submitContest/:contest_id',
        name: 'SubmitContest',
        component: () => import('@/views/Dashboard/views/SubmitContest.vue'),
        props: true,
        meta: {requiresAuth: false},
      },
      {
        path: '/submitWork/:assignment_id',
        name: 'SubmitWork',
        component: () => import('@/views/Dashboard/views/SubmitWork.vue'),
        props: true,
        meta: {requiresAuth: false},
      },
  
  {
    path: '/dashboardTea',
    name: 'DashboardTea',
    component: () => import('@/views/Dashboard/DashboardTea.vue'),
    props: true,
    meta: {requiresAuth: true,hideDrawer: true },
    redirect: { name: 'DataAnalysis' }, 
    children:[
      {
        path: 'dataAnalysis',
        name: 'DataAnalysis',
        component: () => import('@/views/Dashboard/views/DataAnalysis.vue'),
        props: true,
        meta: {requiresAuth: false},
      },
     
      {
        path: 'studentList',
        name: 'StudentList',
        component: () => import('@/views/Dashboard/views/StudentList.vue'),
        props: true,
        meta: {requiresAuth: false},
      },
      {
        path: 'createWork',
        name: 'CreateWork',
        component: () => import('@/views/Dashboard/views/CreateWork.vue'),
        props: true,
        meta: {requiresAuth: false},
      },
      {
        path: 'getTeacherWork',
        name: 'GetTeacherWork',
        component: () => import('@/views/Dashboard/views/GetTeacherWork.vue'),
        props: true,
        meta: {requiresAuth: false},
      },
      {
        path: 'createActivity',
        name: 'CreateActivity',
        component: () => import('@/views/Dashboard/views/CreateActivity.vue'),
        props: true,
        meta: {requiresAuth: false},
      },
      {
        path: 'getTeacherContest',
        name: 'GetTeacherContest',
        component: () => import('@/views/Dashboard/views/GetTeacherContest.vue'),
        props: true,
        meta: {requiresAuth: false},
      },
      {
        path: 'createContest',
        name: 'CreateContest',
        component: () => import('@/views/Dashboard/views/CreateContest.vue'),
        props: true,
        meta: {requiresAuth: false},
      },
      {
        path: 'getTeacherActivity',
        name: 'GetTeacherActivity',
        component: () => import('@/views/Dashboard/views/GetTeacherActivity.vue'),
        props: true,
        meta: {requiresAuth: false},
      },
    

      {
        path: '/activityDetail/:activity_id',
        name: 'ActivityDetail',
        component: () => import('@/views/Dashboard/views/ActivityDetail.vue'),
        props: true,
        meta: {requiresAuth: false},
      },
      {
        path: '/contestDetail/:contest_id',
        name: 'ContestDetail',
        component: () => import('@/views/Dashboard/views/ContestDetail.vue'),
        props: true,
        meta: {requiresAuth: false},
      },
      {
        path: '/workDetail/:assignment_id',
        name: 'WorkDetail',
        component: () => import('@/views/Dashboard/views/WorkDetail.vue'),
        props: true,
        meta: {requiresAuth: false},
      },
     
      
    ]
  }

];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});


if (import.meta.env.MODE === `development`) {
  const componentsToLoad = routes.map(item => item.component)
  const loadComponentsWhenNetworkIdle = debounce(
    () => {
      if (componentsToLoad.length > 0) {
        const componentLoader = componentsToLoad.pop()
        componentLoader && componentLoader()
        // eslint-disable-next-line
        // console.log(`剩余${componentsToLoad.length}个路由未加载`, componentsToLoad)
      }
    },
    1000,
    false
  )

  const observer = new PerformanceObserver((list) => {
    const entries = list.getEntries()
    for (const entry of entries) {
      if (entry.entryType === `resource`) {
        loadComponentsWhenNetworkIdle()
      }
    }
  })
  observer.observe({ entryTypes: [`resource`] })
}

router.beforeEach((to, from, next) => {
  // 使用 to.matched.some() 来检查嵌套路由
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const isAuthenticated = localStorage.getItem('token'); // 检查本地存储中是否有token

  if (requiresAuth && !isAuthenticated) {
    // 如果需要认证且用户未登录，重定向到登录页
    console.log("Redirecting to login because not authenticated");
    next({ name: 'Login' }); // 确保使用正确的路由名
  } else {
    // 否则正常导航到路由
    next(); 
  }
});

// router.afterEach((to, from, next) => {
//   if (to.path === "/") {
//     // 如果路由为"/"，则启动切换页面
//     router.push("/aiChat");
//   }
// });


export default router;
