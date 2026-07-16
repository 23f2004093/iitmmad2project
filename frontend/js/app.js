// Main Application Entrypoint using Native ES Modules

import NavbarComponent from './components/Navbar.js';
import AllLogin from './components/AllLogin.js';
import StudentRegistration from './components/StudentRegistration.js';
import CompanyRegistration from './components/CompanyRegistration.js';
import StudentDashboard from './components/StudentDashboard.js';
import CompanyDashboard from './components/CompanyDashboard.js';
import AdminDashboard from './components/AdminDashboard.js';

// 1. Define Routes
const routes = [
    { path: '/', component: AllLogin },
    { path: '/register/student', component: StudentRegistration },
    { path: '/register/company', component: CompanyRegistration },
    { path: '/dashboard/student', component: StudentDashboard },
    { path: '/dashboard/company', component: CompanyDashboard },
    { path: '/dashboard/admin', component: AdminDashboard }
];

// 2. Create Router Instance
const router = VueRouter.createRouter({
    history: VueRouter.createWebHashHistory(),
    routes
});

// 3. Create Vue App Instance
const app = Vue.createApp({
    components: {
        NavbarComponent
    }
});

// 4. Attach Router and Mount
app.use(router);
app.mount('#app');
