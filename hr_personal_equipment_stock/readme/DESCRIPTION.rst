This module integrates stock with hr_personal_equipment_request module.
When the equipment request is accepted, a stock request is generated and a "stock.move" is created for each request line.
If the "stock.move" is marked as done, the corresponding allocations are marked as valid if the quantity_delivered is equal to the requested quantity.
In case a service is added to the equipment request, it will skip the procurement method. Instead, it has to be validated from the corresponding allocation.
In case a backorder is generated and cancelled afterwards, if qty_delivered is not null, the allocation is marked as valid. If not, it is marked as cancelled.
