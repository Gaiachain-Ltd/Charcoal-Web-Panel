$(document).ready(function() {
const DAY_LABELS = ['S', 'M', 'T', 'W', 'Th', 'F', 'S'];
const MONTH_LABELS = [
        "January", "February", "March",
        "April", "May", "June",
        "July", "August", "September",
        "October", "November", "December"];

const Calendar = Vue.component('calendar', {
  template: `
    <div class="calendar">
      <header class="header">
        <button @click="previousMonth">&lt;&lt;</button>
        <span>{{ currentMonthLabel }} {{ currentYear }}</span>
        <button @click="nextMonth">&gt;&gt;</button>
      </header>
      <div class="headings" v-for="dayLabel in dayLabels">
        {{ dayLabel }}
      </div>
      <div v-for="(day, index) in datesList"
           class="day"
           :class="dayClassObj(day)">
        <button @click="setSelectedDate(day)">
          {{ day.date | formatDateToDay }}
          <div class="action-dots">
            <div class="action-dot" v-for="action in day.availableActions" :class="action"></div>
          </div>
        </button>
        
      </div>
    </div>
  `,
  data() {
    return {
      today: null,
      selectedDate: null,
      currDateCursor: null,
      dayLabels: null,
      datesList: [],
      response: []
    };
  },
  created() {
    this.dayLabels = DAY_LABELS.slice();
    this.today = new Date();
    this.selectedDate = this.today;
    this.currDateCursor = this.today;
  },
  props: {
    startDate: {
      required: false,
      type: Date,
    }
  },
  computed: {
    currentMonth() {
      return this.currDateCursor.getMonth();
    },
    currentYear() {
      return this.currDateCursor.getFullYear();
    },
    currentMonthLabel() {
      return MONTH_LABELS[this.currentMonth];
    },
    dates() {
    },
  },
  watch: {
  },
  mounted: function () {
    this.drawCalendar();
    if (this.startDate) {
      this.currDateCursor = this.startDate;
      this.selectedDate = this.startDate;
    }
  },
  methods: {
    showDots: function (actions) {

    },
    drawCalendar: function () {
        const cursorDate = this.currDateCursor;
        let startDate = dateFns.startOfMonth(cursorDate),
          endDate = dateFns.lastDayOfMonth(cursorDate);
        const daysNeededForLastMonth = dateFns.getDay(startDate),
            daysNeededForNextMonth = (7 - (dateFns.getDay(endDate) + 1)) > 6 ? 0 : (7 - dateFns.getDay(endDate)) - 1;
        startDate = dateFns.addDays(startDate, -daysNeededForLastMonth);
        endDate = dateFns.addDays(endDate, daysNeededForNextMonth);
        let daysList = [];
        dateFns.eachDay(startDate, endDate).forEach(function (day) {
            daysList.push((dateFns.getTime(day) / 1000).toString())
        });
        let arrArg = encodeURIComponent(JSON.stringify(daysList));
        this.$http.get('/entities/dots/?dates=' + arrArg)
        .then(function (response){
            dates = [];
            actionsFunc = this.getAvailableActions
            dateFns.eachDay(startDate, endDate).forEach(function (date) {
                let one_day = {
                    'date': date,
                    'isCurrentMonth': dateFns.isSameMonth(cursorDate, date),
                    'isToday': dateFns.isToday(date),
                    'isSelected': dateFns.isSameDay(this.selectedDate, date),
                    'availableActions': actionsFunc(date, response),
                };
                dates.push(one_day)
            });
            this.datesList = dates;
        }).catch(function(err) {
            console.log('error', err);
        })
    },
    getAvailableActions: function (day, response) {
      let actions = [];
      Object.keys(response.data).forEach(function(key) {
        timestamp = dateFns.getTime(day) / 1000;
        if (timestamp === parseInt(key)){
            actions = response.data[key];
        }
      });
      return actions
    },
    dayClassObj(day) {
      return {
        'today' : day.isToday,
        'current': day.isCurrentMonth,
        'selected': day.isSelected,
      };
    },
    nextMonth() {
      this.currDateCursor = dateFns.addMonths(this.currDateCursor, 1);
      this.drawCalendar();
    },
    previousMonth() {
      this.currDateCursor = dateFns.addMonths(this.currDateCursor, -1);
      this.drawCalendar();
    },
    setSelectedDate(day) {
      this.selectedDate = day.date;
      this.$emit('input', this.selectedDate);
      // change calendar to correct month if they select previous or next month's days
      if (!day.isCurrentMonth) {
        const selectedMonth = dateFns.getMonth(this.selectedDate);
        this.currDateCursor = dateFns.setMonth(this.currDateCursor, selectedMonth);
      }
      let startTimestamp =  dateFns.getTime(this.selectedDate) / 1000;
      let endDate = dateFns.addHours(this.selectedDate, 24);
      let endTimestamp = dateFns.getTime(endDate) / 1000;
      this.$parent.actions = this.$parent.getActions("?from_timestamp=" + startTimestamp + "&to_timestamp=" + endTimestamp);
    }
  },
  filters: {
    formatDateToDay(val) {
      return dateFns.format(val, 'D');
    }
  },
});



const app = new Vue(
    {
        el: '#dashboard-main',
        components: {
            Calendar,
        },
        delimiters: ['[[', ']]'],
        data: {
            actions: [],
            action_types: {},
            keyword: '',
            active_package_type: 'harvest',
            recent_limit: 5,
            content_page: "recent_actions",
            active_element: '',
            active_subelement: '',
            show_subelements: false,
            package_keyword: '',
            packages: [],
            package_properties: {},
            opened_package: '',
            chain_list: '',
            loading: false,
            transactions: [],
            transactions_per_page: 10,
            transactions_next_page: '',
            transactions_prev_page: '',
            opened_transaction: '',
            showTransactionFirstPage: false,
            curr: new Date(),
        },
        computed: {
            formattedDate() {
              return dateFns.format(this.curr, 'MM/DD/YYYY');
            }
        },
        watch: {
            keyword: function (val) {
                let args = "";
                if (this.content_page === 'recent_actions') {
                    args = "?limit=" + this.recent_limit + "&keyword=" + val;
                }
                this.getActions(args, search=true)
            },
            package_keyword: function (val) {
                let args = "";
                if (this.content_page === 'recent_actions') {
                    args = "&keyword=" + val;
                }
                this.getPackages(this.active_package_type, args, search=true)
            },
        },
        mounted: function () {
            this.loading = true;
            this.getActions("?limit=5");
            this.getActionTypes()
        },
        methods: {
            setActiveAction: function(el) {
                let previous_element = this.active_element;
                this.active_element = el;
                if (el === 'tracability') {
                    if (previous_element === 'tracability') {
                        this.active_element = '';
                        this.show_subelements = false;
                    } else {
                        this.show_subelements = true;
                    }
                    this.active_subelement = '';
                } else {
                    this.show_subelements = false;
                    this.active_subelement = '';
                    this.active_package_type = '';
                }
                this.loading = false;
            },
            getActionTypes: function () {
                this.loading = true;
                this.$http.get('/entities/types/').then(function (response){
                        this.action_types = response.data;
                        this.loading = false;
                    }).catch(function(err) {
                        this.loading = false;
                        console.log(err);
                    })
            },
            getRecentActions: function (args) {
                this.getActions()
            },
            getActions: function (args="", search=false) {
                if (!search) {
                    this.loading = true;
                }
                this.$http.get(
                   '/entities/batch_web/' + args,
               ).then(function (response) {
                   this.actions = response.data.results;
                   this.loading = false;
                   return response.data.results
               }).catch(function (err) {
                this.loading = false;
                console.log(err);
               })
            },
            showRecentTransactions: function () {
                this.loading = true;
                this.active_subelement = 'tracability_transactions';
                this.active_element = 'tracability_transactions';
                this.getActions();
            },
            getActionTitle: function (action) {
                return this.action_types[action.action] + ' ' + action.pid
            },
            getActionDate: function (timestamp) {
                return moment(timestamp*1000).format('DD/MM/YYYY')
            },
            getActionColor: function (action) {
                let color_class = "";
                if (['HA', 'BR', 'HR'].includes(action.action)){
                    color_class = 'harvest';
                } else if (action.action === 'BG') {
                    color_class = 'sac';
                } else if (['CR', 'TR', 'LR', 'IN'].includes(action.action)) {
                    color_class = 'lot';
                }
                return color_class
            },
            getPackages: function (type, args="", search=false) {
                if (!search) {
                    this.loading = true;
                }
                let url = '/entities/packages/?type=' + type;
                if (args.length > 0) {
                    url += args
                }
                this.$http.get(url).then(function (response){
                        this.packages = response.data.results;
                        this.opened_package = '';
                        this.loading = false;
                    }).catch(function(err) {
                        this.loading = false;
                        this.opened_package = '';
                        console.log(err);
                    })
            },
            showPackages: function (type, active_sub=false) {
                if (active_sub) {
                    this.active_subelement = active_sub;
                }
                this.active_package_type = type;
                this.package_keyword = "";
                this.getPackages(type)
            },
            getPackageDetails: function (id) {
                this.loading = true;
                let url = "/entities/packages/" + id + "/get_package_details/";
                this.$http.get(url).then(function (response){
                        this.package_properties = response.data;
                        this.opened_package = response.data.id;
                        this.loading = false;
                    }).catch(function(err) {
                        this.loading = false;
                        console.log(err);
                    })
            },
            getPropertyKey: function (val) {
                return Object.keys(val)[0]
            },
            getPropertyValue: function (val) {
                return val[Object.keys(val)[0]]
            },
            hideDetails: function () {
                this.opened_package = ''
            },
            getPackageChain: function (id) {
                this.loading = true;
                this.opened_package = '';
                this.active_element = 'package_chain';
                this.active_subelement = 'package_chain';
                let url = "/entities/packages/" + id + "/get_package_chain/";
                this.$http.get(url).then(function (response){
                        this.chain_list = response.data;
                        this.loading = false;
                    }).catch(function(err) {
                        this.loading = false;
                        console.log(err);
                    })
            },
            getMap: function() {
                this.loading = true;
                this.active_element = 'map_chain';
                this.active_subelement = 'map_chain';
                let chain_list = this.chain_list;
                let default_position = this.chain_list[0].location.split(", ");
                default_position[0] = parseFloat(default_position[0]);
                default_position[1] = parseFloat(default_position[1]);
                setTimeout(function (){
                    var mymap = L.map('mapid').setView(default_position, 8);
                    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1Ijoic2NoZXJub3YiLCJhIjoiY2s1MmVubXZuMDdwejNtcW5wY3lkMnZsZyJ9.I_3cxb5zDMf6ahWoq8Js6w', {
                        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
                        maxZoom: 18,
                        id: 'mapbox/streets-v11',
                        accessToken: 'pk.eyJ1Ijoic2NoZXJub3YiLCJhIjoiY2s1MmVubXZuMDdwejNtcW5wY3lkMnZsZyJ9.I_3cxb5zDMf6ahWoq8Js6w'
                    }).addTo(mymap);
                    var harvestIcon = L.icon({
                        iconUrl: '/static/img/harvest_map_icon.png',
                        iconSize: [40, 40],
                    });
                    var sacIcon = L.icon({
                        iconUrl: '/static/img/sac_map_icon.png',
                        iconSize: [40, 40],
                    });
                    var lotIcon = L.icon({
                        iconUrl: '/static/img/lot_map_icon.png',
                        iconSize: [40, 40],
                    });
                    var mapChain = {};
                    var locations = [];
                    chain_list.forEach(function (item) {
                        var location = item.location.split(", ");
                        location[0] = parseFloat(location[0]);
                        location[1] = parseFloat(location[1]);
                        locations.push(location);
                        var marker_name = item.action_short_name;
                        var current_icon = harvestIcon;
                        if (['CR', 'TR', 'LR', 'IN'].includes(marker_name)){
                            current_icon = lotIcon
                        } else if (marker_name === 'BG') {
                            current_icon = sacIcon
                        }
                        mapChain[marker_name] = L.marker(location, {icon: current_icon}).bindPopup(item.action_name).openPopup();
                        mapChain[marker_name].addTo(mymap);
                    });
                    var polyline = L.polyline(locations, {color: 'red'}).addTo(mymap);
                }, 1000);
                this.loading = false;
            },
            showBlockchainExplorer: function () {
                this.getTransactions();
                this.setActiveAction('blockchain_explorer');

            },
            getTransactions: function (query) {
                var url;
                if (query === undefined)
                    url = `/blockchain/transactions/?limit=${this.transactions_per_page}`;
                else
                    url = `/blockchain/transactions/?${query}`;
                this.$http.get(url)
                    .then(function (response) {
                        this.transactions = response.body.data;
                        if (response.body.paging.next)
                            this.transactions_next_page = response.body.paging.next.split('?')[1];
                        if (response.body.paging.previous)
                            this.transactions_prev_page = response.body.paging.previous.split('?')[1];
                        this.showTransactionFirstPage = response.body.paging.start !== null;
                    })
            },
            getTransactionDetails: function (head) {
                this.opened_transaction = head;
            },
            hideTransactionDetails: function () {
                this.opened_transaction = ''
            },
            openMap: function () {
                // this.active_subelement = 'tracability_maps';
                // // window.open('http://etclab.org/websig/lizmap/www/index.php/view/map/?repository=rci&project=PROJET_PRM&layers=0BTTFFFTTTFTTTTTTTTTTTTTTTTTTTTTTT&bbox=-764617.961462%2C570930.920373%2C-186754.027707%2C753768.292006&crs=EPSG%3A3857', '_blank');
                // url = "https://iframe-beta.gaiachain.io/websig/lizmap/www/index.php/view/map/?repository=rci&project=PROJET_PRM&layers=0BTTFFFTTTFTTTTTTTTTTTTTTTTTTTTTTT&bbox=-764617.961462%2C570930.920373%2C-186754.027707%2C753768.292006&crs=EPSG%3A3857";
                // this.$http.get(url).then(function (response){
                //         console.log()
                //         this.loading = false;
                //     }).catch(function(err) {
                //         this.loading = false;
                //         console.log(err);
                //     })
            }
        }
    });
});
