<template>
    <v-container>
        <v-form>
            <v-text-field label="学号" v-model="sno" prepend-icon="mdi-account" :rules="snoRules" required></v-text-field>
            <v-text-field label="姓名" v-model="name" prepend-icon="mdi-account-box" :rules="nameRules" required></v-text-field>
            <v-radio-group v-model="gender" :rules="genderRules" row>
                <v-radio label="男" value="男"></v-radio>
                <v-radio label="女" value="女"></v-radio>
            </v-radio-group>
            <v-text-field label="密码" v-model="password" :type="showPassword ? 'text' : 'password'"
                prepend-icon="mdi-lock" :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append="showPassword = !showPassword" :rules="passwordRules" required></v-text-field>
            <v-text-field label="重复密码" v-model="confirmPassword" :type="showConfirmPassword ? 'text' : 'password'"
                prepend-icon="mdi-lock-check" :append-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append="showConfirmPassword = !showConfirmPassword" :rules="confirmPasswordRules" required></v-text-field>
            <v-select label="班级" v-model="class_id" :items="classes" item-title="ClassName" item-value="ClassID" :rules="classRules" required></v-select>
            <v-btn :disabled="!isValid" color="success" class="mr-4" @click="submit">注册</v-btn>
        </v-form>
        <v-snackbar v-model="snackbar.show" :color="snackbar.color" bottom right>
            {{ snackbar.text }}
        </v-snackbar>
    </v-container>
</template>

<script>
import axios from '@/utils/axiosConfig';
export default {
    data: () => ({
        sno: '',
        name: '',
        gender: '',
        password: '',
        confirmPassword: '',
        class_id: null,
        major: "",
        showPassword: false,
        showConfirmPassword: false,
        classes: [],
        snoRules: [
            v => !!v || '学号是必填项',
            v => (v && v.length ==10) || '学号为10个字符',
        ],
        nameRules: [
            v => !!v || '姓名是必填项',
        ],
        genderRules: [
            v => !!v || '性别是必填项',
        ],
        passwordRules: [
            v => !!v || '密码是必填项',
            v => (v && v.length >= 5) || '密码至少需要5个字符',
        ],
        confirmPasswordRules: [
            v => !!v || '必须确认密码',
            v => v === this.password || '两次密码输入必须相同',
        ],
        classRules: [
            v => !!v || '班级是必填项',
        ],
        snackbar: {
            show: false,
            text: '',
            color: 'success'
        }
    }),
    computed: {
        isValid() {
            return (
                this.sno &&
                this.name &&
                this.gender &&
                this.password &&
                this.password === this.confirmPassword &&
                this.password.length >= 5 &&
                // this.sno <= 10 &&
                this.class_id
            );
        }
    },
    created() {
        this.fetchClasses();
    },
    methods: {
        fetchClasses() {
            axios.get(`${this.$backendUrl}/api/getClasses`)
                .then(response => {
                    this.classes = response.data;
                })
                .catch(error => {
                    console.log(error);
                });
        },
        submit() {
            if (this.isValid) {
                const selectedClass = this.classes.find(c => c.ClassID === this.class_id);
                const major = selectedClass ? selectedClass.ClassName : '';
                const userData = {
                    sno: this.sno,
                    name: this.name,
                    gender: this.gender,
                    password: this.password,
                    class_id: this.class_id,
                    major: major
                };

                axios.post(`${this.$backendUrl}/api/registerStudent`, userData)
                    .then(response => {
                        if (response.data.message === '学生注册成功') {
                            this.snackbar.show = true;
                            this.snackbar.text = '注册成功！前往登录';
                            this.snackbar.color = 'success';

                            setTimeout(() => {
                                this.$router.push({ name: 'Login' });
                            }, 500);
                        } else {
                            this.snackbar.show = true;
                            this.snackbar.text = response.data.message;
                            this.snackbar.color = 'error';
                        }
                    })
                    .catch(error => {
                        this.snackbar.show = true;
                        this.snackbar.text = '注册失败：' + (error.response && error.response.data.error ? error.response.data.error : '未知错误');
                        this.snackbar.color = 'error';
                    });
            } else {
                this.snackbar.show = true;
                this.snackbar.text = '请检查输入信息是否正确。';
                this.snackbar.color = 'warning';
            }
        }
    }
};
</script>
