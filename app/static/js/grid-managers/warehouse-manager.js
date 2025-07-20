import { BaseGridManager } from './base-grid-manager.js';

const grid = document.querySelector("#warehouses-url");

export class WarehouseManager extends BaseGridManager {
  constructor() {
    super("#warehouses-grid", ["id", "code", "name", "description","locations", "divisions"]);
    this.tomSelectInstances = {
      divisions: null,
      locations: null,
    };
  }

  async initializeTomSelects() {
    try {
      this.destroyTomSelects();

      const [divisionsData, locationsData] = await Promise.all([
          this.fetchDivisions(),
          this.fetchLocations()
      ]);
      this.tomSelectInstances.divisions = new TomSelect('#warehouses-divisions', {
          plugins: ['remove_button'],
          valueField: 'code',
          labelField: 'code',
          searchField: 'code',
          options: divisionsData,
          create: false,
          placeholder: 'Select divisions...'
      });

      this.tomSelectInstances.locations = new TomSelect('#warehouses-locations', {
          plugins: ['remove_button'],
          valueField: 'code',
          labelField: 'name',
          searchField: 'name',
          options: locationsData,
          create: false,
          placeholder: 'Select locations...'
      });

    } catch (error) {
      console.error("Error initializing Tom Select:", error);
    }
  }

  getEntityName() { return "Warehouse"; }

  getApiUrls() {
    return {
      getAll: grid.dataset.urlGetAll,
      create: grid.dataset.urlCreate,
      update: grid.dataset.urlUpdate,
      delete: grid.dataset.urlDelete
    };
  }

  getFormElements() {
    return {
      addBtn: "warehouses-addBtn",
      saveBtn: "warehouses-saveWarehouseBtn",
      modal: "warehouses-Modal",
      modalTitle: "warehouses-ModalTitle",
      form: "warehouses-Form"
    };
  }

  getFormData() {
    const formData = {
      code: document.getElementById("warehouses-code").value.trim(),
      name: document.getElementById("warehouses-name").value.trim(),
      description: document.getElementById("warehouses-description").value.trim(),
    };

    if (this.tomSelectInstances.divisions) {
      formData.divisions = this.tomSelectInstances.divisions.getValue();
    }
    if (this.tomSelectInstances.locations) {
      formData.locations = this.tomSelectInstances.locations.getValue();
    }
    return formData;
  }

  getCustomColumnDef(key) {
    if (key === "locations") {
      return {
        field: "locations",
        headerName: "LOCATIONS",
        valueGetter: (params) => `${params.data.locations?.length || 0} location(s)`,
        sortable: true,
        filter: false,
        minWidth: 120,
        hide: true
      };
    }

    if (key === "divisions") {
      return {
        field: "divisions",
        headerName: "DIVISIONS",
        valueGetter: (params) => `${params.data.divisions?.length || 0} division(s)`,
        sortable: true,
        filter: false,
        minWidth: 120,
        hide: true
      };
    }
    return null;
  }

  getActionButtons() {
    return [
      { action: 'edit', title: 'Edit', icon: 'fas fa-edit', variant: 'primary' },
      { action: 'delete', title: 'Delete', icon: 'fas fa-trash-alt', variant: 'danger' },
      { action: 'show-locations', title: 'Show Locations', icon: 'fas fa-location-dot', variant: 'warning' },
      { action: 'show-divisions', title: 'Show Divisions', icon: 'fas fa-building', variant: 'danger' },
    ];
  }

  getCustomActionHandler(action) {
    const handlers = {
      'show-locations': (params) => this.showWarehouseLocations(params.data.locations || []),
      'show-divisions': (params) => this.showWarehouseDivisions(params.data.divisions || []),
    };
    return handlers[action];
  } 

  showWarehouseLocations(locations) {
    this.showItemsInModal(locations, "Locations");
  }

  showWarehouseDivisions(divisions) {
    this.showItemsInModal(divisions, "Divisions");
  }

  validateFormData(formData, isEdit = false) {
    if (!formData.code) {
        alert("code is required");
        return false;
    }
    if (!formData.name) {
        alert("name is required");
        return false;
    }
    return true;
  }

  async fetchLocations() {
    const grid = document.querySelector("#locations-url");
    const response = await fetch(grid.dataset.urlGetAll, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to fetch locations');
    return await response.json();
  }

  async fetchDivisions() {
    const grid = document.querySelector("#divisions-url");
      const response = await fetch(grid.dataset.urlGetAll, {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
      });
      if (!response.ok) throw new Error('Failed to fetch divisions');
      return await response.json();
  }

  populateForm(data) {
    document.getElementById("warehouses-code").value = data.code || "";
    document.getElementById("warehouses-name").value = data.name || "";
    document.getElementById("warehouses-description").value = data.description || "";

    this.populateTomSelects(data);
  }

  populateTomSelects(warehouseData) {
    if (warehouseData.locations && this.tomSelectInstances.locations) {
      const roleCodes = warehouseData.locations.map(location => location.code);
      this.tomSelectInstances.locations.setValue(roleCodes);
    }

    if (warehouseData.divisions && this.tomSelectInstances.divisions) {
      const divisionCodes = warehouseData.divisions.map(division => division.code);
      this.tomSelectInstances.divisions.setValue(divisionCodes);
    }

  }

  // Alias for backwards compatibility
  loadWarehouses() { return this.loadData(); } 

}