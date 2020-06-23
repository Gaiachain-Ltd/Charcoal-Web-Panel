const router = new VueRouter({
    routes: [
        {path: '/traceability', component: Packages},
        {path: '/traceability/:id', component: PackageDetails},
        {path: '/calendar', component: Calendar},
        {path: '/replantation', component: Replantation},
        {path: '/settings', component: Settings},
        {path: '/', redirect: '/traceability'}
    ]
});

const messages = {
    en: {
        search: 'Search',
        traceability: 'Traceability',
        recent_transactions: 'Recent transactions',
        calendar: 'Calendar',
        replantation: 'Replantation',
        settings: 'Settings',
        more: 'More',
        back: 'Back',
        map: 'Map',
        package: {
            types: {
                all: 'All',
                plot: 'Plot',
                harvest: 'Harvest',
                transport: 'Transport',
            }
        },
        beginning_date: 'Beginning date',
        ending_date: 'Ending date',
        gps_coordinates: 'GPS coordinates',
        user_id: 'User ID',
        village: 'Village',
        tree_specie: 'Tree specie',
        number_of_trees_cut: 'Number of trees cut',
        details: 'details',
        loading_transport: 'Loading and transport',
        reception: 'Reception',
        plate_number: 'Plate Number',
        loading_date: 'Loading date',
        scanned_bags: 'Scanned bags',
        reception_date: 'Reception date',
        documents: 'Documents',
        receipt: 'Receipt',
        oven: 'Oven',
        oven_type: 'Oven type',
        oven_measurements: 'Oven measurements',
        height: 'Height',
        length: 'Length',
        width: 'Width',
        carbonizer_id: 'Carbonizer\'s ID',
        carbonization: 'Carbonization',
        logging: 'Logging',
        timber_volume: 'Timber volume',
        weekday_names: {
            short: {
                monday: 'Mon',
                tuesday: 'Tue',
                wednesday: 'Wed',
                thursday: 'Thu',
                friday: 'Fri',
                saturday: 'Sat',
                sunday: 'Sun',
            }
        },
        month_names: {
            january: 'January', february: 'February', march: 'March',
            april: 'April', may: 'May', june: 'June',
            july: 'July', august: 'August', september: 'September',
            october: 'October', 'november': 'November', december: 'December'
        },
        trees_planted: 'Trees planted',
        trees_cut: 'Trees cut',
        parcel_list: 'Parcelle list',
        tree_species_list: 'Tree species list',
        village_list: 'Village list',
        add_new: 'Add new',
        edit: 'Edit',
        delete: 'Delete',
        name: 'Name',
        code: 'Code',
        delivery_destination: 'Delivery destination',
        yes: 'Yes',
        no: 'No',
        modal: {
            delete_item: 'Are you sure you want to delete this item?'
        },
        custom_measurements: 'Custom measurements',
        fixed_measurements: 'Fixed measurements',
        supply_chain: 'Supply chain',
        blockchain_transaction: 'Blockchain transaction',
        header_signature: 'Header signature',
        payload: 'Payload',
        loading: 'Loading',
        dashboard: 'Dashboard',
        logout: 'Logout',
        email_address: 'E-mail address',
        password: 'Password',
        connection: 'Connection'
    },
    fr: {
        search: 'Search',
        traceability: 'Traceability',
        recent_transactions: 'Recent transactions',
        calendar: 'Calendar',
        replantation: 'Replantation',
        settings: 'Settings',
        more: 'More',
        back: 'Back',
        map: 'Map',
        package: {
            types: {
                all: 'All',
                plot: 'Plot',
                harvest: 'Harvest',
                transport: 'Transport',
            }
        },
        beginning_date: 'Beginning date',
        ending_date: 'Ending date',
        gps_coordinates: 'GPS coordinates',
        user_id: 'User ID',
        village: 'Village',
        tree_specie: 'Tree specie',
        number_of_trees_cut: 'Number of trees cut',
        details: 'details',
        loading_transport: 'Loading and transport',
        reception: 'Reception',
        plate_number: 'Plate Number',
        loading_date: 'Loading date',
        scanned_bags: 'Scanned bags',
        reception_date: 'Reception date',
        documents: 'Documents',
        receipt: 'Receipt',
        oven: 'Oven',
        oven_type: 'Oven type',
        oven_measurements: 'Oven measurements',
        height: 'Height',
        length: 'Length',
        width: 'Width',
        carbonizer_id: 'Carbonizer\'s ID',
        carbonization: 'Carbonization',
        logging: 'Logging',
        timber_volume: 'Timber volume',
        weekday_names: {
            short: {
                monday: 'Mon',
                tuesday: 'Tue',
                wednesday: 'Wed',
                thursday: 'Thu',
                friday: 'Fri',
                saturday: 'Sat',
                sunday: 'Sun',
            }
        },
        month_names: {
            january: 'January', february: 'February', march: 'March',
            april: 'April', may: 'May', june: 'June',
            july: 'July', august: 'August', september: 'September',
            october: 'October', 'november': 'November', december: 'December'
        },
        trees_planted: 'Trees planted',
        trees_cut: 'Trees cut',
        parcel_list: 'Parcelle list',
        tree_species_list: 'Tree species list',
        village_list: 'Village list',
        add_new: 'Add new',
        edit: 'Edit',
        delete: 'Delete',
        name: 'Name',
        code: 'Code',
        delivery_destination: 'Delivery destination',
        yes: 'Yes',
        no: 'No',
        modal: {
            delete_item: 'Are you sure you want to delete this item?'
        },
        custom_measurements: 'Custom measurements',
        fixed_measurements: 'Fixed measurements',
        supply_chain: 'Supply chain',
        blockchain_transaction: 'Blockchain transaction',
        header_signature: 'Header signature',
        payload: 'Payload',
        loading: 'Loading',
        dashboard: 'Dashboard',
        logout: 'Logout',
        email_address: 'E-mail address',
        password: 'Password',
        connection: 'Connection'
    },
};

const i18n = new VueI18n({
    locale: 'en',
    messages,
});

Vue.http.interceptors.push((request, next) => {
    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').getAttribute("value");
    request.headers.set('X-CSRFTOKEN', csrftoken);
    next()
});

const app = new Vue({
    delimiters: ['[[', ']]'],
    data: {
        currentPageName: '',
        staticPrefix: window.staticPrefix,
        loading: false,
    },
    computed: {
        languageName() {
            switch (this.$i18n.locale) {
                case 'en':
                    return 'English';
                case 'fr':
                    return 'Française';
            }
        },
    },
    methods: {
        switchLanguage() {
            switch (this.$i18n.locale) {
                case 'en':
                    this.$i18n.locale = 'fr';
                    break;
                case 'fr':
                    this.$i18n.locale = 'en';
                    break;
            }

        }
    },
    router,
    i18n
}).$mount('#dashboard-main');
