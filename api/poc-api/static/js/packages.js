$(document).ready(function() {
const packages = new Vue(
    {
        el: '#sidebar',
        delimiters: ['[[', ']]'],
        data: {
            active_element: '',
            active_subelement: '',
            show_subelements: false,
        },
        computed: {
        },
        watch: {
        },
        mounted: function () {
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
                }
            },
        }
    });
});
