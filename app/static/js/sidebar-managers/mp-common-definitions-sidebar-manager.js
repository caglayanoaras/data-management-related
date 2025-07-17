export class MpCommonDefinitionsSidebarManager {
    constructor({ divisionManager, laboratoryManager, locationManager, warehouseManager, materialTypeManager, materialManager, materialInstanceManager }) {
			this.divisionManager = divisionManager;
			this.laboratoryManager = laboratoryManager;
			this.locationManager = locationManager;
			this.warehouseManager = warehouseManager;
			this.materialTypeManager = materialTypeManager;
			this.materialManager = materialManager;
			this.materialInstanceManager = materialInstanceManager;
  
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
				case 'divisions':
					this.divisionManager?.loadDivisions?.();
					break;
				case 'laboratories':
					this.laboratoryManager?.loadLaboratories?.();
					break;
				case 'locations':
					this.locationManager?.loadLocations?.();
					break;
				case 'warehouses':
					this.warehouseManager?.loadWarehouses?.();
					break;
				case 'material-types':
					this.materialTypeManager?.loadMaterialTypes?.();
					break;
				case 'materials':
					this.materialManager?.loadMaterials?.();
					break;
				case 'material-instances':
					this.materialInstanceManager?.loadMaterialInstances?.();
					break;
      }
    }
  }