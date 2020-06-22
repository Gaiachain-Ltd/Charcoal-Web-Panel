
let PackageMap = Vue.component('package-map', {
    template: `
        <div class="start-content map">
            <div class="content-data">
                <div class="actions-data col" id="map-wrapper">
                </div>
                <div class="actions-data col" v-if="showMapDetails">
                    <div class="map-details">
                        <div class="map-details-header">
                            <p>[[ $t('supply_chain') ]]</p>
                        </div>
                        <div class="calendar-details-packages">
                            <div class="packages-data">
                                <div class="packages">
                                    <div class="package" v-for="(package, key) in packages" v-bind:id="key">
                                        <div class="package-pid">
                                            <div class="pid">
                                                <span :class="[package.type_display]">[[ package.pid ]]</span>
                                            </div>
                                        </div>
                                        <div class="package-details">
                                            <div class="package-entity" v-for="entity in package.entities"
                                                 :key="key">
                                                <div>
                                                    <span class="description">[[ entity.description ]]</span>
                                                    <span class="timestamp">[[ entity.timestamp_display | trimTime ]]</span>
                                                </div>
                                                <hr>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `,
    delimiters: ['[[', ']]'],
    data() {
        return {
            packages: [],
            map: null,
        };
    },
    created() {
    },
    props: {
        packageId: {
            required: true,
            type: Number,
        },
        isReplantation: {
            required: false,
            type: Boolean,
        },
        showMapDetails: {
            required: false,
            type: Boolean,
            default: true
        },
        replantations: {
            required: false,
            type: Array
        }
    },
    computed: {
    },
    watch: {
        replantations() {
            this.getPackages()
        }
    },
    mounted: function () {
        this.getPackages();
    },
    methods: {
        getPackages: function () {
            if (this.isReplantation) {
                this.packages = this.replantations;
                this.loadMap();
            }
            else {
                this.$root.$data.loading = true;
                this.$http.get(`/entities/packages/${this.packageId}/get_package_chain/`).then(function (response) {
                    this.packages = response.data;
                    this.loadMap()
                }).catch(function (err) {
                    this.$root.$data.loading = false;
                    console.log(err);
                })
            }
        },
        loadMap: function () {
            let markers = [];
            let bounds = [];
            let defaultIcon = L.Icon.extend({
                    options: {
                        iconSize: [30, 41],
                        iconAnchor: [15, 41],
                        popupAnchor: [0, -38],
                        shadowSize: [41, 41],
                        shadowUrl: `${window.staticPrefix}img/marker-shadow.png`,
                        shadowAnchor: [13, 44]
                    }
                }),
                plotIcon = new defaultIcon({
                    iconUrl: `${window.staticPrefix}img/marker-icon-blue.png`,
                    iconRetinaUrl: `${window.staticPrefix}img/marker-icon-blue2x.png`,
                }),
                harvestIcon = new defaultIcon({
                    iconUrl: `${window.staticPrefix}img/marker-icon-green.png`,
                    iconRetinaUrl: `${window.staticPrefix}img/marker-icon-green2x.png`,
                }),
                transportIcon = new defaultIcon({
                    iconUrl: `${window.staticPrefix}img/marker-icon-pink.png`,
                    iconRetinaUrl: `${window.staticPrefix}img/marker-icon-pink2x.png`,
                });
            this.packages.forEach((package) => {
                package.entities.forEach((entity) => {
                    bounds.push(entity.location_display);
                    markers.push({
                        location: entity.location_display,
                        text: `<b class="${package.type_display}">${package.pid}</b><br/>${entity.description}`,
                        icon: function () {
                            if (package.type_display == 'plot') {
                                return plotIcon;
                            }
                            else if (['harvest', 'replantation'].indexOf(package.type_display) >= 0) {
                                return harvestIcon;
                            }
                            else if (package.type_display == 'transport') {
                                return transportIcon
                            }
                        }
                    })
                })
            });
            let mapWrapper = document.getElementById('map-wrapper');
            mapWrapper.innerHTML = '<div id="map"></div>';
            if (bounds.length) {
                let map = L.map('map').setView(bounds[0], 13);
                L.tileLayer(`https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=${window.mapboxToken}`, {
                    maxZoom: 18,
                    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
                    '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
                    'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
                    id: 'mapbox/streets-v11',
                    tileSize: 512,
                    zoomOffset: -1
                }).addTo(map);
                map.fitBounds(bounds);
                markers.forEach((marker) => {
                    L.marker(marker.location, {icon: marker.icon()}).addTo(map).bindPopup(marker.text);
                });
            }
            this.$root.$data.loading = false;
        }
    },
    filters: {
        trimTime(timestamp) {
            return timestamp.split(' ')[0]
        }
    },
});