let PackageDetails = Vue.component('package-details', {
    template: `
        <div :class="[ 'start-content', 'package-details', package.type_display ]">
            <div class="nav-search">
                <ul class="nav nav-tabs">
                    <li class="nav-item">
                        <a class="nav-link"
                           :class="{ 'active': activeTab == 'package_details' } "
                           @click.prevent="showPackageDetails()" href="#">[[ package.pid ]]</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link"
                           :class="{ 'active': activeTab == 'map' } "
                           @click.prevent="showMap()" href="#">[[ $t("map") ]] <i class="gps-pin-icon"></i></a>
                    </li>
                </ul>
                <div class="nav-tabs-right-actions">
                    <ul class="nav nav-tabs float-right">
                        <li class="nav-item m-0">
                            <a class="nav-link transport"
                               @click.prevent="$router.back()" href="#">[[ $t("back") ]]</a>
                        </li>
                    </ul>
                </div>
            </div>
            <div v-if="activeTab == 'package_details'">
                <div class="content-data" v-if="package.type_display === 'plot'">
                    <div class="entity" v-if="objectNotEmpty(loggingBeginning)">
                        <div class="entity-header">
                            <div class="entity-action">[[ loggingBeginning.entity.action_display ]]</div>
                            <div class="entity-timestamp">[[ loggingBeginning.entity.timestamp | timestampToDateTime ]] 
                                <div class="blockchain-details" 
                                     @click="openModal(loggingBeginning.entity.action_display, loggingBeginning.entity.blockchain_details)" 
                                     v-if="objectNotEmpty(loggingBeginning.entity.blockchain_details)">
                                 </div>
                            </div>
                        </div>
                        <div class="entity-details">
                            <div class="entity-property">
                                <div class="entity-property-name">[[ $t('beginning_date') ]]</div>
                                <div class="entity-property-value">[[ loggingBeginning.beginning_date | timestampToDate ]]</div>
                            </div>
                            <div class="entity-property">
                                <div class="entity-property-name">[[ $t('gps_coordinates') ]]</div>
                                <div class="entity-property-value">[[ loggingBeginning.entity.location_display ]]</div>
                            </div>
                            <div class="entity-property">
                                <div class="entity-property-name">[[ $t('user_id') ]]</div>
                                <div class="entity-property-value">[[ loggingBeginning.entity.user_code ]]</div>
                            </div>
                            <div class="entity-property">
                                <div class="entity-property-name">[[ $t('village') ]]</div>
                                <div class="entity-property-value">[[ loggingBeginning.village ]]</div>
                            </div>
                            <div class="entity-property">
                                <div class="entity-property-name">[[ $t('tree_specie') ]]</div>
                                <div class="entity-property-value">[[ loggingBeginning.tree_specie ]]</div>
                            </div>
                        </div>
                    </div>
                    <div class="entity" v-if="objectNotEmpty(loggingEnding)">
                        <div class="entity-header">
                            <div class="entity-action">[[ loggingEnding.entity.action_display ]]</div>
                            <div class="entity-timestamp">[[ loggingEnding.entity.timestamp | timestampToDateTime ]] 
                                <div class="blockchain-details" 
                                     @click="openModal(loggingEnding.entity.action_display, loggingEnding.entity.blockchain_details)" 
                                     v-if="objectNotEmpty(loggingEnding.entity.blockchain_details)">
                                 </div>
                            </div>
                        </div>
                        <div class="entity-details">
                            <div class="entity-property">
                                <div class="entity-property-name">[[ $t('ending_date') ]]</div>
                                <div class="entity-property-value">[[ loggingEnding.ending_date | timestampToDate ]]</div>
                            </div>
                            <div class="entity-property">
                                <div class="entity-property-name">[[ $t('gps_coordinates') ]]</div>
                                <div class="entity-property-value">[[ loggingEnding.entity.location_display ]]</div>
                            </div>
                            <div class="entity-property">
                                <div class="entity-property-name">[[ $t('number_of_trees_cut') ]]</div>
                                <div class="entity-property-value">[[ loggingEnding.number_of_trees ]]</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-if="package.type_display === 'harvest'">
                    <div class="nav-search nav-sub">
                        <ul class="nav nav-tabs">
                            <li class="nav-item" v-for="oven in ovens" :key="'oven_' + oven.id">
                                <a class="nav-link"
                                   :class="{ 'active': activeSubTab == 'oven_' + oven.oven_id } "
                                   @click.prevent="showSubTab('oven_' + oven.oven_id)" href="#">[[ $t('oven') ]] [[ oven.oven_id ]]</a>
                            </li>
                        </ul>
                    </div>
                    <div class="content-data" v-for="oven in ovens" v-if="activeSubTab == 'oven_' + oven.oven_id"
                         :key="'oven_' + oven.id">
                        <div class="entity" v-if="objectNotEmpty(oven.carbonization_beginning)">
                            <div class="entity-header">
                                <div class="entity-action">[[ oven.carbonization_beginning.entity.action_display ]]</div>
                                <div class="entity-timestamp">[[ oven.carbonization_beginning.entity.timestamp | timestampToDateTime ]] 
                                    <div class="blockchain-details" 
                                         @click="openModal(oven.carbonization_beginning.entity.action_display, oven.carbonization_beginning.entity.blockchain_details)" 
                                         v-if="objectNotEmpty(oven.carbonization_beginning.entity.blockchain_details)">
                                    </div>
                                </div>
                            </div>
                            <div class="entity-details">
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ $t('beginning_date') ]]</div>
                                    <div class="entity-property-value">[[ oven.carbonization_beginning.beginning_date | timestampToDate ]]</div>
                                </div>
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ $t('gps_coordinates') ]]</div>
                                    <div class="entity-property-value">[[ oven.carbonization_beginning.entity.location_display ]]</div>
                                </div>
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ $t('carbonizer_id') ]]</div>
                                    <div class="entity-property-value">[[ oven.carbonization_beginning.entity.user_code ]]</div>
                                </div>
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ $t('oven_type') ]]</div>
                                    <div class="entity-property-value">[[ oven.carbonization_beginning.oven_type_display ]]</div>
                                </div>
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ $t('oven_measurements') ]]</div>
                                    <div class="entity-property-value" v-if="oven.carbonization_beginning.oven_measurements.oven_height2">[[ $t('height') ]]: [[ oven.carbonization_beginning.oven_measurements.oven_height ]]m  [[ $t('height') ]] 2: [[ oven.carbonization_beginning.oven_measurements.oven_height2 ]]m  [[ $t('length') ]]: [[ oven.carbonization_beginning.oven_measurements.oven_length ]]m  [[ $t('width') ]]: [[ oven.carbonization_beginning.oven_measurements.oven_width ]]m</div>
                                    <div class="entity-property-value" v-else>[[ $t('height') ]]: [[ oven.carbonization_beginning.oven_measurements.oven_height ]]m  [[ $t('length') ]]: [[ oven.carbonization_beginning.oven_measurements.oven_length ]]m  [[ $t('width') ]]: [[ oven.carbonization_beginning.oven_measurements.oven_width ]]m</div>
                                </div>
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ $t('timber_volume') ]]</div>
                                    <div class="entity-property-value">[[ oven.carbonization_beginning.oven_volume ]] m3</div>
                                </div>
                            </div>
                        </div>
                        <div class="entity" v-if="objectNotEmpty(oven.carbonization_ending)">
                            <div class="entity-header">
                                <div class="entity-action">[[ oven.carbonization_ending.entity.action_display ]]</div>
                                <div class="entity-timestamp">[[ oven.carbonization_ending.entity.timestamp | timestampToDateTime ]] 
                                    <div class="blockchain-details" 
                                         @click="openModal(oven.carbonization_ending.entity.action_display, oven.carbonization_ending.entity.blockchain_details)" 
                                         v-if="objectNotEmpty(oven.carbonization_ending.entity.blockchain_details)">
                                    </div>
                                </div>
                            </div>
                            <div class="entity-details">
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ $t('ending_date') ]]</div>
                                    <div class="entity-property-value">[[ oven.carbonization_ending.entity.timestamp | timestampToDate ]]</div>
                                </div>
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ $t('gps_coordinates') ]]</div>
                                    <div class="entity-property-value">[[ oven.carbonization_ending.entity.location_display ]]</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-if="package.type_display === 'transport'">
                    <div class="nav-search nav-sub">
                        <ul class="nav nav-tabs">
                            <li class="nav-item">
                                <a class="nav-link" v-if="objectNotEmpty(loadingTransport)"
                                   :class="{ 'active': activeSubTab == 'loading_transport' } "
                                   @click.prevent="showSubTab('loading_transport')" href="#">[[ $t("loading_transport") ]]</a>
                            </li>
                            <li class="nav-item" v-for="localReception in localReceptions">
                                <a class="nav-link"
                                   :class="{ 'active': activeSubTab == 'localReception' + localReception.entity.id } "
                                   @click.prevent="showSubTab('localReception' + localReception.entity.id)" 
                                   href="#">[[ $t("local_reception") ]]</a>
                            </li>
                            <li class="nav-item" v-if="objectNotEmpty(reception)">
                                <a class="nav-link"
                                   :class="{ 'active': activeSubTab == 'reception' } "
                                   @click.prevent="showSubTab('reception')" href="#">[[ $t("reception") ]]</a>
                            </li>
                        </ul>
                    </div>
                    <div class="content-data" v-if="activeSubTab == 'loading_transport' && objectNotEmpty(loadingTransport)">
                        <div class="entity">
                            <div class="entity-header">
                                <div class="entity-action">[[ loadingTransport.entity.action_display ]]</div>
                                <div class="entity-timestamp">[[ loadingTransport.entity.timestamp | timestampToDateTime ]] 
                                    <div class="blockchain-details" 
                                         @click="openModal(loadingTransport.entity.action_display, loadingTransport.entity.blockchain_details)" 
                                         v-if="objectNotEmpty(loadingTransport.entity.blockchain_details)">
                                    </div>
                                </div>
                            </div>
                            <div class="entity-details">
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ $t('plate_number') ]]</div>
                                    <div class="entity-property-value">[[ loadingTransport.plate_number ]]</div>
                                </div>
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ $t('loading_date') ]]</div>
                                    <div class="entity-property-value">[[ loadingTransport.loading_date | timestampToDate ]]</div>
                                </div>
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ $t('scanned_bags') ]]</div>
                                    <div class="entity-property-value">[[ loadingTransport.scanned_bags ]]</div>
                                </div>
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ $t('gps_coordinates') ]]</div>
                                    <div class="entity-property-value">[[ loadingTransport.entity.location_display ]]</div>
                                </div>
                            </div>
                        </div>
                        <div class="entity">
                            <div class="entity-header">
                                <div class="entity-action">[[ $t('scanned_bags') ]] ([[ loadingTransport.scanned_bags ]])</div>
                            </div>
                            <div class="entity-details" v-for="bag in loadingTransport.bags" :key="'bag_' + bag.id">
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ bag.pid ]]</div>
                                    <div class="entity-property-value">[[ bag.qr_code ]]</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div v-for="reception in localReceptions">
                        <div class="content-data" v-if="activeSubTab == 'localReception' + reception.entity.id">
                            <div class="entity">
                                <div class="entity-header">
                                    <div class="entity-action">[[ reception.entity.action_display ]]</div>
                                    <div class="entity-timestamp">[[ reception.entity.timestamp | timestampToDateTime ]] 
                                        <div class="blockchain-details" 
                                             @click="openModal(reception.entity.action_display, reception.entity.blockchain_details)" 
                                             v-if="objectNotEmpty(reception.entity.blockchain_details)">
                                        </div>
                                    </div>
                                </div>
                                <div class="entity-details">
                                    <div class="entity-property">
                                        <div class="entity-property-name">[[ $t('plate_number') ]]</div>
                                        <div class="entity-property-value">[[ loadingTransport.plate_number ]]</div>
                                    </div>
                                    <div class="entity-property">
                                        <div class="entity-property-name">[[ $t('reception_date') ]]</div>
                                        <div class="entity-property-value">[[ reception.reception_date | timestampToDate ]]</div>
                                    </div>
                                    <div class="entity-property">
                                        <div class="entity-property-name">[[ $t('scanned_bags') ]]</div>
                                        <div class="entity-property-value">[[ reception.scanned_bags ]]</div>
                                    </div>
                                    <div class="entity-property">
                                        <div class="entity-property-name">[[ $t('gps_coordinates') ]]</div>
                                        <div class="entity-property-value">[[ reception.entity.location_display ]]</div>
                                    </div>
                                </div>
                            </div>
                            <div class="entity">
                                <div class="entity-header">
                                    <div class="entity-action">[[ $t('scanned_bags') ]] ([[ reception.scanned_bags ]])</div>
                                </div>
                                <div class="entity-details" v-for="bag in reception.bags" :key="'reception_bag_' + bag.id">
                                    <div class="entity-property">
                                        <div class="entity-property-name">[[ bag.pid ]]</div>
                                        <div class="entity-property-value">[[ bag.qr_code ]]</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="content-data" v-if="activeSubTab == 'reception' && objectNotEmpty(reception)">
                        <div class="entity">
                            <div class="entity-header">
                                <div class="entity-action">[[ reception.entity.action_display ]]</div>
                                <div class="entity-timestamp">[[ reception.entity.timestamp | timestampToDateTime ]] 
                                    <div class="blockchain-details" 
                                         @click="openModal(reception.entity.action_display, reception.entity.blockchain_details)" 
                                         v-if="objectNotEmpty(reception.entity.blockchain_details)">
                                    </div>
                                </div>
                            </div>
                            <div class="entity-details">
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ $t('plate_number') ]]</div>
                                    <div class="entity-property-value">[[ loadingTransport.plate_number ]]</div>
                                </div>
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ $t('reception_date') ]]</div>
                                    <div class="entity-property-value">[[ reception.reception_date | timestampToDate ]]</div>
                                </div>
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ $t('total_bags_sold') ]]</div>
                                    <div class="entity-property-value">[[ reception.total_bags_sold ]]</div>
                                </div>
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ $t('scanned_bags') ]]</div>
                                    <div class="entity-property-value">[[ reception.scanned_bags ]]</div>
                                    <div class="entity-property-icon-warning" v-if="reception.total_bags != loadingTransport.scanned_bags"></div>
                                </div>
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ $t('gps_coordinates') ]]</div>
                                    <div class="entity-property-value">[[ reception.entity.location_display ]]</div>
                                </div>
                                <div class="row m-0">
                                    <div class="entity-property col px-0">
                                        <div class="entity-property-name">[[ $t('documents') ]]</div>
                                    </div>
                                    <div class="entity-property col px-0">
                                        <div class="entity-property-name">[[ $t('receipt') ]]</div>
                                    </div>
                                </div>
                                <div class="row m-0">
                                    <div class="entity-property no-border col px-0">
                                        <div class="entity-property-name" 
                                             v-for="(image, index) in reception.documents_photos" 
                                             :key="'document_' + index">
                                            <a target="_blank" :href="image.image">
                                                <img width="100%" :src="image.image" alt="">
                                            </a>
                                        </div>
                                    </div>
                                    <div class="entity-property no-border col px-0">
                                        <div class="entity-property-name" 
                                             v-for="(image, index) in reception.receipt_photos"
                                             :key="'receipt_' + index">
                                            <a target="_blank" :href="image.image">
                                                <img width="100%" :src="image.image" alt="">
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="entity">
                            <div class="entity-header">
                                <div class="entity-action">[[ $t('scanned_bags') ]] ([[ reception.scanned_bags ]])</div>
                            </div>
                            <div class="entity-details" v-for="bag in reception.bags" :key="'reception_bag_' + bag.id">
                                <div class="entity-property">
                                    <div class="entity-property-name">[[ bag.pid ]]</div>
                                    <div class="entity-property-value">[[ bag.qr_code ]]</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div v-if="activeTab == 'map'">
                <package-map v-bind:package-id="package.id"></package-map>
            </div>
            <blockchain-transaction-modal v-if="isModalOpen" @close="closeModal()" v-bind:action="modalAction" 
                                          v-bind:package-pid="package.pid" v-bind:package-type="package.type_display" 
                                          v-bind:transaction="modalTransaction">
            </blockchain-transaction-modal>
        </div>`,
    delimiters: ['[[', ']]'],
    data() {
        return {
            activeTab: '',
            activeSubTab: '',
            package: {},
            loggingBeginning: {},
            loggingEnding: {},
            loadingTransport: {},
            reception: {},
            localReceptions: {},
            ovens: [],
            isModalOpen: false,
            modalAction: '',
            modalTransaction: {}
        }
    },
    mounted: function () {
        this.showPackageDetails();
    },
    methods: {
        openModal: function(action, transaction) {
            this.modalAction = action;
            this.modalTransaction = transaction;
            this.isModalOpen = true;
        },
        closeModal: function() {
            this.isModalOpen = false;
            this.modalAction = '';
            this.modalTransaction = {};
        },
        objectNotEmpty: function (obj) {
            return Object.keys(obj).length !== 0
        },
        getPackage: function (type, args = "", search = false) {
            this.$root.$data.loading = true;
            let url = `/api/v1/entities/packages/${this.$route.params.id}/get_package_details/`;
            this.$http.get(url).then(function (response) {
                this.package = response.data;
                document.getElementById('current-page-name').innerHTML = this.package.type_display.toUpperCase() + ' ID ' + this.$t('details')
                this.loggingBeginning = this.package.properties.logging_beginning;
                this.loggingEnding = this.package.properties.logging_ending;
                this.loadingTransport = this.package.properties.loading_transport;
                this.reception = this.package.properties.reception;
                this.localReceptions = this.package.properties.local_receptions;
                this.ovens = this.package.properties.ovens;
                if (this.package.type_display == 'transport') {
                    this.activeSubTab = 'loading_transport'
                } else if (this.package.type_display == 'harvest') {
                    this.activeSubTab = `oven_${this.ovens[0].oven_id}`
                }
                this.$root.$data.loading = false;
            }).catch(function (err) {
                this.$root.$data.loading = false;
                console.log(err);
            })
        },
        showPackageDetails: function (type) {
            this.$root.$data.loading = true;
            this.activeTab = 'package_details';
            this.getPackage(type)
        },
        showMap: function () {
            this.activeTab = 'map';
        },
        showSubTab: function (tab) {
            this.activeSubTab = tab;
        }
    },
    filters: {
        timestampToDateTime(val) {
            return dateFns.format(new Date(val * 1000), 'YYYY-MM-DD HH:mm');
        },
        timestampToDate(val) {
            if (val)
                return dateFns.format(new Date(val * 1000), 'DD/MM/YYYY');
            return ''
        }
    },
});