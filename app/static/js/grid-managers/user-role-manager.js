import { BaseGridManager } from './base-grid-manager.js';

export class UserRoleManager extends BaseGridManager {
  constructor() {
    super("#user-roles-grid", ["id", "rolename", "can_create", "can_read", "can_update", "can_delete", "notes", "users"]);
  }

  getEntityName() { return "Role"; }

  getApiUrls() {
    return {
      getAll: "{{ url_for('get_all_user_roles') }}",
      create: "{{ url_for('create_new_user_role') }}",
      update: "{{ url_for('update_existing_user_role', role_id='PLACEHOLDER') }}",
      delete: "{{ url_for('delete_user_role_by_id', role_id='PLACEHOLDER') }}"
    };
  }

  getFormElements() {
    return {
      addBtn: "user-roles-addRoleBtn",
      saveBtn: "user-roles-saveRoleBtn",
      modal: "user-roles-roleModal",
      modalTitle: "user-roles-roleModalTitle",
      form: "user-roles-roleForm"
    };
  }

  getFormData() {
    return {
      rolename: document.getElementById("user-roles-roleName").value.trim(),
      notes: document.getElementById("user-roles-notes").value.trim(),
      can_create: document.getElementById("user-roles-canCreate").checked,
      can_read: document.getElementById("user-roles-canRead").checked,
      can_update: document.getElementById("user-roles-canUpdate").checked,
      can_delete: document.getElementById("user-roles-canDelete").checked
    };
  }

  validateFormData(formData) {
    if (!formData.rolename) {
      alert("Role name is required");
      return false;
    }
    return true;
  }

  populateForm(data) {
    document.getElementById("user-roles-roleName").value = data.rolename || "";
    document.getElementById("user-roles-notes").value = data.notes || "";
    document.getElementById("user-roles-canCreate").checked = !!data.can_create;
    document.getElementById("user-roles-canRead").checked = !!data.can_read;
    document.getElementById("user-roles-canUpdate").checked = !!data.can_update;
    document.getElementById("user-roles-canDelete").checked = !!data.can_delete;
  }

  // Alias for backwards compatibility
  loadRoles() { return this.loadData(); }
}