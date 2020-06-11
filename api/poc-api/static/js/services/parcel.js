class ParcelDataServiceClass {
    getAll() {
        return Vue.http.get("/additional_data/parcels/");
    }

    getByID(id) {
        return Vue.http.get(`/additional_data/parcels/${id}/`);
    }

    create(data) {
        return Vue.http.post("/additional_data/parcels/", data);
    }

    update(id, data) {
        return Vue.http.patch(`/additional_data/parcels/${id}/`, data);
    }

    delete(id) {
        return Vue.http.delete(`/additional_data/parcels/${id}/`);
    }

}

window.ParcelDataService = new ParcelDataServiceClass();