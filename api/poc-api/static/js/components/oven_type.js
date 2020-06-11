
let ovenType = Vue.component('oven-type', {
    template: `
        <div class="additional-data-block">
            <div class="additional-data-title">
                <span class="title">
                    [[ $t("oven_type") ]]
                </span>
                <button class="add-new" @click="addObject()">[[ $t("add_new") ]] <div class="plus"><div class="horizontal"></div><div class="vertical"></div></div></button>
            </div>
            <div class="additional-data-list">
                <div class="additional-data-list-row" v-for="object in objects">
                    <div class="additional-data-list-row-name" v-if="isEditing && object.id == currentObject.id">
                        <input name="name" type="text" :placeholder="[[ $t('name') ]]" v-model="currentObject.name" @change="saveObject">
                    </div>
                    <div class="additional-data-list-row-name" v-else>[[ object.name ]]</div>
                    <div class="additional-data-list-row-actions">
                        <button @click="editObject(object.id)">[[ $t("edit") ]] <i class="icon-edit"></i></button>
                        <button @click="openedModal = object.id">[[ $t("delete") ]] <i class="icon-delete"></i></button>
                    </div>
                    <div class="additional-data-list-row-extra" v-if="isEditing && object.id == currentObject.id">
                        <label><input type="radio" name="oven_measurements" value="1" v-model="currentObject.type"  @change="saveObject"> [[ $t("custom_measurements") ]]</label>
                        <label><input type="radio" name="oven_measurements" value="2" v-model="currentObject.type"  @change="saveObject"> [[ $t("fixed_measurements") ]]</label>
                        <input type="text" :placeholder="$t('height') + ' [m]'" v-model="currentObject.oven_height" v-if="currentObject.type == 2"  @change="saveObject">
                        <input type="text" :placeholder="$t('length') + ' [m]'" v-model="currentObject.oven_length" v-if="currentObject.type == 2"  @change="saveObject">
                        <input type="text" :placeholder="$t('width') + ' [m]'" v-model="currentObject.oven_width" v-if="currentObject.type == 2"  @change="saveObject">
                    </div>
                    <div class="additional-data-list-row-extra" v-else>
                        <span v-if="object.type == 1">[[ $t("custom_measurements") ]]</span>
                        <span v-if="object.type == 2">[[ $t("fixed_measurements") ]]</span>
                        <span class="measurements">
                            <span v-if="object.type == 2">[[ $t("height") ]]: [[ object.oven_height ]] [m]</span>
                            <span v-if="object.type == 2">[[ $t("length") ]]: [[ object.oven_length ]] [m]</span>
                            <span v-if="object.type == 2">[[ $t("width") ]]: [[ object.oven_width ]] [m]</span>
                        </span>
                    </div>
                    <delete-object-modal v-if="openedModal == object.id" @close="openedModal = null" 
                                         v-bind:object-id="object.id" v-bind:submit-callback="deleteObject">
                    </delete-object-modal>
                </div>
                <div class="additional-data-list-row" v-if="isCreating">
                    <div class="additional-data-list-row-name">
                        <input name="name" type="text" :placeholder="[[ $t('name') ]]" v-model="currentObject.name" @change="saveObject">
                    </div>
                    <div class="additional-data-list-row-extra">
                        <label><input type="radio" name="oven_measurements" value="1" v-model="currentObject.type"  @change="saveObject"> [[ $t("custom_measurements") ]]</label>
                        <label><input type="radio" name="oven_measurements" value="2" v-model="currentObject.type"  @change="saveObject"> [[ $t("fixed_measurements") ]]</label>
                        <input type="text" :placeholder="$t('height') + ' [m]'" v-model="currentObject.oven_height" v-if="currentObject.type == 2"  @change="saveObject">
                        <input type="text" :placeholder="$t('length') + ' [m]'" v-model="currentObject.oven_length" v-if="currentObject.type == 2"  @change="saveObject">
                        <input type="text" :placeholder="$t('width') + ' [m]'" v-model="currentObject.oven_width" v-if="currentObject.type == 2"  @change="saveObject">
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
        initialObjects: {
            type: Array
        }
    },
    mounted: function () {
    },
    methods: {
        deleteObject(id) {
            OvenTypeDataService.delete(id)
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
                promise = OvenTypeDataService.update(this.currentObject.id, this.currentObject)
            } else {
                promise = OvenTypeDataService.create(this.currentObject)
            }
            promise.then(response => {
                this.currentObject = response.data;
                if (this.isCreating) {
                    this.isEditing = true;
                    this.isCreating = false;
                }
                this.getData();
            })

        },
        addObject() {
            this.currentObject = {};
            this.isCreating = true;
            this.isEditing = false;
        },
        editObject(id) {
            if (this.isEditing && id == this.currentObject.id) {
                this.isEditing = false;
            }
            else {
                OvenTypeDataService.getByID(id).then(response => {
                    this.currentObject = response.data;
                    this.isEditing = true;
                    this.isCreating = false;
                });
            }

        },
        getData() {
            this.$root.$data.loading = true;
            OvenTypeDataService.getAll()
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