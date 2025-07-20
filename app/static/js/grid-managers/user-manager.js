import { BaseGridManager } from './base-grid-manager.js';

const grid = document.querySelector("#users-url");

export class UserManager extends BaseGridManager {
  constructor() {
    super("#users-grid", ["id", "is_active", "username", "name", "surname", "email", "usertype", "title", "roles", "skills", "divisions", "modules"]);
    this.tomSelectInstances = {
      roles: null,
      skills: null,
      divisions: null,
      modules: null
    };
  }

  async initializeTomSelects() {
    try {
      this.destroyTomSelects();

      const [rolesData, skillsData, divisionsData, modulesData] = await Promise.all([
          this.fetchRoles(),
          this.fetchSkills(),
          this.fetchDivisions(),
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
      this.tomSelectInstances.divisions = new TomSelect('#users-divisions', {
        plugins: ['remove_button'],
        valueField: 'code',
        labelField: 'code',
        searchField: 'code',
        options: divisionsData,
        create: false,
        placeholder: 'Select divisions...'
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

  getEntityName() { return "User"; }

  getUpdateIdentifier(data) { 
    return data.username; 
  }

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
    if (this.tomSelectInstances.divisions) {
      formData.divisions = this.tomSelectInstances.divisions.getValue();
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

    if (key === "divisions") {
      return {
        field: "divisions",
        headerName: "DIVISION(S)",
        valueGetter: (params) => {
          const divisions = params.data.divisions;
          if (!divisions || !Array.isArray(divisions) || divisions.length === 0) {
            return 'No divisions';
          }
          return divisions.map(division => division.code).join(', ');
        },
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
    this.showItemsInModal(roles, "Roles");
  }

  showUserSkills(skills) {
    this.showItemsInModal(skills, "Skills");
  }

  showUserModules(modules) {
    this.showItemsInModal(modules, "Modules");
  }

  validateFormData(formData, isEdit = false) {
    if (!formData.username) {
        alert("Username is required");
        return false;
    }
    if (!formData.email) {
        alert("Email is required");
        return false;
    }
    if (!formData.name) {
        alert("First name is required");
        return false;
    }
    if (!formData.surname) {
        alert("Last name is required");
        return false;
    }
    if (!isEdit && !formData.pw) {
        alert("Password is required for new users");
        return false;
    }
    return true;
  }

  async fetchRoles() {
    const roleGrid = document.querySelector("#user-roles-url");
    const response = await fetch(roleGrid.dataset.urlGetAll, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to fetch roles');
    return await response.json();
  }

  async fetchSkills() {
    const skillGrid = document.querySelector("#user-skills-url");
      const response = await fetch(skillGrid.dataset.urlGetAll, {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
      });
      if (!response.ok) throw new Error('Failed to fetch skills');
      return await response.json();
  }

  async fetchModules() {
    const moduleGrid = document.querySelector("#user-modules-url");
    const response = await fetch(moduleGrid.dataset.urlGetAll, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to fetch modules');
    return await response.json();
  }
  async fetchDivisions() {
    const moduleGrid = document.querySelector("#divisions-url");
    const response = await fetch(moduleGrid.dataset.urlGetAll, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });
    if (!response.ok) throw new Error('Failed to fetch divisions');
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
    if (userData.divisions && this.tomSelectInstances.divisions) {
      const divisionCodes = userData.divisions.map(division => division.code);
      this.tomSelectInstances.divisions.setValue(divisionCodes);
    }
  }

  // Alias for backwards compatibility
  loadUsers() { return this.loadData(); } 
}