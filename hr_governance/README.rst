=====================
HR Governance
=====================


Features
========

Introduce a new way to visualize organization in form of a packed circle chart

## Chart

* **Visualize Organizational Hierarchy**: Only 1 root circle that defines the layout, with all other circles as its children, representing sub-hierarchies.
* **Navigation**:
  * The chart supports zooming in and out, along with dragging to explore different levels of detail.
* **Searching**:
  * Users can perform full-text searches within circle names, employee names, roles, expectations, and authorities to identify responsible roles or circles.
  * Autocomplete is also available.

## Form View

* A form view is shown on the side, displaying the current circle. A resizer bar is placed between the chart and the form for easy resizing.
* The UI in the form view adapts to display circle and role details based on the role type.
* Each modification of a circle or role is logged and visible using Odoo’s chatter.
* The hint/placeholder for the ``Raison d'être`` field dynamically updates based on the role type.

## Models

### On ``governance.circle`` model

* Manages the hierarchy of circles and their subcircles.
* Method ``get_hierarchy_data`` populates data for visualization.
* Method ``create`` is overridden to automatically support role creation.
  * When a role is created, structuring roles (if defined) are automatically created as subcircles.
  * To optimize performance, the result of ``_get_structuring_templates`` is cached and refreshed whenever a type is added or removed.
  * Constraint ``_check_member_ids``: validates that an assigned member to a role should be a part of its parent circle.

### On ``governance.role.type`` model

* ``get_default_type_id`` pre-fills the default type when the user clicks the Create Role button in the form view.

### On ``res.config.settings`` model

* Adds ``governance_check_grayscale`` option to convert all circles to grayscale.
* Adds ``governance_single_assignee_mode`` option to restrict each role to a single assignee.

## UI Components

### At ``src/views``

* ``CirclePackController`` facilitates the coordination between ``CirclePackModel`` and ``CirclePackRenderer``. It subscribes to the **update** event from the model to re-render the renderer whenever a user performs a search.
* ``CirclePackRenderer``: Generates the chart using D3.js, rendering the data passed from the controller.

### At ``src/components``

* ``CirclePackingColorList``: Replaces Odoo native colors for better appearance.
* ``DynamicTextHint``: Supports dynamic text hints based on the value of a field (in the form view, it's the placeholder field).
  * In this module, an example of the usage is in the ``governance_circle_view_form``.
* ``FormWrapperController``: Overrides Odoo's native FormController to enable synchronization with the chart.
  * Adds two buttons for creating circles and roles.
* ``Many2ManySearchBar``: Supports autocomplete for Many2Many (M2M) fields, treating them as Many2One (M2O) fields for search functionality.
