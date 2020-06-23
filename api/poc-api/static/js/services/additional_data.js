class AdditionalDataDataServiceClass {
    getAll() {
        return Vue.http.get("/api/v1/additional_data/all_data/");
    }
}

window.AdditionalDataDataService = new AdditionalDataDataServiceClass();