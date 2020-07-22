class ParcelDataServiceClass {
    getAll() {
        return Vue.http.get("/api/v1/additional_data/parcels/?active_only=1");
    }

    getByID(id) {
        return Vue.http.get(`/api/v1/additional_data/parcels/${id}/`);
    }

    create(data) {
        return Vue.http.post("/api/v1/additional_data/parcels/", data);
    }

    update(id, data) {
        return Vue.http.patch(`/api/v1/additional_data/parcels/${id}/`, data);
    }

    delete(id) {
        return Vue.http.delete(`/api/v1/additional_data/parcels/${id}/`);
    }

}

window.ParcelDataService = new ParcelDataServiceClass();