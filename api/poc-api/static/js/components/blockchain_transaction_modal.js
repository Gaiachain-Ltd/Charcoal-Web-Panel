let blockchainTransactionModal = Vue.component('blockchain-transaction-modal', {
    template:`
    <transition name="modal">
        <div class="modal-mask">
            <div class="modal-wrapper">
                <div class="modal-container blockchain-details">
                    <div class="modal-header">
                        <slot name="header">
                            <span>[[ $t("blockchain_transaction") ]]</span>
                            <button @click="$emit('close')" class="close">&times;</button>
                        </slot>
                    </div>
                    
                    <div class="modal-body">
                        <slot name="body">
                            <div class="heading" :class="packageType">
                                <p class="action-name">[[ action ]]</p>
                                <p class="package-pid">[[ packagePid ]]</p>
                            </div>
                            <div class="package-details">
                                <div class="package-property" v-for="(property, key) in transaction.header" :key="key">
                                    <div class="transaction-property-key">
                                        <span>[[ key ]]</span>
                                    </div>
                                    <div class="transaction-property-value">
                                        <span>[[ property ]]</span>
                                    </div>
                                </div>
                                <div class="package-property">
                                    <div class="transaction-property-key">
                                        <span>[[ $t('header_signature') ]]</span>
                                    </div>
                                    <div class="transaction-property-value">
                                        <span>[[ transaction.header_signature ]]</span>
                                    </div>
                                </div>
                                <div class="package-property">
                                    <div class="transaction-property-key">
                                        <span>[[ $t('payload') ]]</span>
                                    </div>
                                    <div class="transaction-property-value">
                                        <span v-html="transaction.payload"></span>
                                    </div>
                                </div>
                            </div>
                        </slot>
                    </div>
                    
                    <div class="modal-footer">
                        <slot name="footer">
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
        action: {
            type: String
        },
        packagePid: {
            type: String
        },
        packageType: {
            type: String
        },
        transaction: {
            type: Object
        }
    },
    methods: {
    }
});