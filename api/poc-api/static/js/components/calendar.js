
let Calendar = Vue.component('calendar', {
    template: `
        <div class="start-content">
            <div class="content-data">
                <div class="actions-data col">
                    <div class="calendar-block">
                        <div class="nav-search">
                            <ul class="nav nav-tabs">
                                <li class="nav-item dropdown">
                                    <a class="nav-link dropdown-toggle active" data-toggle="dropdown" href="#" 
                                       role="button" aria-haspopup="true" aria-expanded="false">[[ currentMonthLabel ]]</a>
                                    <div class="dropdown-menu">
                                        <a class="dropdown-item" href="#" v-for="(month, index) in months"
                                           @click.prevent="setMonth(index)">[[ month.toUpperCase() ]] <i class="current" v-if="index === currentMonth"></i></a>
                                    </div>
                                </li>
                                <li class="nav-item dropdown">
                                    <a class="nav-link dropdown-toggle active" data-toggle="dropdown" href="#" 
                                       role="button" aria-haspopup="true" aria-expanded="false">[[ currentYear ]]</a>
                                    <div class="dropdown-menu">
                                        <a class="dropdown-item" href="#" v-for="year in yearsRange"
                                           @click.prevent="setYear(year)">[[ year ]] <i class="current" v-if="year === currentYear"></i></a>
                                    </div>
                                </li>
                            </ul>
                            <div class="nav-tabs-right-actions">
                                <ul class="nav nav-tabs float-right">
                                    <li class="nav-item m-0">
                                        <a class="nav-link"
                                           @click.prevent="previousMonth" href="#">&lt;</a>
                                    </li>
                                    <li class="nav-item m-0">
                                        <a class="nav-link"
                                           @click.prevent="nextMonth" href="#">&gt;</a>
                                    </li>
                                </ul>
                            </div>
                        </div>
                        <div class="calendar headings">
                            <div class="headings">
                                [[ $t('weekday_names.short.monday') ]]
                            </div>
                            <div class="headings">
                                [[ $t('weekday_names.short.tuesday') ]]
                            </div>
                            <div class="headings">
                                [[ $t('weekday_names.short.wednesday') ]]
                            </div>
                            <div class="headings">
                                [[ $t('weekday_names.short.thursday') ]]
                            </div>
                            <div class="headings">
                                [[ $t('weekday_names.short.friday') ]]
                            </div>
                            <div class="headings">
                                [[ $t('weekday_names.short.saturday') ]]
                            </div>
                            <div class="headings">
                                [[ $t('weekday_names.short.sunday') ]]
                            </div>
                        </div>
                        <div class="calendar">
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
                <div class="actions-data col">
                    <div class="calendar-details">
                        <div class="calendar-details-header">
                            <p class="calendar-details-date">
                                [[ selectedDate | formatDate ]]
                            </p>
                        </div>
                        <div class="calendar-details-packages">
                            <packages v-bind:date="selectedDate" v-bind:showSearch="false" v-bind:showTimezone="false"></packages>
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
            response: [],
            yearsRange: [],
            months: [
                this.$t("month_names.january"), this.$t("month_names.february"), this.$t("month_names.march"),
                this.$t("month_names.april"), this.$t("month_names.may"), this.$t("month_names.june"),
                this.$t("month_names.july"), this.$t("month_names.august"), this.$t("month_names.september"),
                this.$t("month_names.october"), this.$t("month_names.november"), this.$t("month_names.december")
            ]
        };
    },
    created() {
        this.today = new Date();
        this.selectedDate = this.today;
        this.currDateCursor = this.today;
        this.yearsRange = this.generateYearsRange();
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
            return this.months[this.currentMonth];
        },
    },
    watch: {},
    mounted: function () {
        document.getElementById('current-page-name').innerHTML = this.$t('calendar');
        this.drawCalendar();
        if (this.startDate) {
            this.currDateCursor = this.startDate;
            this.selectedDate = this.startDate;
        }
    },
    methods: {
        generateYearsRange() {
            let arr = [];
            let currentYear = this.today.getFullYear();
            for (let i = currentYear; i >= currentYear - 5; i -= 1) {
                arr.push(i);
            }

            return arr;
        },
        drawCalendar: function () {
            this.$root.$data.loading = true;
            const cursorDate = this.currDateCursor;
            let startDate = dateFns.startOfMonth(cursorDate),
                endDate = dateFns.lastDayOfMonth(cursorDate);
            startDate = dateFns.startOfWeek(startDate, {weekStartsOn: 1});
            endDate = dateFns.endOfWeek(endDate, {weekStartsOn: 1});
            let daysList = [];
            dateFns.eachDay(startDate, endDate).forEach((day) => {
                daysList.push((dateFns.getTime(day) / 1000).toString())
            });
            let arrArg = encodeURIComponent(JSON.stringify(daysList));
            this.$http.get('/entities/dots/?dates=' + arrArg)
                .then((response) => {
                    let dates = [];
                    let actionsFunc = this.getAvailableActions;
                    dateFns.eachDay(startDate, endDate).forEach((date) => {
                        dates.push({
                            'date': date,
                            'isCurrentMonth': dateFns.isSameMonth(cursorDate, date),
                            'isToday': dateFns.isToday(date),
                            'isSelected': dateFns.isSameDay(this.selectedDate, date),
                            'availableActions': actionsFunc(date, response),
                        })
                    });
                    this.datesList = dates;
                    this.$root.$data.loading = false;
                }).catch(function (err) {
                this.$root.$data.loading = false;
                console.log('error', err);
            })

        },
        getAvailableActions: function (day, response) {
            let actions = [];
            Object.keys(response.data).forEach(function (key) {
                let timestamp = dateFns.getTime(day) / 1000;
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
            this.drawCalendar();
        },
        setYear(year) {
            this.currDateCursor = dateFns.setYear(this.currDateCursor, year);
            this.drawCalendar();
        },
        setMonth(month) {
            this.currDateCursor = dateFns.setMonth(this.currDateCursor, month);
            this.drawCalendar();
        },
    },
    filters: {
        formatDateToDay(val) {
            return dateFns.format(val, 'D');
        },
        formatDate(val) {
            return dateFns.format(val, 'MMMM D, YYYY');
        }
    },
});