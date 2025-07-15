import { BaseGridManager } from './base-grid-manager.js';

export class UserModuleManager extends BaseGridManager {
    constructor() {
        super("#user-modules-grid", ["id", "title", "description", "users"]);
    }

    getEntityName() { return "Module"; }

    getApiUrls() {
        return {
            getAll: "{{ url_for('get_all_modules') }}"
        };
    }

    getFormElements() {
        return {}; // No form elements for read-only manager
    }

    getFormData() { return {}; }
    validateFormData() { return true; }

    getActionButtons() {
        return [
            { action: 'show-users', title: 'Show Users', icon: 'fas fa-user', variant: 'info' }
        ];
    }

    initializeEventListeners() {
        // No event listeners for read-only manager
    }

    // Alias for backwards compatibility
    loadModules() { return this.loadData(); }
}