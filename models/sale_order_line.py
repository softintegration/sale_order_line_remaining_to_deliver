# -*- coding: utf-8 -*-

from odoo import models,fields,api,_
from odoo.exceptions import UserError
STOCK_MOVE_PLANNED_TO_DELIVER_STATES = ('waiting','confirmed','assigned')

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    remaining_to_deliver = fields.Float(string='Remaining to deliver', compute='_get_remaining_to_deliver', store=True)

    @api.depends('product_uom_qty','qty_delivered','move_ids.state')
    def _get_remaining_to_deliver(self):
        for each in self:
            each.remaining_to_deliver = each._get_planned_to_deliver()

    def _related_moves(self):
        self.ensure_one()
        return self.mapped('move_ids')

    def _get_planned_to_deliver(self):
        """Computes the planned to deliver qty basing on the related moves
        """
        self.ensure_one()
        qty = 0.0
        for move in self._related_moves().filtered(lambda r: r.state in STOCK_MOVE_PLANNED_TO_DELIVER_STATES and not r.scrapped):
                if move.location_dest_id.usage == "customer":
                    if not move.origin_returned_move_id:
                        qty += move.product_uom._compute_quantity(move.product_uom_qty,self.product_uom)
        return qty