export default {
    name: 'NavbarComponent',
    template: `
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <router-link class="navbar-brand" to="/">Placement Portal</router-link>
                <div class="collapse navbar-collapse">
                    <ul class="navbar-nav ms-auto">
                        <li class="nav-item">
                            <router-link class="nav-link" to="/">Login</router-link>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    `
};
