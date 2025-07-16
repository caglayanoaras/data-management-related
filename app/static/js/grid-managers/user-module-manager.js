import { BaseGridManager } from './base-grid-manager.js';

const grid = document.querySelector("#user-modules-url");


export class UserModuleManager extends BaseGridManager {
  constructor() {
    super("#user-modules-grid", ["id", "title", "description", "users"]);
  }

  getEntityName() { return "Module"; }

  getApiUrls() {
    return {
      getAll: grid.dataset.urlGetAll,
    };
  }

  getActionButtons() {
    return [
      { action: 'show-users', title: 'Show Users', icon: 'fas fa-user', variant: 'info' }
    ];
  }

  getFormElements() {
    return {}; // No form elements for read-only manager
  }

  getFormData() { return {}; }
  validateFormData() { return true; }

  initializeEventListeners() {
      // No event listeners for read-only manager
  }

  // Alias for backwards compatibility
  loadModules() { return this.loadData(); }
}