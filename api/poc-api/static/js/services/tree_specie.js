class TreeSpecieDataServiceClass {
    getAll() {
        return Vue.http.get("/additional_data/tree-species/");
    }

    getByID(id) {
        return Vue.http.get(`/additional_data/tree-species/${id}/`);
    }

    create(data) {
        return Vue.http.post("/additional_data/tree-species/", data);
    }

    update(id, data) {
        return Vue.http.patch(`/additional_data/tree-species/${id}/`, data);
    }

    delete(id) {
        return Vue.http.delete(`/additional_data/tree-species/${id}/`);
    }

}

window.TreeSpecieDataService = new TreeSpecieDataServiceClass();