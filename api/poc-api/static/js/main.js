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
        local_reception: 'Local Reception',
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
        search: 'Rechercher',
        traceability: 'Traçabilité',
        recent_transactions: 'Transactions récentes',
        calendar: 'Calendrier',
        replantation: 'Replantation',
        settings: 'Paramètres',
        more: 'Plus ',
        back: 'Retour',
        map: 'Carte',
        package: {
            types: {
                all: 'Tous',
                plot: 'Parcelle',
                harvest: 'Récolte',
                transport: 'Transport',
            }
        },
        beginning_date: 'Date de début',
        ending_date: 'Date de fin',
        gps_coordinates: 'Coordonnées GPS',
        user_id: 'ID utilisateur',
        village: 'Village',
        tree_specie: 'Essence d\'arbre',
        number_of_trees_cut: 'Nombre d\'arbres coupés',
        details: 'Détails',
        loading_transport: 'Chargement et transport',
        reception: 'Réception',
        local_reception: 'Local Réception',
        plate_number: 'Numéro d\'immatriculation',
        loading_date: 'Date de chargement',
        scanned_bags: 'Sacs scannés',
        reception_date: 'Date de réception',
        documents: 'Documents',
        receipt: 'Reçu',
        oven: 'Four',
        oven_type: 'Type de four',
        oven_measurements: 'Mesures du four',
        height: 'Hauteur',
        length: 'Longueur',
        width: 'Largeur',
        carbonizer_id: 'ID Carbonisateur',
        carbonization: 'Carbonisation',
        logging: 'Abattage',
        timber_volume: 'Volume de bois',
        weekday_names: {
            short: {
                monday: 'Lun',
                tuesday: 'Mar',
                wednesday: 'Mer',
                thursday: 'Jeu',
                friday: 'Ven',
                saturday: 'Sam',
                sunday: 'Dim',
            }
        },
        month_names: {
            january: 'Janvier', february: 'Février', march: 'Mar',
            april: 'Avril', may: 'Mai', june: 'Juin',
            july: 'Juillet', august: 'Août', september: 'Septembre',
            october: 'Octobre', 'november': 'Novembre', december: 'Décembre'
        },
        trees_planted: 'Arbres plantés',
        trees_cut: 'Arbres coupés',
        parcel_list: 'Liste des parcelles',
        tree_species_list: 'Liste des essences d\'arbre',
        village_list: 'Liste des villages',
        add_new: 'Ajouter à la liste',
        edit: 'Modifier',
        delete: 'Supprimer',
        name: 'Nombre d\'arbres coupés',
        code: 'Code',
        delivery_destination: 'Destination de livraison',
        yes: 'Oui',
        no: 'Non',
        modal: {
            delete_item: 'Voulez-vous supprimer cet élément?'
        },
        custom_measurements: 'Mesures selon vos spécifications',
        fixed_measurements: 'Mesures fixes',
        supply_chain: 'Chaîne d\'approvisionnement',
        blockchain_transaction: 'Transaction blockchain',
        header_signature: 'Signature d\'en-tête',
        payload: 'Charge utile',
        loading: 'Chargement',
        dashboard: 'Tableau de bord',
        logout: 'Quitter',
        email_address: 'Adresse e-mail',
        password: 'Mot de passe',
        connection: 'Connexion'
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
