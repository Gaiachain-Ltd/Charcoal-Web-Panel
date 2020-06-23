let Packages = Vue.component('packages', {
    template: `
        <div class="start-content">
            <div class="nav-search">
                <ul class="nav nav-tabs">
                    <li class="nav-item">
                        <a class="nav-link all"
                           :class="{ 'active': active_package_type == 'all' } "
                           @click.prevent="showPackages('all')" href="#">[[ $t("package.types.all") ]]</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link plot"
                           :class="{ 'active': active_package_type == 'plt' } "
                           @click.prevent="showPackages('plt')" href="#">[[ $t("package.types.plot") ]]</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link harvest"
                           :class="{ 'active': active_package_type == 'har' } "
                           @click.prevent="showPackages('har')" href="#">[[ $t("package.types.harvest") ]]</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link transport"
                           :class="{ 'active': active_package_type == 'trk' } "
                           @click.prevent="showPackages('trk')" href="#">[[ $t("package.types.transport") ]]</a>
                    </li>
                </ul>
    
                <div class="nav-tabs-right-actions" v-if="showSearch">
                    <i class="search-icon"></i>
                    <input type="text" v-model="keyword" :placeholder="$t('search') + '...'"/>
                </div>
            </div>
            <div class="content-data">
                <div class="packages-data">
                    <div class="packages">
                        <div class="package" v-for="package in packages" :key="'package_' + package.id">
                            <div class="package-pid">
                                <div class="pid">
                                    <router-link :to="{ path: '/traceability/' + package.id }"
                                                 v-slot="{ href, route, navigate, isActive, isExactActive }">
                                        <span @click="navigate" :class="[package.type_display]">[[ package.pid ]]</span>
                                    </router-link>
                                </div>
                            </div>
                            <div class="package-details">
                                <div class="package-entity" v-for="entity in package.entities" :key="'entity_' + entity.id">
                                    <div>
                                        <span class="description">[[ entity.description ]]</span>
                                        <span class="timestamp" v-if="showTimezone">[[ entity.timestamp_display ]]<span class="timezone"> [[ entity.timezone ]]</span></span>
                                        <span class="timestamp" v-else>[[ entity.timestamp | timestampToDateTime ]]</span>
                                    </div>
                                    <hr>
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
            keyword: '',
            active_package_type: '',
            packages: [],
        }
    },
    props: {
        date: {
            type: Date,
        },
        showSearch: {
            type: Boolean,
            default: true
        },
        showTimezone: {
            type: Boolean,
            default: true
        }
    },
    watch: {
        keyword: function (val) {
            let args = val ? {keyword: val} : {};
            this.getPackages(this.active_package_type, args, true)
        },
        date: function (val) {
            this.getPackages(this.active_package_type)
        }
    },
    mounted: function () {
        this.showPackages('all');
        document.getElementById('current-page-name').innerHTML = this.$t('traceability')
    },
    methods: {
        getPackages: function (type, args = {}, search = false) {
            if (!search) {
                this.$root.$data.loading = true;
            }
            let params = {...{type: type}, ...args};
            if (this.date) {
                params = {...params, ...{
                    from_timestamp: dateFns.startOfDay(this.date).getTime() / 1000 | 0,
                    to_timestamp: dateFns.endOfDay(this.date).getTime() / 1000 | 0
                }}
            }
            let url = '/entities/packages/?' + new URLSearchParams(params).toString();
            this.$http.get(url).then(function (response) {
                this.packages = response.data.results;
                this.$root.$data.loading = false;
            }).catch(function (err) {
                this.$root.$data.loading = false;
                console.log(err);
            })
        },
        showPackages: function (type) {
            this.$root.$data.loading = true;
            this.active_package_type = type;
            this.keyword = "";
            this.getPackages(type)
        },
    },
    filters: {
        timestampToDateTime(val) {
            return dateFns.format(new Date(val * 1000), 'YYYY-MM-DD HH:mm');
        }
    },
});