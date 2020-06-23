class DestinationDataServiceClass {
    getAll() {
        return Vue.http.get("/api/v1/additional_data/destinations/");
    }

    getByID(id) {
        return Vue.http.get(`/api/v1/additional_data/destinations/${id}/`);
    }

    create(data) {
        return Vue.http.post("/api/v1/additional_data/destinations/", data);
    }

    update(id, data) {
        return Vue.http.patch(`/api/v1/additional_data/destinations/${id}/`, data);
    }

    delete(id) {
        return Vue.http.delete(`/api/v1/additional_data/destinations/${id}/`);
    }

}

window.DestinationDataService = new DestinationDataServiceClass();