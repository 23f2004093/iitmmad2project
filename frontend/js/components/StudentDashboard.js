export default {
    name: 'StudentDashboard',
    data() {
        return {
            student: {
                name: 'Student Name',
                cgpa: '0.0',
                resume_path: null
            },
            drives: [], // Active recruitment drives
            applications: [], // User's applications history
            resumeFile: null
        };
    },
    template: `
        <div>
            <div class="row mb-4">
                <div class="col-10">
                    <h2 class="fw-bold">Student Dashboard</h2>
                    <p class="text-muted">Welcome, {{ student.name }} (CGPA: {{ student.cgpa }})</p>
                </div>
                <div class="col-2 text-end">
                    <button @click="triggerCSVExport" class="btn btn-outline-success">Export CSV</button>
                </div>
            </div>

            <div class="row">
                <!-- Profile and Resume Upload -->
                <div class="col-lg-4 mb-4">
                    <div class="card border-0 shadow-sm p-4 rounded-4 mb-4">
                        <h5 class="fw-bold mb-3">Resume Center</h5>
                        <div v-if="student.resume_path" class="alert alert-success py-2">
                            Resume uploaded! <a :href="'/' + student.resume_path" target="_blank" class="alert-link text-decoration-none fw-bold">View PDF</a>
                        </div>
                        <div v-else class="alert alert-warning py-2">No resume uploaded. Upload a PDF to apply to jobs.</div>
                        
                        <form @submit.prevent="handleResumeUpload">
                            <div class="mb-3">
                                <input class="form-control" type="file" @change="onFileChange" accept="application/pdf" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Upload PDF</button>
                        </form>
                    </div>

                    <div class="card border-0 shadow-sm p-4 rounded-4">
                        <h5 class="fw-bold mb-3">My Applications</h5>
                        <ul class="list-group list-group-flush">
                            <li v-for="app in applications" :key="app.id" class="list-group-item d-flex justify-content-between align-items-center py-3">
                                <div>
                                    <h6 class="mb-0 fw-semibold">{{ app.job.title }}</h6>
                                    <small class="text-muted">{{ app.job.company_name }}</small>
                                </div>
                                <span :class="getStatusBadge(app.status)">{{ app.status.toUpperCase() }}</span>
                            </li>
                            <li v-if="applications.length === 0" class="list-group-item text-center text-muted">No applications submitted yet.</li>
                        </ul>
                    </div>
                </div>

                <!-- Active Drives -->
                <div class="col-lg-8">
                    <div class="card border-0 shadow-sm p-4 rounded-4">
                        <h5 class="fw-bold mb-4">Eligible Placement Drives</h5>
                        <div v-for="drive in drives" :key="drive.id" class="border-bottom pb-3 mb-3">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h5 class="fw-bold mb-1 text-primary">{{ drive.title }}</h5>
                                    <h6 class="text-muted mb-2">{{ drive.company_name }}</h6>
                                </div>
                                <span class="badge bg-secondary">{{ drive.job_type }}</span>
                            </div>
                            <p class="mb-2 text-dark">{{ drive.description }}</p>
                            <div class="row text-muted mb-3 small">
                                <div class="col-sm-4"><strong>Package (CTC):</strong> {{ drive.package_ctc }}</div>
                                <div class="col-sm-4"><strong>Deadline:</strong> {{ drive.deadline }}</div>
                                <div class="col-sm-4"><strong>Eligible CGPA:</strong> {{ drive.min_cgpa }}</div>
                            </div>
                            <button 
                                @click="applyForDrive(drive.id)" 
                                :disabled="hasApplied(drive.id) || !isEligible(drive)"
                                :class="getApplyButtonClass(drive)">
                                {{ getApplyButtonText(drive) }}
                            </button>
                        </div>
                        <div v-if="drives.length === 0" class="text-center py-4 text-muted">No open drives currently available.</div>
                    </div>
                </div>
            </div>
        </div>
    `,
    created() {
        this.fetchDashboardData();
    },
    methods: {
        async fetchDashboardData() {
            console.log("Fetching student dashboard data...");
            // TODO: Fetch student profile (GET '/api/students/me'), active drives (GET '/api/jobs/'),
            // and applications list (GET '/api/students/applications') and populate variables:
            //   - this.student
            //   - this.drives
            //   - this.applications
        },
        onFileChange(e) {
            this.resumeFile = e.target.files[0];
        },
        async handleResumeUpload() {
            if (!this.resumeFile) return;
            console.log("Uploading file:", this.resumeFile.name);
            
            // TODO: Construct FormData and send it via POST fetch request to '/api/students/resume'
            // On success: call this.fetchDashboardData()
        },
        async applyForDrive(driveId) {
            console.log("Applying to job ID:", driveId);
            
            // TODO: Send POST fetch request to `/api/jobs/${driveId}/apply`
            // On success: call this.fetchDashboardData()
        },
        async triggerCSVExport() {
            console.log("Triggering CSV export task...");
            
            // TODO: Send POST fetch request to '/api/students/export-applications' to queue celery task
        },
        hasApplied(driveId) {
            return this.applications.some(app => app.job_id === driveId);
        },
        isEligible(drive) {
            if (!this.student.cgpa) return false;
            return parseFloat(this.student.cgpa) >= parseFloat(drive.min_cgpa);
        },
        getStatusBadge(status) {
            const badges = {
                applied: 'badge bg-primary',
                shortlisted: 'badge bg-warning text-dark',
                selected: 'badge bg-success',
                rejected: 'badge bg-danger'
            };
            return badges[status] || 'badge bg-secondary';
        },
        getApplyButtonText(drive) {
            if (this.hasApplied(drive.id)) return "Already Applied";
            if (!this.isEligible(drive)) return "Not Eligible (CGPA too low)";
            if (!this.student.resume_path) return "Upload Resume to Apply";
            return "Apply Now";
        },
        getApplyButtonClass(drive) {
            if (this.hasApplied(drive.id)) return "btn btn-secondary";
            if (!this.isEligible(drive)) return "btn btn-outline-danger";
            return "btn btn-success";
        }
    }
};
