export default {
    name: 'CompanyRegistration',
    data() {
        return {
            email: '',
            password: '',
            companyName: '',
            hrContact: '',
            website: '',
            description: '',
            errorMessage: ''
        };
    },
    template: `
        <div class="row justify-content-center mt-4">
            <div class="col-md-6 col-lg-5">
                <div class="card border-0 shadow rounded-4 p-4">
                    <h3 class="fw-bold text-info text-center mb-4 text-white p-2 bg-info rounded-3">Company Registration</h3>
                    
                    <div v-if="errorMessage" class="alert alert-danger py-2 text-center" role="alert">
                        {{ errorMessage }}
                    </div>

                    <form @submit.prevent="handleRegister">
                        <div class="mb-3">
                            <label class="form-label fw-semibold">Company Name</label>
                            <input v-model="companyName" type="text" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-semibold">Corporate Email</label>
                            <input v-model="email" type="email" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-semibold">Password</label>
                            <input v-model="password" type="password" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-semibold">HR Contact Number</label>
                            <input v-model="hrContact" type="text" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-semibold">Company Website</label>
                            <input v-model="website" type="url" class="form-control" placeholder="https://example.com" required>
                        </div>
                        <div class="mb-4">
                            <label class="form-label fw-semibold">About Company</label>
                            <textarea v-model="description" class="form-control" rows="3" required></textarea>
                        </div>
                        
                        <button type="submit" class="btn btn-info w-100 py-2.5 rounded-3 fw-bold text-white">Submit Request</button>
                    </form>

                    <div class="text-center mt-3">
                        <router-link to="/" class="text-decoration-none">Back to Login</router-link>
                    </div>
                </div>
            </div>
        </div>
    `,
    methods: {
        async handleRegister() {
            this.errorMessage = '';
            try {
                const payload = {
                    user_data: {
                        email: this.email,
                        password: this.password
                    },
                    profile_data: {
                        companyName: this.companyName,
                        hrContact: this.hrContact,
                        website: this.website,
                        description: this.description
                    }
                };
                const response = await fetch('/api/auth/register/company', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (response.ok) {
                    alert("Registration successful! Please sign in.");
                    this.$router.push('/');
                } else {
                    this.errorMessage = data.message || "Registration failed";
                }
            } catch (error) {
                this.errorMessage = "Server connection failed. Is the backend running?";
            }
        }
    }
}
