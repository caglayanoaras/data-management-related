import { BaseGridManager } from './base-grid-manager.js';

const grid = document.querySelector("#laboratories-url");

export class LaboratoryManager extends BaseGridManager {
  constructor() {
    super("#laboratories-grid", ["id", "code", "name", "description", "divisions"]);
    this.tomSelectInstances = {
      divisions: null,
    };
  }

  async initializeTomSelects() {
    try {
      this.destroyTomSelects();

      const [divisionsData] = await Promise.all([
          this.fetchDivisions(),
      ]);
      this.tomSelectInstances.divisions = new TomSelect('#laboratories-divisions', {
          plugins: ['remove_button'],
          valueField: 'code',
          labelField: 'code',
          searchField: 'code',
          options: divisionsData,
          create: false,
          placeholder: 'Select divisions...'
      });


    } catch (error) {
      console.error("Error initializing Tom Select:", error);
    }
  }

  getEntityName() { return "Laboratory"; }

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
      addBtn: "laboratories-addBtn",
      saveBtn: "laboratories-saveLaboratoryBtn",
      modal: "laboratories-Modal",
      modalTitle: "laboratories-ModalTitle",
      form: "laboratories-Form"
    };
  }

  getFormData() {
    const formData = {
      code: document.getElementById("laboratories-code").value.trim(),
      name: document.getElementById("laboratories-name").value.trim(),
      description: document.getElementById("laboratories-description").value.trim(),
    };

    if (this.tomSelectInstances.divisions) {
      formData.divisions = this.tomSelectInstances.divisions.getValue();
    }
    return formData;
  }

  getCustomColumnDef(key) {

    if (key === "divisions") {
      return {
        field: "divisions",
        headerName: "DIVISIONS",
        valueGetter: (params) => `${params.data.divisions?.length || 0} division(s)`,
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
      { action: 'show-divisions', title: 'Show Divisions', icon: 'fas fa-building', variant: 'danger' },
    ];
  }

  getCustomActionHandler(action) {
    const handlers = {
      'show-divisions': (params) => this.showLaboratoryDivisions(params.data.divisions || []),
    };
    return handlers[action];
  }

  showLaboratoryDivisions(divisions) {
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
    document.getElementById("laboratories-code").value = data.code || "";
    document.getElementById("laboratories-name").value = data.name || "";
    document.getElementById("laboratories-description").value = data.description || "";


    this.populateTomSelects(data);
  }

  populateTomSelects(laboratoryData) {

    if (laboratoryData.divisions && this.tomSelectInstances.divisions) {
      const divisionCodes = laboratoryData.divisions.map(division => division.code);
      this.tomSelectInstances.divisions.setValue(divisionCodes);
    }
  }

  // Alias for backwards compatibility
  loadLaboratories() { return this.loadData(); } 

}