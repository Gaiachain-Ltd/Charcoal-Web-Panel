class VillageDataServiceClass {
    getAll() {
        return Vue.http.get("/api/v1/additional_data/villages/?active_only=1");
    }

    getByID(id) {
        return Vue.http.get(`/api/v1/additional_data/villages/${id}/`);
    }

    create(data) {
        return Vue.http.post("/api/v1/additional_data/villages/", data);
    }

    update(id, data) {
        return Vue.http.patch(`/api/v1/additional_data/villages/${id}/`, data);
    }

    delete(id) {
        return Vue.http.delete(`/api/v1/additional_data/villages/${id}/`);
    }

}

window.VillageDataService = new VillageDataServiceClass();