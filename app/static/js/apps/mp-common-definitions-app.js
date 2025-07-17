import { DivisionManager } from '../grid-managers/division-manager.js';
import { LaboratoryManager } from '../grid-managers/laboratory-manager.js';
import { LocationManager } from '../grid-managers/location-manager.js';
import { WarehouseManager } from '../grid-managers/warehouse-manager.js';
import { MaterialTypeManager } from '../grid-managers/material-type-manager.js';
import { MaterialManager } from '../grid-managers/material-manager.js';
import { MaterialInstanceManager } from '../grid-managers/material-instance-manager.js';

import { MpCommonDefinitionsSidebarManager } from '../sidebar-managers/mp-common-definitions-sidebar-manager.js';

class MpCommonDefinitionsApp {
    constructor() {
        this.initializeManagers();
    }

    initializeManagers() {
        // Initialize managers
        this.divisionManager = new DivisionManager();
        this.laboratoryManager = new LaboratoryManager();
        this.locationManager = new LocationManager();
        this.warehouseManager = new WarehouseManager();
        this.materialTypeManager = new MaterialTypeManager();
        this.materialManager = new MaterialManager();
        this.materialInstanceManager = new MaterialInstanceManager();

        this.sidebarManager = new MpCommonDefinitionsSidebarManager({
            divisionManager: this.divisionManager,
            laboratoryManager: this.laboratoryManager,
            locationManager: this.locationManager,
            warehouseManager: this.warehouseManager,
            materialTypeManager: this.materialTypeManager,
            materialManager: this.materialManager,
            materialInstanceManager: this.materialInstanceManager
        });
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  window.mpCommonDefinitionsApp = new MpCommonDefinitionsApp();
});