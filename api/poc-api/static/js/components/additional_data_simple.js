
let additionalDataSimple = Vue.component('additional-data-simple', {
    template: `
        <div class="additional-data-block">
            <div class="additional-data-title">
                <span class="title">
                    [[ $t(title) ]]
                </span>
                <button class="add-new" @click="addObject()">[[ $t("add_new") ]] <div class="plus"><div class="horizontal"></div><div class="vertical"></div></div></button>
            </div>
            <div class="additional-data-list">
                <div class="additional-data-list-row" v-for="object in objects" :key="title + '_' + object.id">
                    <div class="additional-data-list-row-name" v-if="isEditing && object.id == currentObject.id">
                        <input name="name" type="text" :placeholder="[[ $t(placeholder) ]]" v-model="currentObject[nameField]" @change="saveObject">
                    </div>
                    <div class="additional-data-list-row-name" v-else>[[ object[nameField] ]]</div>
                    <div class="additional-data-list-row-actions">
                        <button @click="editObject(object.id)">[[ $t("edit") ]] <i class="icon-edit"></i></button>
                        <button @click="openedModal = object.id">[[ $t("delete") ]] <i class="icon-delete"></i></button>
                    </div>
                    <delete-object-modal v-if="openedModal == object.id" @close="openedModal = null" 
                                         v-bind:object-id="object.id" v-bind:submit-callback="deleteObject">
                    </delete-object-modal>
                </div>
                <div class="additional-data-list-row" v-if="isCreating">
                    <div class="additional-data-list-row-name">
                        <input name="name" type="text" :placeholder="[[ $t(placeholder) ]]" v-model="currentObject[nameField]" @change="saveObject">
                    </div>
                </div>
            </div>
        </div>
        `,
    delimiters: ['[[', ']]'],
    data() {
        return {
            objects: this.initialObjects,
            isCreating: false,
            isEditing: false,
            currentObject: {},
            openedModal: null,
        }
    },
    props: {
        title: {
            type: String,
            default: ''
        },
        placeholder: {
            type: String,
            default: ''
        },
        nameField: {
            type: String,
            default: ''
        },
        dataServiceName: {
            type: String,
            default: ''
        },
        initialObjects: {
            type: Array
        }
    },
    mounted: function () {
        this.dataService = window[`${this.dataServiceName}`];
    },
    methods: {
        deleteObject(id) {
            this.dataService.delete(id)
                .then(response => {
                    this.openedModal = null;
                    this.getData();
                })
                .catch(e => {
                    console.log(e)
                });
        },
        saveObject(e) {
            let promise;
            if (this.isEditing) {
                promise = this.dataService.update(this.currentObject.id, this.currentObject);
            } else {
                promise = this.dataService.create(this.currentObject);
            }
            promise.then(response => {
                this.isEditing = false;
                this.currentObject = {};
                this.isCreating = false;
                this.getData();
            })

        },
        addObject() {
            this.currentObject = {};
            this.isCreating = true;
            this.isEditing = false;
        },
        editObject(id) {
            this.dataService.getByID(id).then(response => {
                this.currentObject = response.data;
                this.isEditing = true;
                this.isCreating = false;
            });

        },
        getData() {
            this.$root.$data.loading = true;
            this.dataService.getAll()
                .then(response => {
                    this.objects = response.data.results;
                    this.$root.$data.loading = false;
                })
                .catch(e => {
                    this.$root.$data.loading = false;
                    console.log(e)
                });
        },
    },
});