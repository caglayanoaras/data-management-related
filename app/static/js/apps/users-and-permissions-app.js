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
        this.userRoleManager = new UserRoleManager();
        this.userSkillManager = new UserSkillManager();
        this.userModuleManager = new UserModuleManager();
        this.userManager = new UserManager();

        this.sidebarManager = new UsersAndPermissionsSidebarManager({
            userRoleManager: this.userRoleManager,
            userSkillManager: this.userSkillManager,
            userModuleManager: this.userModuleManager,
            userManager: this.userManager
        });
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  window.usersPermissionsApp = new UsersPermissionsApp();
});