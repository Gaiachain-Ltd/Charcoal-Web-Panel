let deleteObjectModal = Vue.component('delete-object-modal', {
    template:`
    <transition name="modal">
        <div class="modal-mask">
            <div class="modal-wrapper">
                <div class="modal-container">
                    <div class="modal-header">
                        <slot name="header">
                            <button @click="$emit('close')" class="close">&times;</button>
                        </slot>
                    </div>
                    
                    <div class="modal-body">
                        <slot name="body">
                            [[ $t("modal.delete_item") ]]
                        </slot>
                    </div>
                    
                    <div class="modal-footer">
                        <slot name="footer">
                            <button class="modal-default-button" @click="submit()">
                                [[ $t("yes") ]]
                            </button>
                            <button class="modal-default-button" @click="$emit('close')">
                                [[ $t("no") ]]
                            </button>
                        </slot>
                    </div>
                </div>
            </div>
        </div>
      </transition>
    `,
    delimiters: ['[[', ']]'],
    data() {
        return {
        }
    },
    props: {
        submitCallback: {
            type: Function
        },
        objectId: {
            type: Number
        }
    },
    methods: {
        submit() {
            this.submitCallback(this.objectId);
            console.log('submit')
        },
    }
});