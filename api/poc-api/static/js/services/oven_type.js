class OvenTypeDataServiceClass {
    getAll() {
        return Vue.http.get("/api/v1/additional_data/oven-types/?active_only=1");
    }

    getByID(id) {
        return Vue.http.get(`/api/v1/additional_data/oven-types/${id}/`);
    }

    create(data) {
        return Vue.http.post("/api/v1/additional_data/oven-types/", data);
    }

    update(id, data) {
        return Vue.http.patch(`/api/v1/additional_data/oven-types/${id}/`, data);
    }

    delete(id) {
        return Vue.http.delete(`/api/v1/additional_data/oven-types/${id}/`);
    }

}

window.OvenTypeDataService = new OvenTypeDataServiceClass();