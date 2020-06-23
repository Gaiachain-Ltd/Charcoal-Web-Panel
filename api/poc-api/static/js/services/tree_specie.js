class TreeSpecieDataServiceClass {
    getAll() {
        return Vue.http.get("/api/v1/additional_data/tree-species/");
    }

    getByID(id) {
        return Vue.http.get(`/api/v1/additional_data/tree-species/${id}/`);
    }

    create(data) {
        return Vue.http.post("/api/v1/additional_data/tree-species/", data);
    }

    update(id, data) {
        return Vue.http.patch(`/api/v1/additional_data/tree-species/${id}/`, data);
    }

    delete(id) {
        return Vue.http.delete(`/api/v1/additional_data/tree-species/${id}/`);
    }

}

window.TreeSpecieDataService = new TreeSpecieDataServiceClass();