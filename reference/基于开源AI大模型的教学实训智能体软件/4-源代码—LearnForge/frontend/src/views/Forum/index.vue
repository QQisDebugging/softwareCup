<template>
    <v-app>
      <v-main>
        <v-container fluid>
          <v-row>
            <v-col cols="8">
              <v-card>
                <v-card-title>
                  <span class="headline">论坛</span>
                </v-card-title>
                <v-card-text>
                  <v-list dense>
                    <v-list-item v-for="(post, index) in posts" :key="index">
                      <v-list-item-content>
                        <v-list-item-title>{{ post.title }}</v-list-item-title>
                        <v-list-item-subtitle>{{ post.author }} - {{ post.date }}</v-list-item-subtitle>
                      </v-list-item-content>
                      <v-list-item-action>
                        <v-btn icon small @click="viewPost(post)">
                          <v-icon small>mdi-eye</v-icon>
                        </v-btn>
                        <v-btn icon small @click="editPost(post)">
                          <v-icon small>mdi-pencil</v-icon>
                        </v-btn>
                        <v-btn icon small @click="deletePost(post)">
                          <v-icon small>mdi-delete</v-icon>
                        </v-btn>
                      </v-list-item-action>
                    </v-list-item>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn flat color="primary" @click="showCreatePost = true">发布新帖</v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
            <v-col cols="4">
              <v-card>
                <v-card-title>
                  <span class="headline">活跃用户</span>
                </v-card-title>
                <v-card-text>
                  <v-list dense>
                    <v-list-item v-for="(user, index) in activeUsers" :key="index">
                      <v-list-item-content>
                        <v-list-item-title>{{ user.name }}</v-list-item-title>
                        <v-list-item-subtitle>{{ user.lastSeen }}</v-list-item-subtitle>
                      </v-list-item-content>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
  
          <v-dialog v-model="showCreatePost" max-width="500px">
            <v-card>
              <v-card-title>
                <span class="headline">发布新帖</span>
              </v-card-title>
              <v-card-text>
                <v-text-field label="标题" v-model="newPost.title"></v-text-field>
                <v-textarea label="内容" v-model="newPost.content"></v-textarea>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn flat color="blue darken-1" text @click="showCreatePost = false">
                  取消
                </v-btn>
                <v-btn flat color="blue darken-1" text @click="createPost">
                  发布
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </v-container>
      </v-main>
    </v-app>
  </template>
  
  <script>
  export default {
    data() {
      return {
        posts: [
          {
            title: '如何使用Vue.js构建复杂应用？',
            author: '张三',
            date: '2023-09-01',
            content: '这是一个关于Vue.js的帖子...'
          },
          {
            title: 'React与Vue的性能对比',
            author: '李四',
            date: '2023-08-25',
            content: '这是一个关于React与Vue的性能对比的帖子...'
          }
        ],
        activeUsers: [
          {
            name: '王五',
            lastSeen: '在线'
          },
          {
            name: '赵六',
            lastSeen: '在线'
          }
        ],
        newPost: {
          title: '',
          content: ''
        },
        showCreatePost: false
      };
    },
    methods: {
      createPost() {
        this.posts.push({
          title: this.newPost.title,
          author: '匿名用户',
          date: new Date().toISOString().split('T')[0],
          content: this.newPost.content
        });
        this.newPost.title = '';
        this.newPost.content = '';
        this.showCreatePost = false;
      },
      viewPost(post) {
        console.log(`Viewing post: ${post.title}`);
      },
      editPost(post) {
        console.log(`Editing post: ${post.title}`);
      },
      deletePost(post) {
        console.log(`Deleting post: ${post.title}`);
      }
    }
  };
  </script>