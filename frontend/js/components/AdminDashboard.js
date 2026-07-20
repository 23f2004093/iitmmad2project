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
            pendingDrives: []
        };
    },
    template: `
        <div>
            <h2 class="fw-bold mb-4">Placement Cell Administrator Dashboard</h2>
            
            <div class="row g-3 mb-4">
                <div class="col-md-3">
                    <div class="card border-0 shadow-sm p-3 rounded-3 bg-primary text-white text-center">
                        <h5>Total Students</h5>
                        <h2 class="fw-bold">{{ stats.total_students }}</h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card border-0 shadow-sm p-3 rounded-3 bg-info text-white text-center">
                        <h5>Registered Companies</h5>
                        <h2 class="fw-bold">{{ stats.total_companies }}</h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card border-0 shadow-sm p-3 rounded-3 bg-success text-white text-center">
                        <h5>Placement Drives</h5>
                        <h2 class="fw-bold">{{ stats.total_jobs }}</h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card border-0 shadow-sm p-3 rounded-3 bg-dark text-white text-center">
                        <h5>Placed %</h5>
                        <h2 class="fw-bold">{{ parseFloat(stats.placement_percentage).toFixed(1) }}%</h2>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-6">
                    <div class="card border-0 shadow-sm p-4 rounded-4 mb-4">
                        <h5 class="fw-bold text-warning mb-3">Pending Company Registrations</h5>
                        <div class="list-group list-group-flush">
                            <div v-for="comp in pendingCompanies" :key="comp.id" class="list-group-item py-3">
                                <h6 class="fw-bold mb-1">{{ comp.company_name }}</h6>
                                <p class="small text-muted mb-2">{{ comp.description }}</p>
                                <button @click="approveCompany(comp.id)" class="btn btn-sm btn-success">Approve Recruiter</button>
                            </div>
                            <div v-if="pendingCompanies.length === 0" class="text-muted text-center py-2">No pending company registrations.</div>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card border-0 shadow-sm p-4 rounded-4">
                        <h5 class="fw-bold text-danger mb-3">Pending Placement Drives</h5>
                        <div class="list-group list-group-flush">
                            <div v-for="drive in pendingDrives" :key="drive.id" class="list-group-item py-3">
                                <div class="d-flex justify-content-between align-items-center">
                                    <h6 class="fw-bold mb-0">{{ drive.title }}</h6>
                                    <span class="badge bg-secondary">{{ drive.min_cgpa }} CGPA</span>
                                </div>
                                <p class="small text-muted mb-2">Posted by Company ID: {{ drive.company_id }}</p>
                                <button @click="approveDrive(drive.id)" class="btn btn-sm btn-danger">Approve Drive</button>
                            </div>
                            <div v-if="pendingDrives.length === 0" class="text-muted text-center py-2">No pending placement drives.</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `,
    created() {
        this.fetchAdminData();
    },
    methods: {
        async fetchAdminData() {
            console.log("Fetching admin portal statistics and approvals...");
            try {
                const statsres = await fetch('/api/admin/stats');
                if (statsres.ok) {
                    const statsdata = await statsres.json();
                    this.stats = statsdata.stats;
                } else if (statsres.status === 403) {
                    this.$router.push('/');
                    return;
                }

                const compres = await fetch('/api/admin/pending-recruiters');
                if (compres.ok) {
                    const compdata = await compres.json();
                    this.pendingCompanies = compdata.pending_recruiters;
                }

                const driveres = await fetch('/api/admin/pending-drives');
                if (driveres.ok) {
                    const drivedata = await driveres.json();
                    this.pendingDrives = drivedata.pending_drives;
                }
            } catch (error) {
                console.error("error fetching admin data:", error);
            }
        },

        async approveCompany(id) {
            console.log("Approving company ID:", id);
            try {
                const response = await fetch(`/api/admin/approve-recruiter/${id}`, { method: 'POST' });
                const data = await response.json();
                if (response.ok) {
                    alert("Recruiter approved successfully");
                    this.fetchAdminData();
                } else {
                    alert(data.message || "Failed to approve recruiter.");
                }
            } catch (error) {
                console.error("error approving company:", error);
                alert("Server connection failed during company approval.");
            }
        },

        async approveDrive(id) {
            console.log("Approving placement drive ID:", id);
            try {
                const response = await fetch(`/api/admin/approve-drive/${id}`, { method: 'POST' });
                const data = await response.json();
                if (response.ok) {
                    alert("Placement drive approved");
                    this.fetchAdminData();
                } else {
                    alert(data.message || "Failed to approve drive.");
                }
            } catch (error) {
                console.error("error approving drive:", error);
                alert("Server connection failed during drive approval.");
            }
        }
    }
};
