export default {
    name: 'CompanyDashboard',
    data() {
        return {
            company: {
                company_name: 'Company Name'
            },
            drives: [],
            selectedJobId: null,
            applicants: [],
            newDrive: {
                title: '',
                description: '',
                job_type: 'full-time',
                package_ctc: '',
                deadline: '',
                min_cgpa: ''
            }
        };
    },
    template: `
        <div>
            <h2 class="fw-bold mb-4">Recruiter Center: {{ company.company_name }}</h2>
            
            <div class="row">
                <!-- Create Drive -->
                <div class="col-lg-5 mb-4">
                    <div class="card border-0 shadow-sm p-4 rounded-4">
                        <h5 class="fw-bold mb-3">Create Placement Drive</h5>
                        <form @submit.prevent="createDrive">
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Job Title</label>
                                <input v-model="newDrive.title" type="text" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label fw-semibold">Job Description</label>
                                <textarea v-model="newDrive.description" class="form-control" rows="3" required></textarea>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Package (CTC)</label>
                                    <input v-model="newDrive.package_ctc" type="text" class="form-control" placeholder="e.g. 12 LPA" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Minimum CGPA</label>
                                    <input v-model="newDrive.min_cgpa" type="number" step="0.01" min="0" max="10" class="form-control" required>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-semibold">Job Type</label>
                                    <select v-model="newDrive.job_type" class="form-select">
                                        <option value="full-time">Full-Time</option>
                                        <option value="internship">Internship</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-4">
                                    <label class="form-label fw-semibold">Deadline Date</label>
                                    <input v-model="newDrive.deadline" type="date" class="form-control" required>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-primary w-100 py-2 fw-bold">Post Placement Drive</button>
                        </form>
                    </div>
                </div>

                <!-- Manage Drives & Applicants -->
                <div class="col-lg-7">
                    <div class="card border-0 shadow-sm p-4 rounded-4 mb-4">
                        <h5 class="fw-bold mb-3">Active Drives</h5>
                        <div class="table-responsive">
                            <table class="table align-middle">
                                <thead>
                                    <tr>
                                        <th>Title</th>
                                        <th>Deadline</th>
                                        <th>Min CGPA</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="drive in drives" :key="drive.id">
                                        <td class="fw-bold">{{ drive.title }}</td>
                                        <td>{{ drive.deadline }}</td>
                                        <td>{{ drive.min_cgpa }}</td>
                                        <td>
                                            <button @click="viewApplicants(drive.id)" class="btn btn-sm btn-outline-info me-2">Applicants</button>
                                            <button @click="zipResumes(drive.id)" class="btn btn-sm btn-outline-secondary">Zip Resumes</button>
                                        </td>
                                    </tr>
                                    <tr v-if="drives.length === 0">
                                        <td colspan="4" class="text-center text-muted py-3">No active placement drives found.</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Applicants Panel -->
                    <div v-if="selectedJobId" class="card border-0 shadow-sm p-4 rounded-4">
                        <h5 class="fw-bold mb-3">Applicants for Selected Drive</h5>
                        <div class="table-responsive">
                            <table class="table align-middle">
                                <thead>
                                    <tr>
                                        <th>Student Name</th>
                                        <th>CGPA</th>
                                        <th>Resume</th>
                                        <th>Status</th>
                                        <th>Update Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="app in applicants" :key="app.id">
                                        <td>{{ app.student.name }}</td>
                                        <td>{{ app.student.cgpa }}</td>
                                        <td>
                                            <a :href="'/' + app.student.resume_path" target="_blank" class="btn btn-sm btn-link text-decoration-none">PDF</a>
                                        </td>
                                        <td>
                                            <span :class="getStatusBadge(app.status)">{{ app.status.toUpperCase() }}</span>
                                        </td>
                                        <td>
                                            <select @change="updateStatus(app.id, $event.target.value)" class="form-select form-select-sm">
                                                <option disabled selected>Choose</option>
                                                <option value="shortlisted">Shortlist</option>
                                                <option value="selected">Select</option>
                                                <option value="rejected">Reject</option>
                                            </select>
                                        </td>
                                    </tr>
                                    <tr v-if="applicants.length === 0">
                                        <td colspan="5" class="text-center text-muted py-3">No students have applied to this drive yet.</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
    created() {
        this.fetchCompanyData();
    },
    methods: {
        async fetchCompanyData() {
            console.log("Fetching company data...");
            // TODO: Fetch recruiter profile (GET '/api/auth/me') and jobs list (GET '/api/companies/jobs')
            // Populating variables:
            //   - this.company
            //   - this.drives
        },
        async createDrive() {
            console.log("Submitting job creation request:", this.newDrive.title);
            
            // TODO: Send POST fetch request to '/api/companies/jobs' with this.newDrive payload
            // On success: call this.fetchCompanyData()
        },
        async viewApplicants(jobId) {
            this.selectedJobId = jobId;
            console.log("Viewing applicants for job:", jobId);
            
            // TODO: Send GET fetch request to `/api/companies/applications/${jobId}`
            // Populate this.applicants
        },
        async updateStatus(appId, newStatus) {
            console.log("Updating application status:", appId, "to", newStatus);
            
            // TODO: Send POST fetch request to `/api/companies/applications/${appId}/status?status=${newStatus}`
            // On success: call this.viewApplicants(this.selectedJobId)
        },
        async zipResumes(jobId) {
            console.log("Triggering resume zipping task for job:", jobId);
            
            // TODO: Send POST fetch request to `/api/companies/jobs/${jobId}/zip-resumes`
        },
        getStatusBadge(status) {
            const badges = {
                applied: 'badge bg-primary',
                shortlisted: 'badge bg-warning text-dark',
                selected: 'badge bg-success',
                rejected: 'badge bg-danger'
            };
            return badges[status] || 'badge bg-secondary';
        }
    }
};
