import { BaseGridManager } from './base-grid-manager.js';

const grid = document.querySelector("#locations-url");

export class LocationManager extends BaseGridManager {
  constructor() {
    super("#locations-grid", ["id", "code", "name", "address", "description", "warehouses"]);
  }

  getEntityName() { return "Location"; }

  getApiUrls() {
    return {
      getAll: grid.dataset.urlGetAll,
      create: grid.dataset.urlCreate,
      update: grid.dataset.urlUpdate,
      delete: grid.dataset.urlDelete
    };
  }

  getActionButtons() {
    return [
      { action: 'edit', title: 'Edit', icon: 'fas fa-edit', variant: 'primary' },
      { action: 'delete', title: 'Delete', icon: 'fas fa-trash-alt', variant: 'danger' },
      { action: 'show-warehouses', title: 'Show Warehouses', icon: 'fas fa-warehouse', variant: 'info' }
    ];
  }

  getCustomActionHandler(action) {
    const handlers = {
      'show-warehouses': (params) => this.showWarehouses(params.data.warehouses || [])
    };
    return handlers[action];
  }

  showWarehouses(warehouses) {
    this.showItemsInModal(warehouses, 'Warehouses');
  }

  getCustomColumnDef(key) {
    if (key === "warehouses") {
      return {
        field: "warehouses",
        headerName: "WAREHOUSES",
        valueGetter: (params) => `${params.data.warehouses?.length || 0} warehouse(s)`,
        sortable: true,
        filter: false,
      };
    }
  }

  getFormElements() {
    return {
      addBtn: "locations-addBtn",
      saveBtn: "locations-saveLocationBtn",
      modal: "locations-Modal",
      modalTitle: "locations-ModalTitle",
      form: "locations-Form"
    };
  }

  getFormData() {
    return {
        code: document.getElementById("locations-code").value.trim(),
        name: document.getElementById("locations-name").value.trim(),
        address: document.getElementById("locations-address").value,
        description: document.getElementById("locations-description").value,
    };
  }

  validateFormData(formData) {
    if (!formData.code) {
      alert("Location code is required");
      return false;
    }
    return true;
  }

  populateForm(data) {
    document.getElementById("locations-code").value = data.code || "";
    document.getElementById("locations-name").value = data.name || "";
    document.getElementById("locations-address").value = data.address || "";
    document.getElementById("locations-description").value = data.description || "";
  }

  // Alias for backwards compatibility
  loadLocations() { return this.loadData(); }
}