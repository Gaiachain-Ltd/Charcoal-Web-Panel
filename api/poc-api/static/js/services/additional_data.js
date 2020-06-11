class AdditionalDataDataServiceClass {
    getAll() {
        return Vue.http.get("/additional_data/all_data/");
    }
}

window.AdditionalDataDataService = new AdditionalDataDataServiceClass();