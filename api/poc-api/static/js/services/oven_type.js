class OvenTypeDataServiceClass {
    getAll() {
        return Vue.http.get("/additional_data/oven-types/");
    }

    getByID(id) {
        return Vue.http.get(`/additional_data/oven-types/${id}/`);
    }

    create(data) {
        return Vue.http.post("/additional_data/oven-types/", data);
    }

    update(id, data) {
        return Vue.http.patch(`/additional_data/oven-types/${id}/`, data);
    }

    delete(id) {
        return Vue.http.delete(`/additional_data/oven-types/${id}/`);
    }

}

window.OvenTypeDataService = new OvenTypeDataServiceClass();