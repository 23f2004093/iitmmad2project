export default {
    name: 'CompanyDashboard',
    data() {
        return {
            company: {
                company_name: '',
                is_approved: false
            },
            drives: [],
            selectedJobId: null,
            selectedDriveTitle: '',
            applicants: [],
            newDrive: {
                title: '',
                description: '',
                job_type: 'Full-Time',
                package_ctc: '',
                deadline: '',
                min_cgpa: 0.0
            }
        };
    },
    template: `
        <div>
            <!-- Unified Header with Logout Button -->
            <div class="dashboard-header">
                <div>
                    <h2>Recruiter Dashboard</h2>
                    <p>Welcome, {{ company.company_name }} | Status: {{ company.is_approved ? 'Approved Recruiter' : 'Awaiting Admin Approval' }}</p>
                </div>
                <div>
                    <button @click="handleLogout" class="btn-logout">Logout</button>
                </div>
            </div>

            <p v-if="!company.is_approved" style="color: red; font-weight: bold; margin-bottom: 20px;">
                Notice: Your profile is pending Admin approval. You cannot post new placement drives until approved.
            </p>
            <hr v-if="!company.is_approved">

            <!-- Create Placement Drive -->
            <div>
                <h3>Create New Placement Drive</h3>
                <form @submit.prevent="createDrive">
                    <div style="margin-bottom: 8px;">
                        <input v-model="newDrive.title" type="text" placeholder="Job Title (e.g. Software Engineer)" required :disabled="!company.is_approved">
                        <input v-model="newDrive.package_ctc" type="text" placeholder="Package CTC (e.g. 12 LPA)" required :disabled="!company.is_approved">
                    </div>
                    <div style="margin-bottom: 8px;">
                        <input v-model="newDrive.min_cgpa" type="number" step="0.1" min="0" max="10" placeholder="Min CGPA" required :disabled="!company.is_approved">
                        <select v-model="newDrive.job_type" :disabled="!company.is_approved">
                            <option value="Full-Time">Full-Time</option>
                            <option value="Internship">Internship</option>
                        </select>
                        <input v-model="newDrive.deadline" type="date" required :disabled="!company.is_approved" title="Application Deadline">
                    </div>
                    <div style="margin-bottom: 8px;">
                        <textarea v-model="newDrive.description" placeholder="Job Description..." rows="3" style="width: 100%; max-width: 500px;" required :disabled="!company.is_approved"></textarea>
                    </div>
                    <button type="submit" :disabled="!company.is_approved">Post Placement Drive</button>
                </form>
            </div>
            <hr>

            <!-- Created Placement Drives -->
            <div>
                <h3>Created Placement Drives</h3>
                <button @click="fetchCompanyData">Refresh Drives</button>
                <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%; margin-top: 10px;">
                    <thead>
                        <tr>
                            <th>Job Title</th>
                            <th>Package CTC</th>
                            <th>Min CGPA</th>
                            <th>Job Type</th>
                            <th>Deadline</th>
                            <th>Applicants</th>
                            <th>Approval Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="drive in drives" :key="drive.id">
                            <td><strong>{{ drive.title }}</strong></td>
                            <td>{{ drive.package_ctc }}</td>
                            <td>{{ drive.min_cgpa }}</td>
                            <td>{{ drive.job_type }}</td>
                            <td>{{ drive.deadline }}</td>
                            <td>{{ drive.applicant_count }}</td>
                            <td>{{ drive.status }}</td>
                            <td>
                                <button @click="viewApplicants(drive.id, drive.title)">View Applicants</button>
                            </td>
                        </tr>
                        <tr v-if="drives.length === 0">
                            <td colspan="8">No placement drives posted yet.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <hr>

            <!-- Applicants Management Section -->
            <div v-if="selectedJobId">
                <h3>Applicants for: {{ selectedDriveTitle }}</h3>
                <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%; margin-top: 10px;">
                    <thead>
                        <tr>
                            <th>Student Name</th>
                            <th>Roll Number</th>
                            <th>Department</th>
                            <th>CGPA</th>
                            <th>Resume</th>
                            <th>Current Status</th>
                            <th>Update Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="app in applicants" :key="app.application_id">
                            <td>{{ app.student_name }}</td>
                            <td>{{ app.roll_number }}</td>
                            <td>{{ app.department }}</td>
                            <td>{{ app.cgpa }}</td>
                            <td>
                                <a v-if="app.resume_path" :href="'/' + app.resume_path" target="_blank">View PDF</a>
                                <span v-else>No PDF</span>
                            </td>
                            <td><strong>{{ app.status }}</strong></td>
                            <td>
                                <button @click="updateStatus(app.application_id, 'shortlisted')">Shortlist</button>
                                <button @click="updateStatus(app.application_id, 'selected')">Select</button>
                                <button @click="updateStatus(app.application_id, 'rejected')">Reject</button>
                            </td>
                        </tr>
                        <tr v-if="applicants.length === 0">
                            <td colspan="7">No student applications received for this drive yet.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `,
    created() {
        this.fetchCompanyData();
    },
    methods: {
        async handleLogout() {
            const res = await fetch('/api/auth/logout', { method: 'POST' });
            if (res.ok) {
                this.$router.push('/');
            }
        },
        async fetchCompanyData() {
            const res = await fetch('/api/companies/dashboard');
            if (res.ok) {
                const data = await res.json();
                this.company = data.company;
                this.drives = data.drives;
            } else if (res.status === 403) {
                this.$router.push('/');
            }
        },
        async createDrive() {
            const res = await fetch('/api/companies/jobs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.newDrive)
            });
            const data = await res.json();
            if (res.ok) {
                alert(data.message);
                this.newDrive = { title: '', description: '', job_type: 'Full-Time', package_ctc: '', deadline: '', min_cgpa: 0.0 };
                this.fetchCompanyData();
            } else {
                alert(data.message || "Failed to create drive.");
            }
        },
        async viewApplicants(jobId, title) {
            this.selectedJobId = jobId;
            this.selectedDriveTitle = title;
            const res = await fetch(`/api/companies/drives/${jobId}/applications`);
            if (res.ok) {
                const data = await res.json();
                this.applicants = data.applicants;
            }
        },
        async updateStatus(appId, newStatus) {
            const res = await fetch(`/api/companies/applications/${appId}/status`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            });
            const data = await res.json();
            if (res.ok) {
                this.viewApplicants(this.selectedJobId, this.selectedDriveTitle);
            } else {
                alert(data.message || "Failed to update status.");
            }
        }
    }
};