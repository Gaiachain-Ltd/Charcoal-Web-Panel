let Replantation = Vue.component('replantation', {
    template: `
        <div class="start-content">
            <div class="nav-search">
                <ul class="nav nav-tabs">
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" :class="{ 'active': activeTab == 'list' } " data-toggle="dropdown" href="#" 
                           role="button" aria-haspopup="true" aria-expanded="false">[[ selectedYear ]]</a>
                        <div class="dropdown-menu">
                            <a class="dropdown-item" href="#" v-for="year in yearsRange" :key="year"
                               @click.prevent="setYear(year)">[[ year ]] <i class="current" v-if="year === selectedYear"></i></a>
                        </div>
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
                            <a class="nav-link"
                               @click.prevent="previousYear" href="#">&lt;</a>
                        </li>
                        <li class="nav-item m-0" v-if="selectedYear < todayYear">
                            <a class="nav-link"
                               @click.prevent="nextYear" href="#">&gt;</a>
                        </li>
                    </ul>
                </div>
            </div>
            <div class="content-data" v-if="activeTab == 'list'">
                <div class="replantation-data">
                    <div class="replantations">
                        <div class="replantation" v-for="replantation in replantations" :key="replantation.id">
                            <div class="replantation-pid">
                                <div class="pid">
                                    <span>[[ replantation.pid ]]</span>
                                </div>
                                <div class="replantation-ending-date">
                                    <span>[[ replantation.ending_date | timestampToDateTime ]] 
                                        <div class="blockchain-details" 
                                             @click="openModal(replantation.pid, replantation.blockchain_details)" 
                                             v-if="objectNotEmpty(replantation.blockchain_details)">
                                        </div>
                                    </span>
                                </div>
                            </div>
                            <div class="replantation-details">
                                <div class="replantation-entity">
                                    <div>
                                        <span class="description">[[ $t('trees_planted') ]]: [[ replantation.trees_planted ]]</span>
                                        <span class="timestamp">[[ replantation.trees_planted_dates[0] | timestampToDate ]] - [[ replantation.trees_planted_dates[1] | timestampToDate ]]</span>
                                    </div>
                                    <div>
                                        <span class="description">[[ $t('trees_cut') ]]: [[ replantation.trees_cut ]]</span>
                                        <span class="timestamp">[[ replantation.trees_cut_dates[0] | timestampToDate ]] - [[ replantation.trees_cut_dates[1] | timestampToDate ]]</span>
                                    </div>
                                </div>
                                <div class="replantation-bar">
                                    <div class="trees-planted" v-bind:style='{ width: replantation.trees_planted_percent + "%" }'></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="content-data" v-if="activeTab == 'map'">
                <package-map v-bind:package-id="0" v-bind:is-replantation="true" 
                             v-bind:show-map-details="false" v-bind:replantations="replantations"></package-map>
            </div>
            <blockchain-transaction-modal v-if="isModalOpen" @close="closeModal()" v-bind:action="$t('replantation')" 
                                          v-bind:package-pid="modalPid" package-type="harvest" 
                                          v-bind:transaction="modalTransaction">
            </blockchain-transaction-modal>
        </div>`,
    delimiters: ['[[', ']]'],
    data() {
        return {
            todayYear: null,
            selectedYear: null,
            replantations: [],
            yearsRange: [],
            activeTab: 'list',
            isModalOpen: false,
            modalTransaction: {},
            modalPid: ''
        }
    },
    created() {
        this.todayYear = new Date().getFullYear();
        this.selectedYear = this.todayYear;
        this.yearsRange = this.generateYearsRange();
    },
    mounted: function () {
        document.getElementById('current-page-name').innerHTML = this.$t('replantation')
    },
    watch: {
        selectedYear() {
            this.updateData();
        }
    },
    methods: {
        objectNotEmpty: function (obj) {
            return Object.keys(obj).length !== 0
        },
        openModal: function(pid, transaction) {
            this.modalPid = pid;
            this.modalTransaction = transaction;
            this.isModalOpen = true;
        },
        closeModal: function() {
            this.isModalOpen = false;
            this.modalPid = '';
            this.modalTransaction = {};
        },
        showMap: function (type) {
            this.activeTab = 'map';
        },
        nextYear() {
            this.selectedYear += 1;
        },
        previousYear() {
            this.selectedYear -= 1;
        },
        setYear(year) {
            this.selectedYear = year;
            this.showReplantations();
        },
        generateYearsRange() {
            let arr = [];
            let currentYear = this.todayYear;
            for (let i = currentYear; i >= currentYear - 5; i -= 1) {
                arr.push(i);
            }
            return arr;
        },
        updateData: function () {
            this.$root.$data.loading = true;
            let params = {'year': this.selectedYear};
            let url = '/entities/replantation/?' + new URLSearchParams(params).toString();
            this.$http.get(url).then(function (response) {
                this.replantations = response.data.results;
                this.$root.$data.loading = false;
            }).catch(function (err) {
                this.$root.$data.loading = false;
                console.log(err);
            })
        },
        showReplantations: function () {
            this.activeTab = 'list';
        },
    },
    filters: {
        timestampToDateTime(val) {
            return dateFns.format(new Date(val * 1000), 'DD/MM/YYYY HH:mm');
        },
        timestampToDate(val) {
            return dateFns.format(new Date(val * 1000), 'DD/MM/YYYY');
        }
    },
});