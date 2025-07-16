export class UsersAndPermissionsSidebarManager {
  constructor({ userRoleManager, userManager, userSkillManager, userModuleManager }) {
    this.userRoleManager = userRoleManager;
    this.userManager = userManager;
    this.userSkillManager = userSkillManager;
    this.userModuleManager = userModuleManager;

    this.sidebarButtons = document.querySelectorAll('.sidebar-btn');
    this.contentSections = document.querySelectorAll('.content-section');
    this.welcomeContent = document.getElementById('welcome-content');
    this.initializeEventListeners();
  }

  initializeEventListeners() {
    this.sidebarButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        this.handleSidebarClick(e.currentTarget);
      });
    });
  }

  handleSidebarClick(button) {
    const contentType = button.dataset.content;
    
    // Update active states
    this.sidebarButtons.forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
    
    // Hide all content
    this.welcomeContent.style.display = 'none';
    this.contentSections.forEach(section => section.style.display = 'none');
    
    // Show selected content
    const targetContent = document.getElementById(contentType + '-content');
    if (targetContent) {
      targetContent.style.display = 'block';
      this.handleContentTypeSpecificActions(contentType);
    }
  }

  handleContentTypeSpecificActions(contentType) {
    switch (contentType) {
      case 'user-roles':
        this.userRoleManager?.loadRoles?.();
        break;
      case 'users':
        this.userManager?.loadUsers?.();
        break;
      case 'user-skills':
        this.userSkillManager?.loadSkills?.();
        break;
      case 'modules':
        this.userModuleManager?.loadModules?.();
        break;
    }
  }
}