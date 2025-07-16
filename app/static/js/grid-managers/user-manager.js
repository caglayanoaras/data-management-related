import { BaseGridManager } from './base-grid-manager.js';

const grid = document.querySelector("#users-url");

export class UserManager extends BaseGridManager {
  constructor() {
    super("#users-grid", ["id", "is_active", "username", "name", "surname", "email", "usertype", "title", "roles", "skills", "modules"]);
    this.tomSelectInstances = {
      roles: null,
      skills: null,
      modules: null
    };
  }

  getEntityName() { return "User"; }

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
      addBtn: "users-addUserBtn",
      saveBtn: "users-saveUserBtn",
      modal: "users-Modal",
      modalTitle: "users-ModalTitle",
      form: "users-Form"
    };
  }

  getFormData() {
    const formData = {
      username: document.getElementById("users-username").value.trim(),
      email: document.getElementById("users-email").value.trim(),
      name: document.getElementById("users-name").value.trim(),
      surname: document.getElementById("users-surname").value.trim(),
      usertype: document.getElementById("users-usertype").value,
      is_active: document.getElementById("users-isActive").checked,
      title: document.getElementById("users-title").value.trim()
    };

    const password = document.getElementById("users-password").value;
    if (password) {
      formData.pw = password;
    }

    if (this.tomSelectInstances.roles) {
      formData.roles = this.tomSelectInstances.roles.getValue().map(id => parseInt(id));
    }
    if (this.tomSelectInstances.skills) {
      formData.skills = this.tomSelectInstances.skills.getValue().map(id => parseInt(id));
    }
    if (this.tomSelectInstances.modules) {
      formData.modules = this.tomSelectInstances.modules.getValue().map(id => parseInt(id));
    }

    return formData;
  }

  getCustomColumnDef(key) {
    if (key === "roles") {
      return {
        field: "roles",
        headerName: "ROLES",
        valueGetter: (params) => `${params.data.roles?.length || 0} role(s)`,
        sortable: true,
        filter: false,
        minWidth: 120,
        hide: true
      };
    }

    if (key === "skills") {
      return {
        field: "skills",
        headerName: "SKILLS",
        valueGetter: (params) => `${params.data.skills?.length || 0} skill(s)`,
        sortable: true,
        filter: false,
        minWidth: 120,
        hide: true
      };
    }

    if (key === "modules") {
      return {
        field: "modules",
        headerName: "MODULES",
        valueGetter: (params) => `${params.data.modules?.length || 0} module(s)`,
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
      { action: 'show-roles', title: 'Show Roles', icon: 'fas fa-user-shield', variant: 'success' },
      { action: 'show-skills', title: 'Show Skills', icon: 'fas fa-hammer', variant: 'warning' },
      { action: 'show-modules', title: 'Show Modules', icon: 'fas fa-gears', variant: 'secondary' }
    ];
  }

  getCustomActionHandler(action) {
    const handlers = {
      'show-roles': (params) => this.showUserRoles(params.data.roles || []),
      'show-skills': (params) => this.showUserSkills(params.data.skills || []),
      'show-modules': (params) => this.showUserModules(params.data.modules || [])
    };
    return handlers[action];
  } 

  showUserRoles(roles) {
    this.showItemsInModal(roles, "Roles", "role");
}

showUserSkills(skills) {
    this.showItemsInModal(skills, "Skills", "skill");
}

showUserModules(modules) {
    this.showItemsInModal(modules, "Modules", "module");
}

showItemsInModal(items, title, type) {
    const linksList = document.getElementById("linksList");
    const modalTitle = document.querySelector("#showLinksModal .modal-title");
    
    modalTitle.textContent = `User ${title} (${items.length})`;
    linksList.innerHTML = "";

    if (items.length === 0) {
      linksList.innerHTML = `<li class='list-group-item text-muted'>No ${type}s assigned</li>`;
    } else {
        items.forEach(item => {
            const listItem = this.createItemListItem(item, type);
            linksList.appendChild(listItem);
        });
    }

    const modal = bootstrap.Modal.getOrCreateInstance(
        document.getElementById("showLinksModal")
    );
    modal.show();
}

createItemListItem(item, type) {
    const li = document.createElement("li");
    li.className = "list-group-item";
    
    let content = '';
    if (type === 'role') {
        content = `
            <strong>${item.rolename}</strong>
            <div><small>${item.notes || 'No notes'}</small></div>
        `;
    } else if (type === 'skill') {
        content = `
            <strong>${item.skillname}</strong>
            <div><small>Level: ${item.skill_level || 'N/A'} | ${item.notes || 'No notes'}</small></div>
        `;
    } else if (type === 'module') {
        content = `
            <strong>${item.title}</strong>
            <div><small>${item.description || 'No description'}</small></div>
        `;
    }
    
    li.innerHTML = content;
    return li;
}






  async showModal(mode, params = null) {
    this.currentMode = mode;
    const elements = this.getFormElements();

    if (!this.modal) {
      this.modal = bootstrap.Modal.getOrCreateInstance(
        document.getElementById(elements.modal)
      );
    }

    // Initialize Tom Select instances
    await this.initializeTomSelects();

    const form = document.getElementById(elements.form);
    const titleEl = document.getElementById(elements.modalTitle);
    const primaryEl = document.getElementById(elements.saveBtn);

    if (mode === "add") {
      form.reset();
      titleEl.textContent = "Add New User";
      primaryEl.innerHTML = '<i class="fas fa-plus me-1"></i> Create User';
      
      this.clearTomSelects();
      document.getElementById("users-password").required = true;
    } else {
      this.gridDiv.__pendingEdit = {
        id: params.data.username, // Use username for users
        rowData: params.data,
        rowNode: params.node
      };

      titleEl.textContent = "Edit User";
      primaryEl.innerHTML = '<i class="fas fa-save me-1"></i> Save Changes';

      this.populateForm(params.data);
      document.getElementById("users-password").required = false;
    }

    this.modal.show();
  }

  async initializeTomSelects() {
    try {
      this.destroyTomSelects();

      const [rolesData, skillsData, modulesData] = await Promise.all([
          this.fetchRoles(),
          this.fetchSkills(),
          this.fetchModules()
      ]);

      this.tomSelectInstances.roles = new TomSelect('#users-roles', {
          plugins: ['remove_button'],
          valueField: 'id',
          labelField: 'rolename',
          searchField: 'rolename',
          options: rolesData,
          create: false,
          placeholder: 'Select roles...'
      });

      this.tomSelectInstances.skills = new TomSelect('#users-skills', {
          plugins: ['remove_button'],
          valueField: 'id',
          labelField: 'skillname',
          searchField: 'skillname',
          options: skillsData,
          create: false,
          placeholder: 'Select skills...'
      });

      this.tomSelectInstances.modules = new TomSelect('#users-modules', {
          plugins: ['remove_button'],
          valueField: 'id',
          labelField: 'title',
          searchField: 'title',
          options: modulesData,
          create: false,
          placeholder: 'Select modules...'
      });

    } catch (error) {
      console.error("Error initializing Tom Select:", error);
    }
  }

  destroyTomSelects() {
    Object.values(this.tomSelectInstances).forEach(instance => {
      if (instance) {
        instance.destroy();
      }
    });
    this.tomSelectInstances = { roles: null, skills: null, modules: null };
  }

  clearTomSelects() {
    Object.values(this.tomSelectInstances).forEach(instance => {
      if (instance) {
        instance.clear();
      }
    });
  }

  async fetchRoles() {
    const response = await fetch("{{ url_for('get_all_user_roles') }}", {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to fetch roles');
    return await response.json();
  }

  async fetchSkills() {
      const response = await fetch("{{ url_for('get_all_user_skills') }}", {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
      });
      if (!response.ok) throw new Error('Failed to fetch skills');
      return await response.json();
  }

  async fetchModules() {
    const response = await fetch("{{ url_for('get_all_modules') }}", {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to fetch modules');
    return await response.json();
  }

  populateForm(data) {
    document.getElementById("users-username").value = data.username || "";
    document.getElementById("users-email").value = data.email || "";
    document.getElementById("users-name").value = data.name || "";
    document.getElementById("users-surname").value = data.surname || "";
    document.getElementById("users-usertype").value = data.usertype || "user";
    document.getElementById("users-isActive").checked = !!data.is_active;
    document.getElementById("users-title").value = data.title || "";
    document.getElementById("users-password").value = "";

    this.populateTomSelects(data);
  }

  populateTomSelects(userData) {
    if (userData.roles && this.tomSelectInstances.roles) {
      const roleIds = userData.roles.map(role => role.id.toString());
      this.tomSelectInstances.roles.setValue(roleIds);
    }

    if (userData.skills && this.tomSelectInstances.skills) {
      const skillIds = userData.skills.map(skill => skill.id.toString());
      this.tomSelectInstances.skills.setValue(skillIds);
    }

    if (userData.modules && this.tomSelectInstances.modules) {
      const moduleIds = userData.modules.map(module => module.id.toString());
      this.tomSelectInstances.modules.setValue(moduleIds);
    }
  }

  clearForm() {
    this.clearTomSelects();
  }

  getFormData() {
    const formData = {
      username: document.getElementById("users-username").value.trim(),
      email: document.getElementById("users-email").value.trim(),
      name: document.getElementById("users-name").value.trim(),
      surname: document.getElementById("users-surname").value.trim(),
      usertype: document.getElementById("users-usertype").value,
      is_active: document.getElementById("users-isActive").checked,
      title: document.getElementById("users-title").value.trim()
    };

    const password = document.getElementById("users-password").value;
    if (password) {
      formData.pw = password;
    }

    if (this.tomSelectInstances.roles) {
      formData.roles = this.tomSelectInstances.roles.getValue().map(id => parseInt(id));
    }
    if (this.tomSelectInstances.skills) {
      formData.skills = this.tomSelectInstances.skills.getValue().map(id => parseInt(id));
    }
    if (this.tomSelectInstances.modules) {
      formData.modules = this.tomSelectInstances.modules.getValue().map(id => parseInt(id));
    }

    return formData;
  }

}