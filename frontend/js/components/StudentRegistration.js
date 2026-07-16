export default {
    name: 'StudentRegistration',
    data() {
        return {
            email: '',
            password: '',
            rollNumber: '',
            name: '',
            department: '',
            cgpa: '',
            errorMessage: ''
        };
    },
    template: `
        <div class="row justify-content-center mt-4">
            <div class="col-md-6 col-lg-5">
                <div class="card border-0 shadow rounded-4 p-4">
                    <h3 class="fw-bold text-success text-center mb-4">Student Signup</h3>
                    
                    <div v-if="errorMessage" class="alert alert-danger py-2 text-center" role="alert">
                        {{ errorMessage }}
                    </div>

                    <form @submit.prevent="handleRegister">
                        <div class="mb-3">
                            <label class="form-label fw-semibold">Full Name</label>
                            <input v-model="name" type="text" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-semibold">Email address</label>
                            <input v-model="email" type="email" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-semibold">Password</label>
                            <input v-model="password" type="password" class="form-control" required>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-semibold">Roll Number</label>
                                <input v-model="rollNumber" type="text" class="form-control" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-semibold">CGPA</label>
                                <input v-model="cgpa" type="number" step="0.01" min="0" max="10" class="form-control" placeholder="e.g. 8.5" required>
                            </div>
                        </div>
                        <div class="mb-4">
                            <label class="form-label fw-semibold">Department / Branch</label>
                            <select v-model="department" class="form-select" required>
                                <option value="" disabled>Select Branch</option>
                                <option value="Computer Science">Computer Science</option>
                                <option value="Electrical Engineering">Electrical Engineering</option>
                                <option value="Mechanical Engineering">Mechanical Engineering</option>
                                <option value="Aerospace Engineering">Aerospace Engineering</option>
                            </select>
                        </div>
                        
                        <button type="submit" class="btn btn-success w-100 py-2.5 rounded-3 fw-bold">Sign Up</button>
                    </form>

                    <div class="text-center mt-3">
                        <router-link to="/" class="text-decoration-none">Already have an account? Sign In</router-link>
                    </div>
                </div>
            </div>
        </div>
    `,
    methods: {
        async handleRegister() {
            this.errorMessage = '';
            console.log("Handle student registration called:", this.name);
            
            // TODO: Implement the fetch API call to '/api/auth/register/student' (POST) here.
            // On success: redirect back to login page: this.$router.push('/')
            // On error: set this.errorMessage = data.message
        }
    }
};
