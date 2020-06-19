class VillageDataServiceClass {
    getAll() {
        return Vue.http.get("/additional_data/villages/");
    }

    getByID(id) {
        return Vue.http.get(`/additional_data/villages/${id}/`);
    }

    create(data) {
        return Vue.http.post("/additional_data/villages/", data);
    }

    update(id, data) {
        return Vue.http.patch(`/additional_data/villages/${id}/`, data);
    }

    delete(id) {
        return Vue.http.delete(`/additional_data/villages/${id}/`);
    }

}

window.VillageDataService = new VillageDataServiceClass();