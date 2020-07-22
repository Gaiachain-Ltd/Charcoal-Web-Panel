class AdditionalDataDataServiceClass {
    getAll() {
        return Vue.http.get("/api/v1/additional_data/all_data/?active_only=1");
    }
}

window.AdditionalDataDataService = new AdditionalDataDataServiceClass();