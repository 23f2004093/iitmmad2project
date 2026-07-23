export default {
    name: 'AdminDashboard',
    data() {
        return {
            stats: {
                total_students: 0,
                total_companies: 0,
                total_jobs: 0,
                placement_percentage: 0
            },
            pendingCompanies: [],
            pendingDrives: [],
            allApplications: [],
            allStudents: [],
            searchQuery: '',
            searchResults: {
                students: [],
                companies: []
            },
            isSearching: false
        };
    },
    template: `
        <div>
            <!-- Unified Header with Logout Button -->
            <div class="dashboard-header">
                <div>
                    <h2>Admin Dashboard</h2>
                    <p>Overview of system metrics, student profiles, recruiter registrations, and job applications</p>
                </div>
                <div>
                    <button @click="handleLogout" class="btn-logout">Logout</button>
                </div>
            </div>
            
            <!-- Statistics Overview -->
            <div>
                <p>
                    <strong>Total Students:</strong> {{ stats.total_students }} | 
                    <strong>Approved Companies:</strong> {{ stats.total_companies }} | 
                    <strong>Active Drives:</strong> {{ stats.total_jobs }} | 
                    <strong>Placement %:</strong> {{ parseFloat(stats.placement_percentage).toFixed(1) }}%
                </p>
            </div>
            <hr>

            <!-- Search Section -->
            <div>
                <h3>Search Portal</h3>
                <form @submit.prevent="handleSearch">
                    <input v-model="searchQuery" type="text" placeholder="Search student or company..." required>
                    <button type="submit">Search</button>
                    <button v-if="isSearching" @click="clearSearch" type="button">Clear</button>
                </form>

                <div v-if="isSearching" style="margin-top: 15px;">
                    <h4>Matching Students</h4>
                    <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Roll No</th>
                                <th>Department</th>
                                <th>CGPA</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="s in searchResults.students" :key="s.user_id">
                                <td>{{ s.name }}</td>
                                <td>{{ s.roll_number }}</td>
                                <td>{{ s.department }}</td>
                                <td>{{ s.cgpa }}</td>
                                <td>{{ s.is_active ? 'Active' : 'Blacklisted' }}</td>
                                <td>
                                    <button @click="toggleUserStatus(s.user_id)">
                                        {{ s.is_active ? 'Blacklist' : 'Reactivate' }}
                                    </button>
                                </td>
                            </tr>
                            <tr v-if="searchResults.students.length === 0">
                                <td colspan="6">No matching students found.</td>
                            </tr>
                        </tbody>
                    </table>

                    <h4 style="margin-top: 15px;">Matching Companies</h4>
                    <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
                        <thead>
                            <tr>
                                <th>Company</th>
                                <th>HR Contact</th>
                                <th>Website</th>
                                <th>Approval</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="c in searchResults.companies" :key="c.user_id">
                                <td>{{ c.company_name }}</td>
                                <td>{{ c.hr_contact }}</td>
                                <td>{{ c.website }}</td>
                                <td>{{ c.is_approved ? 'Approved' : 'Pending' }}</td>
                                <td>{{ c.is_active ? 'Active' : 'Blacklisted' }}</td>
                                <td>
                                    <button @click="toggleUserStatus(c.user_id)">
                                        {{ c.is_active ? 'Blacklist' : 'Reactivate' }}
                                    </button>
                                </td>
                            </tr>
                            <tr v-if="searchResults.companies.length === 0">
                                <td colspan="6">No matching companies found.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <hr>

            <!-- Pending Approvals & Rejections -->
            <div>
                <h3>Pending Approvals</h3>
                
                <h4>Pending Company Registrations</h4>
                <ul>
                    <li v-for="comp in pendingCompanies" :key="comp.id" style="margin-bottom: 10px;">
                        <strong>{{ comp.company_name }}</strong> (HR: {{ comp.hr_contact }}, Website: {{ comp.website }})
                        <br>
                        <button @click="approveCompany(comp.id)">Approve Recruiter</button>
                        <button @click="rejectCompany(comp.id)">Reject</button>
                    </li>
                    <li v-if="pendingCompanies.length === 0">No pending company registrations.</li>
                </ul>

                <h4>Pending Placement Drives</h4>
                <ul>
                    <li v-for="drive in pendingDrives" :key="drive.id" style="margin-bottom: 10px;">
                        <strong>{{ drive.title }}</strong> - {{ drive.company_name }} (Package: {{ drive.package_ctc }}, Min CGPA: {{ drive.min_cgpa }})
                        <br>
                        <button @click="approveDrive(drive.id)">Approve Drive</button>
                        <button @click="rejectDrive(drive.id)">Reject</button>
                    </li>
                    <li v-if="pendingDrives.length === 0">No pending placement drives.</li>
                </ul>
            </div>
            <hr>

            <!-- Student Details Directory -->
            <div>
                <h3>All Student Details</h3>
                <button @click="fetchAllStudents">Refresh Students</button>
                <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%; margin-top: 10px;">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Roll Number</th>
                            <th>Department</th>
                            <th>CGPA</th>
                            <th>Resume</th>
                            <th>Account Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="s in allStudents" :key="s.user_id">
                            <td>{{ s.name }}</td>
                            <td>{{ s.roll_number }}</td>
                            <td>{{ s.department }}</td>
                            <td>{{ s.cgpa }}</td>
                            <td>
                                <a v-if="s.resume_path" :href="'/' + s.resume_path" target="_blank">View PDF</a>
                                <span v-else>No PDF</span>
                            </td>
                            <td>{{ s.is_active ? 'Active' : 'Blacklisted' }}</td>
                            <td>
                                <button @click="toggleUserStatus(s.user_id)">
                                    {{ s.is_active ? 'Blacklist' : 'Reactivate' }}
                                </button>
                            </td>
                        </tr>
                        <tr v-if="allStudents.length === 0">
                            <td colspan="7">No students registered yet.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <hr>

            <!-- All Applications History Table -->
            <div>
                <h3>All Student Applications</h3>
                <button @click="fetchAllApplications">Refresh List</button>
                <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%; margin-top: 10px;">
                    <thead>
                        <tr>
                            <th>Student Name</th>
                            <th>Roll Number</th>
                            <th>Company</th>
                            <th>Drive Title</th>
                            <th>Applied Date</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="app in allApplications" :key="app.id">
                            <td>{{ app.student_name }}</td>
                            <td>{{ app.student_roll }}</td>
                            <td>{{ app.company_name }}</td>
                            <td>{{ app.job_title }}</td>
                            <td>{{ app.applied_on }}</td>
                            <td>{{ app.status }}</td>
                        </tr>
                        <tr v-if="allApplications.length === 0">
                            <td colspan="6">No student applications found.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `,
    created() {
        this.fetchAdminData();
        this.fetchAllStudents();
        this.fetchAllApplications();
    },
    methods: {
        async handleLogout() {
            const res = await fetch('/api/auth/logout', { method: 'POST' });
            if (res.ok) {
                this.$router.push('/');
            }
        },
        async fetchAdminData() {
            const statsRes = await fetch('/api/admin/stats');
            if (statsRes.ok) {
                const data = await statsRes.json();
                this.stats = data.stats;
            } else if (statsRes.status === 403) {
                this.$router.push('/');
                return;
            }

            const compRes = await fetch('/api/admin/pending-recruiters');
            if (compRes.ok) {
                const data = await compRes.json();
                this.pendingCompanies = data.pending_recruiters;
            }

            const driveRes = await fetch('/api/admin/pending-drives');
            if (driveRes.ok) {
                const data = await driveRes.json();
                this.pendingDrives = data.pending_drives;
            }
        },
        async fetchAllStudents() {
            const res = await fetch('/api/admin/students');
            if (res.ok) {
                const data = await res.json();
                this.allStudents = data.students;
            }
        },
        async fetchAllApplications() {
            const res = await fetch('/api/admin/applications');
            if (res.ok) {
                const data = await res.json();
                this.allApplications = data.applications;
            }
        },
        async approveCompany(id) {
            const res = await fetch(`/api/admin/approve-recruiter/${id}`, { method: 'POST' });
            if (res.ok) this.fetchAdminData();
        },
        async rejectCompany(id) {
            if (!confirm("Reject company registration?")) return;
            const res = await fetch(`/api/admin/reject-recruiter/${id}`, { method: 'POST' });
            if (res.ok) this.fetchAdminData();
        },
        async approveDrive(id) {
            const res = await fetch(`/api/admin/approve-drive/${id}`, { method: 'POST' });
            if (res.ok) this.fetchAdminData();
        },
        async rejectDrive(id) {
            if (!confirm("Reject placement drive?")) return;
            const res = await fetch(`/api/admin/reject-drive/${id}`, { method: 'POST' });
            if (res.ok) this.fetchAdminData();
        },
        async handleSearch() {
            if (!this.searchQuery) return;
            const res = await fetch(`/api/admin/search?query=${encodeURIComponent(this.searchQuery)}`);
            if (res.ok) {
                const data = await res.json();
                this.searchResults = { students: data.students, companies: data.companies };
                this.isSearching = true;
            }
        },
        clearSearch() {
            this.searchQuery = '';
            this.searchResults = { students: [], companies: [] };
            this.isSearching = false;
        },
        async toggleUserStatus(userId) {
            const res = await fetch(`/api/admin/toggle-user-status/${userId}`, { method: 'POST' });
            if (res.ok) {
                if (this.isSearching) this.handleSearch();
                this.fetchAllStudents();
            }
        }
    }
};