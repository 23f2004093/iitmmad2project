export default {
    name: 'AllLogin',
    data() {
        return {
            email: '',
            password: '',
            errorMessage: ''
        };
    },
    template: `
        <div class="row justify-content-center align-items-center mt-5">
            <div class="col-md-5 col-lg-4">
                <div class="card border-0 shadow-lg rounded-4 p-4">
                    <div class="text-center mb-4">
                        <h2 class="fw-bold text-primary">Placement Portal</h2>
                        <p class="text-muted">Sign in to your account</p>
                    </div>
                    
                    <div v-if="errorMessage" class="alert alert-danger py-2 text-center" role="alert">
                        {{ errorMessage }}
                    </div>

                    <form @submit.prevent="handleLogin">
                        <div class="form-floating mb-3">
                            <input v-model="email" type="email" class="form-control" id="floatingInput" placeholder="name@example.com" required>
                            <label for="floatingInput">Email address</label>
                        </div>
                        <div class="form-floating mb-4">
                            <input v-model="password" type="password" class="form-control" id="floatingPassword" placeholder="Password" required>
                            <label for="floatingPassword">Password</label>
                        </div>
                        <button type="submit" class="btn btn-primary w-100 py-3 rounded-3 fw-bold">Sign In</button>
                    </form>

                    <div class="text-center mt-4">
                        <p class="mb-1 text-muted">Don't have an account?</p>
                        <router-link to="/register/student" class="text-decoration-none me-3">Register as Student</router-link>
                        <router-link to="/register/company" class="text-decoration-none">Register as Company</router-link>
                    </div>
                </div>
            </div>
        </div>
    `,
    methods: {
               async handleLogin() {
            this.errorMessage = '';
            
            try {
                // 1. Send login credentials to the Flask route
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        email: this.email,
                        password: this.password
                    })
                });

                // 2. Parse the JSON response
                const data = await response.json();

                if (response.ok) {
                    // 3. Redirect the browser to the correct dashboard based on user role
                    if (data.role === 'admin') {
                        this.$router.push('/dashboard/admin');
                    } else if (data.role === 'student') {
                        this.$router.push('/dashboard/student');
                    } else if (data.role === 'recruiter') {
                        this.$router.push('/dashboard/company');
                    }
                } else {
                    // Display error message from backend
                    this.errorMessage = data.message || "Login failed";
                }
            } catch (error) {
                console.error("Login fetch error:", error);
                this.errorMessage = "Server connection failed. Is the Flask server running?";
            }
        }
    }
};
