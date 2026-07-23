export default {
    name: 'StudentDashboard',
    data() {
        return {
            student: {
                name: 'Student Name',
                cgpa: '0.0',
                resume_path: null
            },
            editName: '',
            editDepartment: '',
            drives: [], 
            applications: [], 
            resumeFile: null,
            searchQuery: '',
            filterEligibility: 'all',
            exporting: false,
            exportStatusText: ''
        };
    },
    computed: {
        filteredDrives() {
            return this.drives.filter(drive => {
                const matchesQuery = !this.searchQuery || 
                    drive.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                    drive.company_name.toLowerCase().includes(this.searchQuery.toLowerCase());
                
                const matchesEligibility = this.filterEligibility === 'all' || this.isEligible(drive);
                
                return matchesQuery && matchesEligibility;
            });
        }
    },
    template: `
        <div>
            <div class="dashboard-header">
                <div>
                    <h2>Student Dashboard</h2>
                    <p>Welcome, {{ student.name }} (CGPA: {{ student.cgpa }})</p>
                </div>
                <div>
                    <button @click="triggerCSVExport" :disabled="exporting">
                        {{ exporting ? 'Exporting...' : 'Export Applications CSV' }}
                    </button>
                    <button @click="handleLogout" class="btn-logout">Logout</button>
                </div>
            </div>

            <div v-if="exporting" class="alert alert-info py-2 mb-4 d-flex justify-content-between align-items-center">
                <span><strong>CSV Export Status:</strong> {{ exportStatusText }}</span>
                <span class="spinner-border spinner-border-sm" role="status"></span>
            </div>

            <div class="row">
                <div class="col-lg-4 mb-4">
                    <div class="card border-0 shadow-sm p-4 rounded-4 mb-4">
                        <h5 class="fw-bold mb-3">Edit Profile Details</h5>
                        <form @submit.prevent="handleProfileUpdate">
                            <div class="mb-3">
                                <label class="form-label small fw-semibold">Name</label>
                                <input v-model="editName" type="text" class="form-control form-control-sm" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label small fw-semibold">Department</label>
                                <input v-model="editDepartment" type="text" class="form-control form-control-sm" required>
                            </div>
                            <button type="submit" class="btn btn-sm btn-primary w-100">Save Changes</button>
                        </form>
                    </div>

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
                            <li v-for="app in applications" :key="app.id" class="list-group-item d-flex justify-content-between align-items-center py-3 px-0">
                                <div>
                                    <h6 class="mb-0 fw-semibold">{{ app.job.title }}</h6>
                                    <small class="text-muted">{{ app.job.company_name }}</small>
                                </div>
                                <span :class="getStatusBadge(app.status)">{{ app.status.toUpperCase() }}</span>
                            </li>
                            <li v-if="applications.length === 0" class="list-group-item text-center text-muted px-0">No applications submitted yet.</li>
                        </ul>
                    </div>
                </div>

                <div class="col-lg-8">
                    <div class="card border-0 shadow-sm p-4 rounded-4">
                        <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center mb-4">
                            <h5 class="fw-bold m-0 mb-2 mb-sm-0">Placement Drives</h5>
                            <div class="d-flex gap-2 w-100 w-sm-auto">
                                <input v-model="searchQuery" type="text" class="form-control form-control-sm" placeholder="Search title/company...">
                                <select v-model="filterEligibility" class="form-select form-select-sm" style="max-width: 150px;">
                                    <option value="all">All Drives</option>
                                    <option value="eligible">Eligible Only</option>
                                </select>
                            </div>
                        </div>

                        <div v-for="drive in filteredDrives" :key="drive.id" class="border-bottom pb-3 mb-3">
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
                        <div v-if="filteredDrives.length === 0" class="text-center py-4 text-muted">No matching placement drives found.</div>
                    </div>
                </div>
            </div>
        </div>
    `,
    created() {
        this.fetchDashboardData();
    },
    methods: {
        async handleLogout() {
            const res = await fetch('/api/auth/logout', { method: 'POST' });
            if (res.ok) {
                this.$router.push('/');
            }
        },
        async fetchDashboardData() {
            try {
                const profileRes = await fetch('/api/students/me');
                if (profileRes.ok) {
                    const profileData = await profileRes.json();
                    this.student = profileData.student;
                    this.editName = this.student.name;
                    this.editDepartment = this.student.department;
                } else if (profileRes.status === 401) {
                    this.$router.push('/');
                    return;
                }

                const drivesRes = await fetch('/api/jobs/');
                if (drivesRes.ok) {
                    const drivesData = await drivesRes.json();
                    this.drives = drivesData.jobs;
                }

                const appsRes = await fetch('/api/students/applications');
                if (appsRes.ok) {
                    const appsData = await appsRes.json();
                    this.applications = appsData.applications;
                }
            } catch (error) {
                console.error("Error fetching dashboard data:", error);
            }
        },
        async handleProfileUpdate() {
            try {
                const res = await fetch('/api/students/profile', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: this.editName,
                        department: this.editDepartment
                    })
                });
                const data = await res.json();
                if (res.ok) {
                    alert(data.message);
                    this.fetchDashboardData();
                } else {
                    alert(data.message || "Failed to update profile.");
                }
            } catch (e) {
                console.error("Profile update error:", e);
            }
        },
        onFileChange(e) {
            this.resumeFile = e.target.files[0];
        },
        async handleResumeUpload() {
            if (!this.resumeFile) return;
            const formData = new FormData();
            formData.append('resume', this.resumeFile);

            try {
                const response = await fetch('/api/students/resume', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                if (response.ok) {
                    alert("Resume uploaded successfully!");
                    this.resumeFile = null;
                    this.fetchDashboardData();
                } else {
                    alert(data.message || "Failed to upload resume");
                }
            } catch (error) {
                console.error("Resume upload error:", error);
                alert("Server connection failed during resume upload.");
            }
        },
        async applyForDrive(driveId) {
            try {
                const response = await fetch(`/api/jobs/${driveId}/apply`, {
                    method: 'POST'
                });
                
                const data = await response.json();
                if (response.ok) {
                    alert("Application submitted successfully!");
                    this.fetchDashboardData();
                } else {
                    alert(data.message || "Failed to apply");
                }
            } catch (error) {
                console.error("Apply drive error:", error);
                alert("Server connection failed during application process.");
            }
        },
        async triggerCSVExport() {
            this.exporting = true;
            this.exportStatusText = 'Queuing asynchronous Celery export task...';
            try {
                const response = await fetch('/api/students/export-applications', {
                    method: 'POST'
                });
                const data = await response.json();
                if (response.ok && data.task_id) {
                    const taskId = data.task_id;
                    this.exportStatusText = 'Export task processing in background queue...';
                    const interval = setInterval(async () => {
                        try {
                            const statusRes = await fetch(`/api/students/export-status/${taskId}`);
                            const statusData = await statusRes.json();
                            if (statusData.status === 'success') {
                                clearInterval(interval);
                                this.exportStatusText = 'Task complete! Downloading file...';
                                setTimeout(() => {
                                    this.exporting = false;
                                    const a = document.createElement('a');
                                    a.href = statusData.download_url;
                                    a.download = `applications_history_${this.student.roll_number || 'student'}.csv`;
                                    document.body.appendChild(a);
                                    a.click();
                                    a.remove();
                                }, 800);
                            } else if (statusData.status === 'failure') {
                                clearInterval(interval);
                                alert("Celery export task failed: " + statusData.message);
                                this.exporting = false;
                            }
                        } catch (err) {
                            clearInterval(interval);
                            this.exporting = false;
                        }
                    }, 1000);
                } else {
                    alert(data.message || "Failed to start export task.");
                    this.exporting = false;
                }
            } catch (error) {
                alert("Server connection failed during CSV export.");
                this.exporting = false;
            }
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
