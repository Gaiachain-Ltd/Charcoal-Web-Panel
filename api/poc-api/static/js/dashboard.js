$(document).ready(function() {
const dashboard = new Vue(
    {
        el: '#dashboard',
        delimiters: ['[[', ']]'],
        data: {
            active_element: "",
            actions: [],
            action_types: {},
            keyword: "",
            recent_limit: 5,
        },
        computed: {
            get_active_element: function (val) {
                this.active_element = window.active_element;

            },
        },
        watch: {
            keyword: function (val) {
                args = "?limit=" + this.recent_limit;
                if (val.length > 0) {
                    args += "&keyword=" + val;
                }
                this.getActions(args)
            },
        },
        mounted: function () {
            this.getActions("?limit=5");
            this.getActionTypes()
        },
        methods: {
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
            getActions: function (args="") {
                console.log('args', args)
                this.$http.post(
                   '/entities/batch/' + args,
                   {},
               ).then(function (response) {
                   this.loading = false;
                   this.actions = response.data.results;
                   return response.data.results
               }).catch(function (err) {
                this.loading = false;
                console.log(err);
               })
            },
            getActionTitle: function (action) {
                return this.action_types[action.action] + ' ' + action.pid
            },
            getActionDate: function (timestamp) {
                return moment(timestamp*1000).format('DD/MM/YYYY')
            }
        }
    });
});
