

import NavbarComponent from './components/Navbar.js';
import AllLogin from './components/AllLogin.js';
import StudentRegistration from './components/StudentRegistration.js';
import CompanyRegistration from './components/CompanyRegistration.js';
import StudentDashboard from './components/StudentDashboard.js';
import CompanyDashboard from './components/CompanyDashboard.js';
import AdminDashboard from './components/AdminDashboard.js';


const routes = [
    { path: '/', component: AllLogin },
    { path: '/register/student', component: StudentRegistration },
    { path: '/register/company', component: CompanyRegistration },
    { path: '/dashboard/student', component: StudentDashboard },
    { path: '/dashboard/company', component: CompanyDashboard },
    { path: '/dashboard/admin', component: AdminDashboard }
];


const router = VueRouter.createRouter({
    history: VueRouter.createWebHashHistory(),
    routes
});


const app = Vue.createApp({
    components: {
        NavbarComponent
    }
});


app.use(router);
app.mount('#app');
