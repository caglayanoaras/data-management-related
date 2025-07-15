import { UserManager } from '../grid-managers/user-manager.js';
import { UserRoleManager } from '../grid-managers/user-role-manager.js';
import { UserModuleManager } from '../grid-managers/user-module-manager.js';
import { UserSkillManager } from '../grid-managers/user-skill-manager.js';
import { UsersAndPermissionsSidebarManager } from '../sidebar-managers/users-and-permissions-sidebar-manager.js';


class UsersPermissionsApp {
    constructor() {
        this.initializeManagers();
    }

    initializeManagers() {
        // Initialize managers
        this.sidebarManager = new UsersAndPermissionsSidebarManager();
        this.userRoleManager = new UserRoleManager();
        this.userSkillManager = new UserSkillManager();
        this.userModuleManager = new UserModuleManager();
        this.userManager = new UserManager();

        // Make managers globally accessible if needed
        window.userRoleManager = this.userRoleManager;
        window.userSkillManager = this.userSkillManager;
        window.sidebarManager = this.sidebarManager;
        window.userModuleManager = this.userModuleManager;
        window.userManager = this.userManager;
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  window.usersPermissionsApp = new UsersPermissionsApp();
});