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
    //     computed: {
    //         formattedDate() {
    //           return dateFns.format(this.curr, 'MM/DD/YYYY');
    //         }
    //     },
    //     watch: {
    //         keyword: function (val) {
    //             let args = "";
    //             if (this.content_page === 'recent_actions') {
    //                 args = "?limit=" + this.recent_limit + "&keyword=" + val;
    //             }
    //             this.getActions(args, search=true)
    //         },
    //         package_keyword: function (val) {
    //             let args = "";
    //             if (this.content_page === 'recent_actions') {
    //                 args = "&keyword=" + val;
    //             }
    //             this.getPackages(this.active_package_type, args, search=true)
    //         },
    //     },
    //     mounted: function () {
    //         // this.loading = true;
    //         // this.showPackages('all');
    //         // document.getElementById('current-page-name').innerHTML = 'Traceability'
    //     },
    //     methods: {
    //         setActiveAction: function(el, title = "") {
    //             let previous_element = this.active_element;
    //             this.active_element = el;
    //             // if (el === 'tracability') {
    //             //     if (previous_element === 'tracability') {
    //             //         this.active_element = '';
    //             //         this.show_subelements = false;
    //             //     } else {
    //             //         this.show_subelements = true;
    //             //     }
    //             //     this.active_subelement = '';
    //             // } else {
    //             //     this.show_subelements = false;
    //             //     this.active_subelement = '';
    //             //     this.active_package_type = '';
    //             // }
    //             if (title)
    //                 document.getElementById('current-page-name').innerHTML = title;
    //             this.loading = false;
    //         },
    //         getActionTypes: function () {
    //             this.loading = true;
    //             this.$http.get('/entities/types/').then(function (response){
    //                     this.action_types = response.data;
    //                     this.loading = false;
    //                 }).catch(function(err) {
    //                     this.loading = false;
    //                     console.log(err);
    //                 })
    //         },
    //         getRecentActions: function (args) {
    //             this.getActions()
    //         },
    //         getActions: function (args="", search=false) {
    //             if (!search) {
    //                 this.loading = true;
    //             }
    //             this.$http.get(
    //                '/entities/batch_web/' + args,
    //            ).then(function (response) {
    //                this.actions = response.data.results;
    //                this.loading = false;
    //                return response.data.results
    //            }).catch(function (err) {
    //             this.loading = false;
    //             console.log(err);
    //            })
    //         },
    //         showRecentTransactions: function () {
    //             this.loading = true;
    //             this.active_subelement = 'tracability_transactions';
    //             this.active_element = 'tracability_transactions';
    //             this.getActions();
    //         },
    //         getActionTitle: function (action) {
    //             return this.action_types[action.action] + ' ' + action.pid
    //         },
    //         getActionDate: function (timestamp) {
    //             return moment(timestamp*1000).format('DD/MM/YYYY')
    //         },
    //         getActionColor: function (action) {
    //             let color_class = "";
    //             if (['HA', 'BR', 'HR'].includes(action.action)){
    //                 color_class = 'harvest';
    //             } else if (action.action === 'BG') {
    //                 color_class = 'sac';
    //             } else if (['CR', 'TR', 'LR', 'IN'].includes(action.action)) {
    //                 color_class = 'lot';
    //             }
    //             return color_class
    //         },
    //         getPackages: function (type, args = "", search = false) {
    //             if (!search) {
    //                 this.loading = true;
    //             }
    //             let url = '/entities/packages/?type=' + type;
    //             if (args.length > 0) {
    //                 url += args
    //             }
    //             this.$http.get(url).then(function (response) {
    //                 this.packages = response.data.results;
    //                 console.log(response.data)
    //                 this.opened_package = '';
    //                 this.loading = false;
    //             }).catch(function (err) {
    //                 this.loading = false;
    //                 this.opened_package = '';
    //                 console.log(err);
    //             })
    //         },
    //         showPackages: function (type) {
    //             this.setActiveAction('tracability', 'Tracability');
    //             this.active_package_type = type;
    //             this.package_keyword = "";
    //             this.getPackages(type)
    //         },
    //         getPackageDetails: function (id) {
    //             this.loading = true;
    //             let url = "/entities/packages/" + id + "/get_package_details/";
    //             this.$http.get(url).then(function (response){
    //                     this.package_properties = response.data;
    //                     this.opened_package = response.data.id;
    //                     this.loading = false;
    //                 }).catch(function(err) {
    //                     this.loading = false;
    //                     console.log(err);
    //                 })
    //         },
    //         getPropertyKey: function (val) {
    //             return Object.keys(val)[0]
    //         },
    //         getPropertyValue: function (val) {
    //             return val[Object.keys(val)[0]]
    //         },
    //         hideDetails: function () {
    //             this.opened_package = ''
    //         },
    //         getPackageChain: function (id) {
    //             this.loading = true;
    //             this.opened_package = '';
    //             this.active_element = 'package_chain';
    //             this.active_subelement = 'package_chain';
    //             let url = "/entities/packages/" + id + "/get_package_chain/";
    //             this.$http.get(url).then(function (response){
    //                     this.chain_list = response.data;
    //                     this.loading = false;
    //                 }).catch(function(err) {
    //                     this.loading = false;
    //                     console.log(err);
    //                 })
    //         },
    //         getMap: function() {
    //             this.loading = true;
    //             this.active_element = 'map_chain';
    //             this.active_subelement = 'map_chain';
    //             let chain_list = this.chain_list;
    //             let default_position = this.chain_list[0].location.split(", ");
    //             default_position[0] = parseFloat(default_position[0]);
    //             default_position[1] = parseFloat(default_position[1]);
    //             setTimeout(function (){
    //                 var mymap = L.map('mapid').setView(default_position, 8);
    //                 L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1Ijoic2NoZXJub3YiLCJhIjoiY2s1MmVubXZuMDdwejNtcW5wY3lkMnZsZyJ9.I_3cxb5zDMf6ahWoq8Js6w', {
    //                     attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    //                     maxZoom: 18,
    //                     id: 'mapbox/streets-v11',
    //                     accessToken: 'pk.eyJ1Ijoic2NoZXJub3YiLCJhIjoiY2s1MmVubXZuMDdwejNtcW5wY3lkMnZsZyJ9.I_3cxb5zDMf6ahWoq8Js6w'
    //                 }).addTo(mymap);
    //                 var harvestIcon = L.icon({
    //                     iconUrl: '/static/img/harvest_map_icon.png',
    //                     iconSize: [40, 40],
    //                 });
    //                 var sacIcon = L.icon({
    //                     iconUrl: '/static/img/sac_map_icon.png',
    //                     iconSize: [40, 40],
    //                 });
    //                 var lotIcon = L.icon({
    //                     iconUrl: '/static/img/lot_map_icon.png',
    //                     iconSize: [40, 40],
    //                 });
    //                 var mapChain = {};
    //                 var locations = [];
    //                 chain_list.forEach(function (item) {
    //                     var location = item.location.split(", ");
    //                     location[0] = parseFloat(location[0]);
    //                     location[1] = parseFloat(location[1]);
    //                     locations.push(location);
    //                     var marker_name = item.action_short_name;
    //                     var current_icon = harvestIcon;
    //                     if (['CR', 'TR', 'LR', 'IN'].includes(marker_name)){
    //                         current_icon = lotIcon
    //                     } else if (marker_name === 'BG') {
    //                         current_icon = sacIcon
    //                     }
    //                     mapChain[marker_name] = L.marker(location, {icon: current_icon}).bindPopup(item.action_name).openPopup();
    //                     mapChain[marker_name].addTo(mymap);
    //                 });
    //                 var polyline = L.polyline(locations, {color: 'red'}).addTo(mymap);
    //             }, 1000);
    //             this.loading = false;
    //         },
    //         showCalendar: function () {
    //             this.setActiveAction('calendar', 'Calendar');
    //
    //         },
    //         showBlockchainExplorer: function () {
    //             // this.getTransactions();
    //             this.setActiveAction('blockchain_explorer');
    //
    //         },
    //         getTransactions: function (query) {
    //             var url;
    //             if (query === undefined)
    //                 url = `/blockchain/transactions/?limit=${this.transactions_per_page}`;
    //             else
    //                 url = `/blockchain/transactions/?${query}`;
    //             this.$http.get(url)
    //                 .then(function (response) {
    //                     this.transactions = response.body.data;
    //                     if (response.body.paging.next)
    //                         this.transactions_next_page = response.body.paging.next.split('?')[1];
    //                     if (response.body.paging.previous)
    //                         this.transactions_prev_page = response.body.paging.previous.split('?')[1];
    //                     this.showTransactionFirstPage = response.body.paging.start !== null;
    //                 })
    //         },
    //         getTransactionDetails: function (head) {
    //             this.opened_transaction = head;
    //         },
    //         hideTransactionDetails: function () {
    //             this.opened_transaction = ''
    //         },
    //         openMap: function () {
    //             // this.active_subelement = 'tracability_maps';
    //             // // window.open('http://etclab.org/websig/lizmap/www/index.php/view/map/?repository=rci&project=PROJET_PRM&layers=0BTTFFFTTTFTTTTTTTTTTTTTTTTTTTTTTT&bbox=-764617.961462%2C570930.920373%2C-186754.027707%2C753768.292006&crs=EPSG%3A3857', '_blank');
    //             // url = "https://iframe-beta.gaiachain.io/websig/lizmap/www/index.php/view/map/?repository=rci&project=PROJET_PRM&layers=0BTTFFFTTTFTTTTTTTTTTTTTTTTTTTTTTT&bbox=-764617.961462%2C570930.920373%2C-186754.027707%2C753768.292006&crs=EPSG%3A3857";
    //             // this.$http.get(url).then(function (response){
    //             //         console.log()
    //             //         this.loading = false;
    //             //     }).catch(function(err) {
    //             //         this.loading = false;
    //             //         console.log(err);
    //             //     })
    //         }
    //     },
    router,
    i18n
}).$mount('#dashboard-main');
