const DAY_LABELS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
const MONTH_LABELS = [
    "January", "February", "March",
    "April", "May", "June",
    "July", "August", "September",
    "October", "November", "December"];

let Calendar = Vue.component('calendar', {
    template: `
        <div class="start-content">
            <div class="content-data">
                <div class="actions-data left-block">
                    <div class="calendar-block">
                        <div class="calendar">
                            <header class="header">
                                <span>[[ currentMonthLabel ]] [[ currentYear ]]</span>
                                <button @click="previousMonth">&lt;</button>
                                <button @click="nextMonth">&gt;</button>
                            </header>
                            <div class="headings" v-for="dayLabel in dayLabels">
                                [[ dayLabel ]]
                            </div>
                            <div v-for="(day, index) in datesList"
                                 class="day"
                                 :class="dayClassObj(day)">
                                <button @click="setSelectedDate(day)">
                                    [[ day.date | formatDateToDay ]]
                                    <div class="action-dots">
                                        <div class="action-dot" v-for="action in day.availableActions" :class="action"></div>
                                    </div>
                                </button>
        
                            </div>
                        </div>
                    </div>
                </div>
                <div class="actions-data right-block">
                    <div class="title-block">
                        <span class="title">[[ $t('recent_transactions') ]]</span>
                        <div class="more" @click="showRecentTransactions()">
                            <span>[[ $t('more') ]]</span>
                            <img v-bind:src="$root.$data.staticPrefix + 'img/icons_right_arrow.png'"/>
                        </div>
                    </div>
                    <div class="actions">
                        <div class="action" v-for="(action, key) in actions" v-bind:id="key">
                            <div class="action-name-date">
                                <span class="action-name" :class="getActionColor(action)">[[getActionTitle(action)]]</span>
                                <span class="acrtion-date">[[getActionDate(action.timestamp)]]</span>
                            </div>
                            <span class="direction">[[action.properties.short_description]]</span>
                            <hr>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `,
    delimiters: ['[[', ']]'],
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
    watch: {},
    mounted: function () {
        document.getElementById('current-page-name').innerHTML = this.$t('calendar')
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
                .then(function (response) {
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
                }).catch(function (err) {
                console.log('error', err);
            })
        },
        getAvailableActions: function (day, response) {
            let actions = [];
            Object.keys(response.data).forEach(function (key) {
                timestamp = dateFns.getTime(day) / 1000;
                if (timestamp === parseInt(key)) {
                    actions = response.data[key];
                }
            });
            return actions
        },
        dayClassObj(day) {
            return {
                'today': day.isToday,
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
            let startTimestamp = dateFns.getTime(this.selectedDate) / 1000;
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