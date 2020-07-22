
let Settings = Vue.component('settings', {
    template: `
        <div class="start-content settings">
            <div class="nav-search">
                <ul class="nav nav-tabs">
                    <li class="nav-item">
                        <a class="nav-link all"
                           :class="{ 'active': activeTab == 'logging' } "
                           @click.prevent="showTab('logging')" href="#">[[ $t("logging") ]]</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link plot"
                           :class="{ 'active': activeTab == 'carbonization' } "
                           @click.prevent="showTab('carbonization')" href="#">[[ $t("carbonization") ]]</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link harvest"
                           :class="{ 'active': activeTab == 'transport' } "
                           @click.prevent="showTab('transport')" href="#">[[ $t("loading_transport") ]]</a>
                    </li>
                </ul>
            </div>
            <div class="content-data">
                <div class="settings-tab-details" v-show="activeTab == 'logging'">
                    <additional-data-simple title="parcel_list" placeholder="code" data-service-name="ParcelDataService"
                                            v-bind:initial-objects="parcels" v-if="dataLoaded">
                    </additional-data-simple>
                    <additional-data-simple title="tree_species_list" data-service-name="TreeSpecieDataService" 
                                            v-bind:initial-objects="treeSpecies" v-if="dataLoaded">
                    </additional-data-simple>
                    <additional-data-simple title="village_list" data-service-name="VillageDataService" 
                                            v-bind:initial-objects="villages" v-if="dataLoaded">
                    </additional-data-simple>
                </div>
                <div class="settings-tab-details" v-show="activeTab == 'carbonization'">
                    <oven-type v-bind:initial-objects="ovenTypes" v-if="dataLoaded"></oven-type>
                </div>
                <div class="settings-tab-details" v-show="activeTab == 'transport'">
                    <additional-data-simple title="delivery_destination" data-service-name="DestinationDataService" 
                                            v-bind:initial-objects="destinations" v-if="dataLoaded">
                    </additional-data-simple>
                </div>
                
            </div>
        </div>
        `,
    delimiters: ['[[', ']]'],
    data() {
        return {
            activeTab: '',
            parcels: [],
            villages: [],
            treeSpecies: [],
            ovenTypes: [],
            destinations: [],
            dataLoaded: false,
        };
    },
    watch: {
    },
    mounted: function () {
        document.getElementById('current-page-name').innerHTML = this.$t('settings');
        this.getData();
        this.showTab('logging')
    },
    methods: {
        getData() {
            AdditionalDataDataService.getAll()
                .then(response => {
                    this.parcels = response.data.parcels;
                    this.villages = response.data.villages;
                    this.treeSpecies = response.data.tree_species;
                    this.ovenTypes = response.data.oven_types;
                    this.destinations = response.data.destinations;
                    this.$root.$data.loading = false;
                    this.dataLoaded = true;
                })
                .catch(e => {
                    this.$root.$data.loading = false;
                    console.log(e)
                });
        },
        showTab(tab) {
            this.activeTab = tab;
        },
    },
});