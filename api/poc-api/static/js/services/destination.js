class DestinationDataServiceClass {
    getAll() {
        return Vue.http.get("/additional_data/destinations/");
    }

    getByID(id) {
        return Vue.http.get(`/additional_data/destinations/${id}/`);
    }

    create(data) {
        return Vue.http.post("/additional_data/destinations/", data);
    }

    update(id, data) {
        return Vue.http.patch(`/additional_data/destinations/${id}/`, data);
    }

    delete(id) {
        return Vue.http.delete(`/additional_data/destinations/${id}/`);
    }

}

window.DestinationDataService = new DestinationDataServiceClass();