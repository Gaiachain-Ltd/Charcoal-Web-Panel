let Replantation = Vue.component('replantation', {
    template: `
        <div class="start-content">
            <div class="nav-search">
                <ul class="nav nav-tabs">
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" :class="{ 'active': activeTab == 'list' } " data-toggle="dropdown" href="#" 
                           role="button" aria-haspopup="true" aria-expanded="false">[[ selectedYear ]]</a>
                        <div class="dropdown-menu">
                            <a class="dropdown-item" href="#" v-for="year in yearsRange"
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
            <div class="content-data">
                <div class="replantation-data">
                    <div class="replantations">
                        <div class="replantation" v-for="replantation in replantations">
                            <div class="replantation-pid">
                                <div class="pid">
                                    <span>[[ replantation.pid ]]</span>
                                </div>
                                <div class="replantation-ending-date">
                                    <span>[[ replantation.ending_date_display ]]</span>
                                </div>
                            </div>
                            <div class="replantation-details">
                                <div class="replantation-entity">
                                    <div>
                                        <span class="description">[[ $t('trees_planted') ]]: [[ replantation.trees_planted ]]</span>
                                        <span class="timestamp">[[ replantation.trees_planted_dates_display ]]</span>
                                    </div>
                                    <div>
                                        <span class="description">[[ $t('trees_cut') ]]: [[ replantation.trees_cut ]]</span>
                                        <span class="timestamp">[[ replantation.trees_cut_dates_display ]]</span>
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
        </div>`,
    delimiters: ['[[', ']]'],
    data() {
        return {
            todayYear: null,
            selectedYear: null,
            replantations: [],
            yearsRange: [],
            activeTab: 'list'
        }
    },
    created() {
        this.todayYear = new Date().getFullYear();
        this.selectedYear = this.todayYear;
        this.yearsRange = this.generateYearsRange();
    },
    mounted: function () {
        this.showReplantations();
        document.getElementById('current-page-name').innerHTML = this.$t('replantation')
    },
    methods: {
        showMap: function (type) {
            // this.$root.$data.loading = true;
            this.activeTab = 'map';
            // this.getPackages(type)
        },
        nextYear() {
            this.selectedYear += 1;
            this.showReplantations();
        },
        previousYear() {
            this.selectedYear -= 1;
            this.showReplantations();
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
        showReplantations: function () {
            this.$root.$data.loading = true;
            this.activeTab = 'list';
            let params = {'year': this.selectedYear};
            let url = '/entities/replantation/?' + new URLSearchParams(params).toString();
            this.$http.get(url).then(function (response) {
                this.replantations = response.data.results;
                console.log(this.replantations);
                this.$root.$data.loading = false;
            }).catch(function (err) {
                this.$root.$data.loading = false;
                console.log(err);
            })
        },
    }
});