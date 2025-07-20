import { BaseGridManager } from './base-grid-manager.js';

const grid = document.querySelector("#divisions-url");

export class DivisionManager extends BaseGridManager {
  constructor() {
    super("#divisions-grid", ["id", "code", "name", "description", "laboratories","warehouses", "users"]);
    this.tomSelectInstances = {
      laboratories: null,
      warehouses: null,
      users: null,
    };
  }

  async initializeTomSelects() {
    try {
      this.destroyTomSelects();

      const [laboratoriesData, warehousesData, usersData] = await Promise.all([
          this.fetchLaboratories(),
          this.fetchWarehouses(),
          this.fetchUsers()
      ]);
      this.tomSelectInstances.laboratories = new TomSelect('#divisions-laboratories', {
          plugins: ['remove_button'],
          valueField: 'code',
          labelField: 'name',
          searchField: 'name',
          options: laboratoriesData,
          create: false,
          placeholder: 'Select laboratories...'
      });

      this.tomSelectInstances.warehouses = new TomSelect('#divisions-warehouses', {
          plugins: ['remove_button'],
          valueField: 'code',
          labelField: 'name',
          searchField: 'name',
          options: warehousesData,
          create: false,
          placeholder: 'Select warehouses...'
      });

      this.tomSelectInstances.users = new TomSelect('#divisions-users', {
        plugins: ['remove_button'],
        valueField: 'username',
        labelField: 'username',
        searchField: 'username',
        options: usersData,
        create: false,
        placeholder: 'Select users...'
    });
    } catch (error) {
      console.error("Error initializing Tom Select:", error);
    }
  }

  getEntityName() { return "Division"; }

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
      addBtn: "divisions-addBtn",
      saveBtn: "divisions-saveDivisionBtn",
      modal: "divisions-Modal",
      modalTitle: "divisions-ModalTitle",
      form: "divisions-Form"
    };
  }

  getFormData() {
    const formData = {
      code: document.getElementById("divisions-code").value.trim(),
      name: document.getElementById("divisions-name").value.trim(),
      description: document.getElementById("divisions-description").value.trim(),
    };

    if (this.tomSelectInstances.laboratories) {
      formData.laboratories = this.tomSelectInstances.laboratories.getValue();
    }
    if (this.tomSelectInstances.warehouses) {
      formData.warehouses = this.tomSelectInstances.warehouses.getValue();
    }
    if (this.tomSelectInstances.users) {
      formData.users = this.tomSelectInstances.users.getValue();
    }
    return formData;
  }

  getCustomColumnDef(key) {
    if (key === "users") {
      return {
        field: "users",
        headerName: "USERS",
        valueGetter: (params) => `${params.data.users?.length || 0} user(s)`,
        sortable: true,
        filter: false
      };
    }
    if (key === "laboratories") {
      return {
        field: "laboratories",
        headerName: "LABORATORIES",
        valueGetter: (params) => `${params.data.laboratories?.length || 0} laboratory(s)`,
        sortable: true,
        filter: false,
      };
    }
    if (key === "warehouses") {
      return {
        field: "warehouses",
        headerName: "WAREHOUSES",
        valueGetter: (params) => `${params.data.warehouses?.length || 0} warehouse(s)`,
        sortable: true,
        filter: false,
      };
    }
    return null;
  }

  getActionButtons() {
    return [
      { action: 'edit', title: 'Edit', icon: 'fas fa-edit', variant: 'primary' },
      { action: 'delete', title: 'Delete', icon: 'fas fa-trash-alt', variant: 'danger' },
      { action: 'show-laboratories', title: 'Show Laboratories', icon: 'fas fa-flask-vial', variant: 'success' },
      { action: 'show-warehouses', title: 'Show Warehouses', icon: 'fas fa-warehouse', variant: 'warning' },
      { action: 'show-users', title: 'Show Users', icon: 'fas fa-users', variant: 'primary' },
    ];
  }

  getCustomActionHandler(action) {
    const handlers = {
      'show-laboratories': (params) => this.showDivisionLaboratories(params.data.laboratories || []),
      'show-warehouses': (params) => this.showDivisionWarehouses(params.data.warehouses || []),
    };
    return handlers[action];
  } 

  showDivisionLaboratories(laboratories) {
    this.showItemsInModal(laboratories, "Laboratories");
  }
  showDivisionWarehouses(warehouses) {
    this.showItemsInModal(warehouses, "Warehouses");
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


  async fetchLaboratories() {
    const grid = document.querySelector("#laboratories-url");
    const response = await fetch(grid.dataset.urlGetAll, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to fetch laboratories');
    return await response.json();
  }

  async fetchWarehouses() {
    const grid = document.querySelector("#warehouses-url");
      const response = await fetch(grid.dataset.urlGetAll, {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
      });
      if (!response.ok) throw new Error('Failed to fetch warehouses');
      return await response.json();
  }
  async fetchUsers() {
    const grid = document.querySelector("#users-url");
      const response = await fetch(grid.dataset.urlGetAll, {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
      });
      if (!response.ok) throw new Error('Failed to fetch users');
      return await response.json();
  }

  populateForm(data) {
    document.getElementById("divisions-code").value = data.code || "";
    document.getElementById("divisions-name").value = data.name || "";
    document.getElementById("divisions-description").value = data.description || "";


    this.populateTomSelects(data);
  }

  populateTomSelects(divisionData) {
    if (divisionData.laboratories && this.tomSelectInstances.laboratories) {
      const labCodes = divisionData.laboratories.map(laboratory => laboratory.code);
      this.tomSelectInstances.laboratories.setValue(labCodes);
    }

    if (divisionData.warehouses && this.tomSelectInstances.warehouses) {
      const warehouseCodes = divisionData.warehouses.map(warehouse => warehouse.code);
      this.tomSelectInstances.warehouses.setValue(warehouseCodes);
    }
    if (divisionData.users && this.tomSelectInstances.users) {
      const userNames = divisionData.users.map(user => user.username);
      this.tomSelectInstances.users.setValue(userNames);
    }
  }

  // Alias for backwards compatibility
  loadDivisions() { return this.loadData(); } 
}