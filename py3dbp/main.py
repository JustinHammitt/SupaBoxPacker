from .constants import RotationType, Axis
from .auxiliary_methods import intersect, set2Decimal
from decimal import Decimal, getcontext
import numpy as np
import copy
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D, art3d
from matplotlib.patches import Rectangle, Circle

# Set global context for decimal precision if needed
getcontext().prec = 28  # Adjust as needed

# Global variable for the external logger
external_logger = None

def set_external_logger(logger):
    global external_logger
    external_logger = logger
    if external_logger:
        external_logger.info('Logger correctly configured in the external module.')

# Example of using the logger in the external module
# external_logger.info('Logger correctly configured in the external module.')

DEFAULT_NUMBER_OF_DECIMALS = 0
START_POSITION = [Decimal('0'), Decimal('0'), Decimal('0')]

avg_density_coefficient = 0.00026  # kg/cm³
class Item:
    def __init__(self, WHD, weight=None, priority_level=100, updown=False, color="red", loadbear=None, item_id=None, item_name=None, typeof='cube', assigned_bin=None, packer=None):
        self.packer = packer if packer is not None else Packer.get_default_packer()
        if typeof not in ['cube', 'cylinder']:
            raise ValueError(f"Invalid item type: {typeof}. Must be 'cube' or 'cylinder'.")
        self.item_id = self.generate_unique_id(item_id)
        self.item_name = item_name if item_name else item_id
        self.typeof = typeof
        self.width = Decimal(str(WHD[0]))
        self.height = Decimal(str(WHD[1]))
        self.depth = Decimal(str(WHD[2]))
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS
        self.weight = Decimal(str(weight)) if weight else self.getVolume() * Decimal(str(avg_density_coefficient))
        self.priority_level = priority_level
        self.loadbear = loadbear if loadbear else self.weight # Load bearing capacity (in terms of kilos): if 0 it means that the item is non-stackable
        self.updown = updown if typeof == 'cube' else False
        self.color = color
        self.rotation_type = 0
        self.position = START_POSITION.copy()
        self.assigned_bin = assigned_bin

    def generate_unique_id(self, base_id):
        ''' Generate a unique ID if the base ID already exists '''
        existing_items_ids = self.packer.existing_items_ids
        if base_id and base_id not in existing_items_ids:
            existing_items_ids.add(base_id)
            return base_id

        counter = 1
        new_id = f"{base_id}{counter}"
        while new_id in existing_items_ids:
            counter += 1
            new_id = f"{base_id}{counter}"

        existing_items_ids.add(new_id)
        if external_logger:
            external_logger.warning(f'ID conflict for item {base_id}. Assigned new id: {new_id}')
        return new_id

    def formatNumbers(self, number_of_decimals):
        self.width = set2Decimal(self.width, number_of_decimals)
        self.height = set2Decimal(self.height, number_of_decimals)
        self.depth = set2Decimal(self.depth, number_of_decimals)
        self.weight = set2Decimal(self.weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals

    def string(self):
        return "%s(%sx%sx%s, weight: %s) pos(%s) rt(%s) vol(%s)" % (
            self.item_id, self.width, self.height, self.depth, self.weight,
            self.position, self.rotation_type, self.getVolume()
        )

    def getVolume(self):
        return set2Decimal(self.width * self.height * self.depth, self.number_of_decimals)

    def getMaxArea(self):
        a = sorted([self.width, self.height, self.depth], reverse=True) if self.updown else [self.width, self.height, self.depth]
        return set2Decimal(a[0] * a[1], self.number_of_decimals)

    def getDimension(self):
        ''' Rotation type '''
        if self.rotation_type == RotationType.RT_WHD:
            dimension = [self.width, self.height, self.depth]
        elif self.rotation_type == RotationType.RT_HWD:
            dimension = [self.height, self.width, self.depth]
        elif self.rotation_type == RotationType.RT_HDW:
            dimension = [self.height, self.depth, self.width]
        elif self.rotation_type == RotationType.RT_DHW:
            dimension = [self.depth, self.height, self.width]
        elif self.rotation_type == RotationType.RT_DWH:
            dimension = [self.depth, self.width, self.height]
        elif self.rotation_type == RotationType.RT_WDH:
            dimension = [self.width, self.depth, self.height]
        else:
            dimension = []

        return dimension

class Bin:
    def __init__(self, WHD, max_weight=10000000000000, bin_id=None, bin_name=None, corner=0, put_type=1, packer=None):
        self.packer = packer if packer is not None else Packer.get_default_packer()
        self.bin_id = self.generate_unique_id(bin_id)
        self.width = Decimal(str(WHD[0]))
        self.height = Decimal(str(WHD[1]))
        self.depth = Decimal(str(WHD[2]))
        self.max_weight = Decimal(str(max_weight))
        self.corner = Decimal(str(corner))
        self.items = []
        self.fit_items = np.array([[Decimal('0'), self.width, Decimal('0'), self.height, Decimal('0'), Decimal('0')]], dtype=object)
        self.unfitted_items = []
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS
        self.fix_point = True
        self.check_stable = False
        self.support_surface_ratio = Decimal('0')
        self.put_type = put_type
        # used to put gravity distribution
        self.gravity = []
        self.bin_name = bin_name if bin_name else bin_id

    def generate_unique_id(self, base_id):
        ''' Generate a unique id if the base id already exists '''
        existing_bins_ids = self.packer.existing_bins_ids
        if base_id and base_id not in existing_bins_ids:
            existing_bins_ids.add(base_id)
            return base_id

        counter = 1
        new_id = f"{base_id}{counter}"
        while new_id in existing_bins_ids:
            counter += 1
            new_id = f"{base_id}{counter}"

        existing_bins_ids.add(new_id)
        if external_logger:
            external_logger.warning(f'ID conflict for bin {base_id}. Assigned new id: {new_id}')
        return new_id

    def formatNumbers(self, number_of_decimals):
        self.width = set2Decimal(self.width, number_of_decimals)
        self.height = set2Decimal(self.height, number_of_decimals)
        self.depth = set2Decimal(self.depth, number_of_decimals)
        self.max_weight = set2Decimal(self.max_weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals

    def string(self):
        return "%s(%sx%sx%s, max_weight:%s) vol(%s)" % (
            self.bin_id, self.width, self.height, self.depth, self.max_weight,
            self.getVolume()
        )

    def getVolume(self):
        return set2Decimal(
            self.width * self.height * self.depth, self.number_of_decimals
        )

    def getTotalWeight(self):
        total_weight = Decimal('0')

        for item in self.items:
            total_weight += item.weight

        return set2Decimal(total_weight, self.number_of_decimals)

    def putItem(self, item, pivot, axis=None):
        ''' Put item in bin '''
        fit = False
        valid_item_position = item.position.copy()
        item.position = pivot.copy()
        rotate = RotationType.ALL if item.updown else RotationType.Notupdown
        for i in range(0, len(rotate)):
            item.rotation_type = i
            dimension = item.getDimension()
            # Check if item exceeds bin boundaries after rotation
            if (
                self.width < pivot[0] + dimension[0] or
                self.height < pivot[1] + dimension[1] or
                self.depth < pivot[2] + dimension[2]
            ):
                continue

            fit = True

            # Check for intersection with items already in the bin
            for current_item_in_bin in self.items:
                if intersect(current_item_in_bin, item):
                    fit = False
                    break

            if fit:
                # Check if total weight exceeds bin's maximum weight
                if self.getTotalWeight() + item.weight > self.max_weight:
                    fit = False
                    return fit

                # Fix positioning issues
                if self.fix_point:
                    [w, h, d] = dimension
                    [x, y, z] = pivot.copy()

                    for _ in range(3):
                        # fix height
                        y = self.checkHeight([x, x + w, y, y + h, z, z + d])
                        # fix width
                        x = self.checkWidth([x, x + w, y, y + h, z, z + d])
                        # fix depth
                        z = self.checkDepth([x, x + w, y, y + h, z, z + d])

                    # Check stability of the item
                    # Rule:
                    # 1. Define a support ratio, if the ratio below the support surface does not exceed this ratio, compare the second rule.
                    # 2. If there is no support under any vertices of the bottom of the item, then fit = False.
                    if self.check_stable:
                        # Calculate the surface area of item's bottom
                        item_area_lower = dimension[0] * dimension[1]
                        # Calculate the surface area of the underlying support
                        support_area_upper = Decimal('0')
                        for i in self.fit_items:
                            # Verify that the lower support surface area is greater than the upper support surface area * support_surface_ratio.
                            if z == i[5]:
                                x_overlap = max(Decimal('0'), min(x + w, i[1]) - max(x, i[0]))
                                y_overlap = max(Decimal('0'), min(y + h, i[3]) - max(y, i[2]))
                                area = x_overlap * y_overlap
                                support_area_upper += area

                        # If not, get four vertices of the bottom of the item
                        if support_area_upper / item_area_lower < self.support_surface_ratio:
                            four_vertices = [
                                (x, y),
                                (x + w, y),
                                (x, y + h),
                                (x + w, y + h)
                            ]
                            # If any vertices are not supported, fit = False
                            c = [False, False, False, False]
                            for i in self.fit_items:
                                if z == i[5]:
                                    for idx, vertex in enumerate(four_vertices):
                                        if (i[0] <= vertex[0] <= i[1]) and (i[2] <= vertex[1] <= i[3]):
                                            c[idx] = True
                            if False in c:
                                item.position = valid_item_position
                                fit = False
                                return fit

                    # Load-bearing capacity check
                    bottom_y = y  # Bottom y-coordinate of the item being placed
                    can_support = True
                    tolerance = Decimal('1e-6')  # Tolerance for decimal comparison

                    for supporting_item in self.items:
                        supporting_item_top_y = supporting_item.position[1] + supporting_item.getDimension()[1]

                        if abs(supporting_item_top_y - bottom_y) < tolerance:
                            # Check overlap in x and z axes
                            item_x_range = (x, x + w)
                            item_z_range = (z, z + d)

                            supporting_x = supporting_item.position[0]
                            supporting_z = supporting_item.position[2]
                            supporting_w, _, supporting_d = supporting_item.getDimension()
                            supporting_x_range = (supporting_x, supporting_x + supporting_w)
                            supporting_z_range = (supporting_z, supporting_z + supporting_d)

                            x_overlap = max(Decimal('0'), min(item_x_range[1], supporting_x_range[1]) - max(item_x_range[0], supporting_x_range[0]))
                            z_overlap = max(Decimal('0'), min(item_z_range[1], supporting_z_range[1]) - max(item_z_range[0], supporting_z_range[0]))

                            if x_overlap > 0 and z_overlap > 0:
                                # Check cumulative load-bearing capacity
                                cumulative_weight = self.get_cumulative_weight_above(supporting_item, item)
                                if supporting_item.loadbear == 0 or supporting_item.loadbear < cumulative_weight:
                                    can_support = False
                                    break

                    if not can_support:
                        fit = False
                        item.position = valid_item_position
                        if external_logger:
                            external_logger.info(f"Item {item.item_id} cannot be placed on top of items that cannot bear its cumulative load")
                        continue  # Try next rotation or pivot

                    # Record the item's position in the bin
                    new_fit_item = np.array([[x, x + w, y, y + h, z, z + d]], dtype=object)
                    self.fit_items = np.append(self.fit_items, new_fit_item, axis=0)
                    item.position = [set2Decimal(coord, self.number_of_decimals) for coord in [x, y, z]]

                if fit:
                    self.items.append(copy.deepcopy(item))

            else:
                item.position = valid_item_position

            return fit

    def is_directly_supported_by(self, item_above, item_below):
        ''' Check if item_above is directly supported by item_below '''
        tolerance = Decimal('1e-6')
        item_below_top_y = item_below.position[1] + item_below.getDimension()[1]
        item_above_bottom_y = item_above.position[1]

        if abs(item_below_top_y - item_above_bottom_y) < tolerance:
            # Check overlap in x and z axes
            item_above_x_range = (item_above.position[0], item_above.position[0] + item_above.getDimension()[0])
            item_above_z_range = (item_above.position[2], item_above.position[2] + item_above.getDimension()[2])

            item_below_x_range = (item_below.position[0], item_below.position[0] + item_below.getDimension()[0])
            item_below_z_range = (item_below.position[2], item_below.position[2] + item_below.getDimension()[2])

            x_overlap = max(Decimal('0'), min(item_above_x_range[1], item_below_x_range[1]) - max(item_above_x_range[0], item_below_x_range[0]))
            z_overlap = max(Decimal('0'), min(item_above_z_range[1], item_below_z_range[1]) - max(item_above_z_range[0], item_below_z_range[0]))

            if x_overlap > 0 and z_overlap > 0:
                return True
        return False

    def get_cumulative_weight_above(self, supporting_item, current_item):
        ''' Calculate the cumulative weight of all items above supporting_item, including current_item '''
        cumulative_weight = Decimal('0')
        items_to_check = [supporting_item]
        visited = set()
        while items_to_check:
            item = items_to_check.pop()
            if item in visited:
                continue
            visited.add(item)
            for item_above in self.items + [current_item]:
                if item_above == supporting_item or item_above in visited:
                    continue
                if self.is_directly_supported_by(item_above, item):
                    cumulative_weight += item_above.weight
                    items_to_check.append(item_above)
        return cumulative_weight

    def checkDepth(self, unfix_point):
        ''' Fix item position z '''
        z_intervals = [[Decimal('0'), Decimal('0')], [self.depth, self.depth]]
        for j in self.fit_items:
            # x intervals
            x_bottom = (j[0], j[1])
            x_top = (unfix_point[0], unfix_point[1])
            # y intervals
            y_bottom = (j[2], j[3])
            y_top = (unfix_point[2], unfix_point[3])
            # Check for overlap
            x_overlap = max(Decimal('0'), min(x_bottom[1], x_top[1]) - max(x_bottom[0], x_top[0]))
            y_overlap = max(Decimal('0'), min(y_bottom[1], y_top[1]) - max(y_bottom[0], y_top[0]))
            if x_overlap > 0 and y_overlap > 0:
                z_intervals.append([j[4], j[5]])
        top_depth = unfix_point[5] - unfix_point[4]
        z_intervals = sorted(z_intervals, key=lambda z_: z_[1])
        for j in range(len(z_intervals) - 1):
            if z_intervals[j + 1][0] - z_intervals[j][1] >= top_depth:
                return z_intervals[j][1]
        return unfix_point[4]

    def checkWidth(self, unfix_point):
        ''' Fix item position x '''
        x_intervals = [[Decimal('0'), Decimal('0')], [self.width, self.width]]
        for j in self.fit_items:
            # z intervals
            z_bottom = (j[4], j[5])
            z_top = (unfix_point[4], unfix_point[5])
            # y intervals
            y_bottom = (j[2], j[3])
            y_top = (unfix_point[2], unfix_point[3])
            # Check for overlap
            z_overlap = max(Decimal('0'), min(z_bottom[1], z_top[1]) - max(z_bottom[0], z_top[0]))
            y_overlap = max(Decimal('0'), min(y_bottom[1], y_top[1]) - max(y_bottom[0], y_top[0]))
            if z_overlap > 0 and y_overlap > 0:
                x_intervals.append([j[0], j[1]])
        top_width = unfix_point[1] - unfix_point[0]
        x_intervals = sorted(x_intervals, key=lambda x_: x_[1])
        for j in range(len(x_intervals) - 1):
            if x_intervals[j + 1][0] - x_intervals[j][1] >= top_width:
                return x_intervals[j][1]
        return unfix_point[0]

    def checkHeight(self, unfix_point):
        ''' Fix item position y '''
        y_intervals = [[Decimal('0'), Decimal('0')], [self.height, self.height]]
        for j in self.fit_items:
            # x intervals
            x_bottom = (j[0], j[1])
            x_top = (unfix_point[0], unfix_point[1])
            # z intervals
            z_bottom = (j[4], j[5])
            z_top = (unfix_point[4], unfix_point[5])
            # Check for overlap
            x_overlap = max(Decimal('0'), min(x_bottom[1], x_top[1]) - max(x_bottom[0], x_top[0]))
            z_overlap = max(Decimal('0'), min(z_bottom[1], z_top[1]) - max(z_bottom[0], z_top[0]))
            if x_overlap > 0 and z_overlap > 0:
                y_intervals.append([j[2], j[3]])
        top_height = unfix_point[3] - unfix_point[2]
        y_intervals = sorted(y_intervals, key=lambda y_: y_[1])
        for j in range(len(y_intervals) - 1):
            if y_intervals[j + 1][0] - y_intervals[j][1] >= top_height:
                return y_intervals[j][1]
        return unfix_point[2]

    def addCorner(self):
        ''' Add container corner '''
        if self.corner != 0:
            corner_list = []
            for i in range(8):
                a = Item(
                    item_id='corner{}'.format(i),
                    item_name='corner',
                    typeof='cube',
                    WHD=(self.corner, self.corner, self.corner),
                    weight=0,
                    priority_level=0,
                    loadbear=0,
                    updown=True,
                    color='#000000')

                corner_list.append(a)
            return corner_list

    def putCorner(self, info, item):
        ''' Put corner in bin '''
        x = set2Decimal(self.width - self.corner)
        y = set2Decimal(self.height - self.corner)
        z = set2Decimal(self.depth - self.corner)
        pos = [
            [Decimal('0'), Decimal('0'), Decimal('0')],
            [Decimal('0'), Decimal('0'), z],
            [Decimal('0'), y, z],
            [Decimal('0'), y, Decimal('0')],
            [x, y, Decimal('0')],
            [x, Decimal('0'), Decimal('0')],
            [x, Decimal('0'), z],
            [x, y, z]
        ]
        item.position = pos[info]
        self.items.append(item)

        corner = [item.position[0], item.position[0] + self.corner,
                  item.position[1], item.position[1] + self.corner,
                  item.position[2], item.position[2] + self.corner]

        corner = np.array([corner], dtype=object)
        self.fit_items = np.append(self.fit_items, corner, axis=0)

    def clearBin(self):
        ''' Clear items in bin '''
        self.items = []
        self.fit_items = np.array([[Decimal('0'), self.width, Decimal('0'), self.height, Decimal('0'), Decimal('0')]], dtype=object)

class Packer:
    _default_packer = None

    def __init__(self, packer_id=None, packer_name=None):
        self.existing_items_ids = set()
        self.existing_bins_ids = set()
        self.existing_packers_ids = set()
        self.bins = []
        self.items = []
        self.unfit_items = []
        self.total_items = 0
        self.binding = []
        self.packer_id = self._generate_unique_id(packer_id)
        self.packer_name = packer_name if packer_name else packer_id
        if Packer._default_packer is None:
            Packer._default_packer = self
        if external_logger:
            external_logger.info(f'Added packer: {self.packer_id}')
    
    @staticmethod
    def get_default_packer():
        if Packer._default_packer is not None:
            return Packer._default_packer
        else:
            raise ValueError("No default packer available. Create an instance of Packer before creating Item or Bin.")

    def _generate_unique_id(self, base_id):
        ''' Generate a unique id if the base id already exists '''
        if base_id and base_id not in self.existing_packers_ids:
            self.existing_packers_ids.add(base_id)
            return base_id

        counter = 1
        new_id = f"{base_id}{counter}"
        while new_id in self.existing_packers_ids:
            counter += 1
            new_id = f"{base_id}{counter}"

        self.existing_packers_ids.add(new_id)
        if external_logger:
            external_logger.warning(f'ID conflict for packer {base_id}. Assigned new id: {new_id}')

        return new_id

    def addBin(self, bin):
        if external_logger:
            external_logger.info(f'Bin added: {bin.bin_id} to packer {self.packer_id}')
        self.bins.append(bin)

    def addItem(self, item):
        self.total_items = len(self.items) + 1
        if external_logger:
            external_logger.info(f'Item added: {item.item_id} to packer: {self.packer_id}')
        self.items.append(item)

    def pack2Bin(self, bin, item, fix_point, check_stable, support_surface_ratio):
        ''' Pack item into bin '''
        fitted = False
        bin.fix_point = fix_point
        bin.check_stable = check_stable
        bin.support_surface_ratio = Decimal(str(support_surface_ratio))
        if external_logger:
            external_logger.info(f"Attempting to pack item {item.item_id} into bin {bin.bin_id}")

        if item.assigned_bin and item.assigned_bin.bin_id != bin.bin_id:
            return False  # Skip packing if item is assigned to a different bin

        # First put item at (0, 0, 0), if corner exists, first add corner in box
        if bin.corner != 0 and not bin.items:
            corner_lst = bin.addCorner()
            for i in range(len(corner_lst)):
                bin.putCorner(i, corner_lst[i])

        elif not bin.items:
            response = bin.putItem(item, item.position)

            if not response:
                bin.unfitted_items.append(item)
                if external_logger:
                    external_logger.info(f'Item: {item.item_id} does not fit in bin: {bin.bin_id}')
                return False
            else:
                return True

        for axis in range(0, 3):
            items_in_bin = bin.items
            for ib in items_in_bin:
                pivot = [Decimal('0'), Decimal('0'), Decimal('0')]
                w, h, d = ib.getDimension()
                if axis == Axis.WIDTH:
                    pivot = [ib.position[0] + w, ib.position[1], ib.position[2]]
                elif axis == Axis.HEIGHT:
                    pivot = [ib.position[0], ib.position[1] + h, ib.position[2]]
                elif axis == Axis.DEPTH:
                    pivot = [ib.position[0], ib.position[1], ib.position[2] + d]

                if bin.putItem(item, pivot, axis):
                    fitted = True
                    break
            if fitted:
                break
        if not fitted:
            bin.unfitted_items.append(item)
            if external_logger:
                external_logger.info(f"Item {item.item_id} does not fit in bin {bin.bin_id}")
        return fitted

    def sortBinding(self):
        ''' Process binding groups according to the new specifications '''
        # Step 1: Merge groups with common items
        merged_bindings = self.mergeBindingGroups()

        # Step 2: For each merged group, check assigned bins and set minimum priority
        for group in merged_bindings:
            assigned_bins = set()
            priorities = []
            for item_id in group:
                item = next((i for i in self.items if i.item_id == item_id), None)
                if item:
                    if item.assigned_bin:
                        assigned_bins.add(item.assigned_bin)
                    priorities.append(item.priority_level)
                else:
                    if external_logger:
                        external_logger.warning(f"Item {item_id} specified in binding but not found in items.")
            # Check for conflicting assigned bins
            if len(assigned_bins) > 1:
                raise ValueError(f"Items in binding group {group} have conflicting assigned bins.")
            # Assign the bin to all items in the group if any
            assigned_bin = assigned_bins.pop() if assigned_bins else None
            for item_id in group:
                item = next((i for i in self.items if i.item_id == item_id), None)
                if item:
                    item.assigned_bin = assigned_bin
            # Set minimum priority to all items in the group
            min_priority = min(priorities) if priorities else None
            for item_id in group:
                item = next((i for i in self.items if i.item_id == item_id), None)
                if item and min_priority is not None:
                    item.priority_level = min_priority

        # Step 3: Reorder items so that binding groups are together
        bound_items = []
        unbound_items = self.items.copy()
        for group in merged_bindings:
            group_items = []
            for item_id in group:
                item = next((i for i in self.items if i.item_id == item_id), None)
                if item:
                    group_items.append(item)
                    if item in unbound_items:
                        unbound_items.remove(item)
            bound_items.append(group_items)

        # Flatten the list of bound items while maintaining groupings
        self.items = []
        for group_items in bound_items:
            self.items.extend(group_items)
        self.items.extend(unbound_items)

    def mergeBindingGroups(self):
        ''' Merge binding groups that have common items '''
        parent = dict()

        def find(item):
            while parent[item] != item:
                parent[item] = parent[parent[item]]  # Path compression
                item = parent[item]
            return item

        def union(item1, item2):
            root1 = find(item1)
            root2 = find(item2)
            if root1 != root2:
                parent[root2] = root1

        # Initialize parent pointers
        all_items_in_bindings = set()
        for group in self.binding:
            for item_id in group:
                parent[item_id] = item_id
                all_items_in_bindings.add(item_id)

        # Union items in the same group
        for group in self.binding:
            for i in range(len(group) - 1):
                union(group[i], group[i + 1])

        # Collect merged groups
        groups = dict()
        for item_id in all_items_in_bindings:
            root = find(item_id)
            if root in groups:
                groups[root].add(item_id)
            else:
                groups[root] = {item_id}

        merged_bindings = [list(group) for group in groups.values()]
        return merged_bindings

    def putOrder(self):
        ''' Arrange the order of items '''
        for i in self.bins:
            # Open top container
            if i.put_type == 2:
                i.items.sort(key=lambda item: item.position[0], reverse=False)
                i.items.sort(key=lambda item: item.position[1], reverse=False)
                i.items.sort(key=lambda item: item.position[2], reverse=False)
            # General container
            elif i.put_type == 1:
                i.items.sort(key=lambda item: item.position[1], reverse=False)
                i.items.sort(key=lambda item: item.position[2], reverse=False)
                i.items.sort(key=lambda item: item.position[0], reverse=False)
            else:
                pass
        return

    def gravityCenter(self, bin):
        '''Deviation Of Cargo gravity distribution'''
        w = bin.width
        h = bin.height

        # Define areas using decimal.Decimal
        half_w = w / 2
        half_h = h / 2

        areas = [
            {'x_range': (Decimal('0'), half_w), 'y_range': (Decimal('0'), half_h), 'weight': Decimal('0')},
            {'x_range': (half_w, w), 'y_range': (Decimal('0'), half_h), 'weight': Decimal('0')},
            {'x_range': (Decimal('0'), half_w), 'y_range': (half_h, h), 'weight': Decimal('0')},
            {'x_range': (half_w, w), 'y_range': (half_h, h), 'weight': Decimal('0')}
        ]

        for item in bin.items:
            x_start = item.position[0]
            y_start = item.position[1]
            dimension = item.getDimension()
            x_end = x_start + dimension[0]
            y_end = y_start + dimension[1]

            item_area = (x_end - x_start) * (y_end - y_start)
            item_weight = item.weight

            for area in areas:
                x_overlap = max(Decimal('0'), min(area['x_range'][1], x_end) - max(area['x_range'][0], x_start))
                y_overlap = max(Decimal('0'), min(area['y_range'][1], y_end) - max(area['y_range'][0], y_start))
                overlap_area = x_overlap * y_overlap

                if overlap_area > 0:
                    weight_contribution = (overlap_area / item_area) * item_weight
                    area['weight'] += weight_contribution

        total_weight = sum(area['weight'] for area in areas)
        if total_weight == 0:
            return [0, 0, 0, 0]  # No items in the bin

        result = [float((area['weight'] / total_weight) * 100) for area in areas]
        return result

    def pack(self, bigger_first=False, distribute_items=True, fix_point=True, check_stable=True, support_surface_ratio=0.75, binding=[], number_of_decimals=DEFAULT_NUMBER_OF_DECIMALS):
        '''Pack items into bins with binding considerations.'''
        # Set the number of decimals for measurements
        for bin in self.bins:
            bin.formatNumbers(number_of_decimals)

        for item in self.items:
            item.formatNumbers(number_of_decimals)

        # Add the binding attribute
        self.binding = binding

        # Process binding groups
        if binding != []:
            self.sortBinding()

        # Sort bins by volume
        self.bins.sort(key=lambda bin: bin.getVolume(), reverse=bigger_first)

        # Sort items by priority_level, loadbear, and volume
        self.items.sort(key=lambda item: (
            item.priority_level,  # Ascending priority_level
            -item.loadbear,  # Descending loadbear
            -item.getVolume() if bigger_first else item.getVolume()  # Volume
        ))

        # Prepare a set to track already packed items
        packed_items = set()
        unfit_binding_groups = []

        # Initialize the list of unfit items
        self.unfit_items = []

        # Create a dictionary of items for easy lookup
        items_dict = {item.item_id: item for item in self.items}

        # Process binding groups
        if self.binding != []:
            for group in self.binding:
                group_items = [items_dict[item_id] for item_id in group if item_id in items_dict]
                group_packed = False

                # Try to pack the group into each bin
                for bin in self.bins:
                    # Check if items have assigned bins and if they match the current bin
                    assigned_bins = set(item.assigned_bin.bin_id for item in group_items if item.assigned_bin)
                    if assigned_bins and bin.bin_id not in assigned_bins:
                        continue  # Skip bin if it doesn't match assigned bin

                    # Set the assigned bin for all items in the group
                    for item in group_items:
                        item.assigned_bin = bin

                    # Save the current state of the bin for rollback
                    bin_items_backup = bin.items.copy()
                    bin_fit_items_backup = bin.fit_items.copy()
                    bin_unfitted_items_backup = bin.unfitted_items.copy()

                    # Try to pack the group
                    group_fitted = True
                    for item in group_items:
                        if not self.pack2Bin(bin, item, fix_point, check_stable, support_surface_ratio):
                            group_fitted = False
                            break

                    if group_fitted:
                        packed_items.update(item.item_id for item in group_items)
                        group_packed = True
                        break  # Group packed successfully, move to next group
                    else:
                        # Restore bin state and try next bin
                        bin.items = bin_items_backup
                        bin.fit_items = bin_fit_items_backup
                        bin.unfitted_items = bin_unfitted_items_backup

                if not group_packed:
                    # Group couldn't be packed into any bin
                    unfit_binding_groups.extend(group_items)
                    if external_logger:
                        external_logger.info(f"Group {group} could not be packed into any bin")

        # After processing binding groups, pack unbound items
        for bin in self.bins:
            # Set bin properties
            bin.fix_point = fix_point
            bin.check_stable = check_stable
            bin.support_surface_ratio = Decimal(str(support_surface_ratio))

            # Get items not yet packed and not in unfit binding groups
            items_to_pack = [item for item in self.items if item.item_id not in packed_items and item not in unfit_binding_groups]

            # Sort remaining items
            items_to_pack.sort(key=lambda item: (
                item.priority_level,  # Ascending priority_level
                -item.loadbear,  # Descending loadbear
                -item.getVolume() if bigger_first else item.getVolume()  # Volume
            ))

            # Try to pack unbound items
            for item in items_to_pack:
                if item.assigned_bin and item.assigned_bin.bin_id != bin.bin_id:
                    if external_logger:
                        external_logger.info(f'Item {item.item_id} (assigned to bin {item.assigned_bin.bin_id}) does not match bin {bin.bin_id}')
                    continue  # Skip items assigned to another bin
                if self.pack2Bin(bin, item, fix_point, check_stable, support_surface_ratio):
                    packed_items.add(item.item_id)
                else:
                    bin.unfitted_items.append(item)
                    if external_logger:
                        external_logger.info(f"Item {item.item_id} does not fit in bin {bin.bin_id}")

            # Calculate the cargo gravity center
            bin.gravity = self.gravityCenter(bin)

        # Add unfit binding groups to unfit items
        self.unfit_items.extend(unfit_binding_groups)

        # Add any remaining unfit items
        remaining_unpacked_items = [item for item in self.items if item.item_id not in packed_items and item not in unfit_binding_groups]
        self.unfit_items.extend(remaining_unpacked_items)

        # Remove packed items from self.items if distribute_items is True
        if distribute_items:
            self.items = [item for item in self.items if item.item_id not in packed_items]

        # Arrange the order of items
        self.putOrder()

class Painter:

    def __init__(self, bin):
        self.items = bin.items
        self.width = float(bin.width)
        self.height = float(bin.height)
        self.depth = float(bin.depth)
        self.bin = bin

    def _plotCube(self, ax, x, y, z, dx, dy, dz, color='red', mode=2, linewidth=1, text="", fontsize=15, alpha=0.5):
        """Auxiliary function to plot a cube."""
        xx = [x, x, x + dx, x + dx, x]
        yy = [y, y + dy, y + dy, y, y]

        kwargs = {'alpha': 1, 'color': color, 'linewidth': linewidth}
        if mode == 1:
            ax.plot3D(xx, yy, [z] * 5, **kwargs)
            ax.plot3D(xx, yy, [z + dz] * 5, **kwargs)
            ax.plot3D([x, x], [y, y], [z, z + dz], **kwargs)
            ax.plot3D([x, x], [y + dy, y + dy], [z, z + dz], **kwargs)
            ax.plot3D([x + dx, x + dx], [y + dy, y + dy], [z, z + dz], **kwargs)
            ax.plot3D([x + dx, x + dx], [y, y], [z, z + dz], **kwargs)
        else:
            p = Rectangle((x, y), dx, dy, fc=color, ec='black', alpha=alpha)
            p2 = Rectangle((x, y), dx, dy, fc=color, ec='black', alpha=alpha)
            p3 = Rectangle((y, z), dy, dz, fc=color, ec='black', alpha=alpha)
            p4 = Rectangle((y, z), dy, dz, fc=color, ec='black', alpha=alpha)
            p5 = Rectangle((x, z), dx, dz, fc=color, ec='black', alpha=alpha)
            p6 = Rectangle((x, z), dx, dz, fc=color, ec='black', alpha=alpha)

            ax.add_patch(p)
            ax.add_patch(p2)
            ax.add_patch(p3)
            ax.add_patch(p4)
            ax.add_patch(p5)
            ax.add_patch(p6)

            if text != "":
                ax.text(
                    (x + dx / 2),
                    (y + dy / 2),
                    (z + dz / 2),
                    str(text),
                    color='black',
                    fontsize=fontsize,
                    ha='center',
                    va='center'
                )

            art3d.pathpatch_2d_to_3d(p, z=z, zdir="z")
            art3d.pathpatch_2d_to_3d(p2, z=z + dz, zdir="z")
            art3d.pathpatch_2d_to_3d(p3, z=x, zdir="x")
            art3d.pathpatch_2d_to_3d(p4, z=x + dx, zdir="x")
            art3d.pathpatch_2d_to_3d(p5, z=y, zdir="y")
            art3d.pathpatch_2d_to_3d(p6, z=y + dy, zdir="y")

    def _plotCylinder(self, ax, x, y, z, dx, dy, dz, color='red', mode=2, text="", fontsize=10, alpha=0.2):
        """Auxiliary function to plot a cylinder."""
        p = Circle((x + dx / 2, y + dy / 2), radius=dx / 2, color=color, alpha=0.5)
        p2 = Circle((x + dx / 2, y + dy / 2), radius=dx / 2, color=color, alpha=0.5)
        ax.add_patch(p)
        ax.add_patch(p2)
        art3d.pathpatch_2d_to_3d(p, z=z, zdir="z")
        art3d.pathpatch_2d_to_3d(p2, z=z + dz, zdir="z")

        center_z = np.linspace(0, dz, 10)
        theta = np.linspace(0, 2 * np.pi, 10)
        theta_grid, z_grid = np.meshgrid(theta, center_z)
        x_grid = dx / 2 * np.cos(theta_grid) + x + dx / 2
        y_grid = dy / 2 * np.sin(theta_grid) + y + dy / 2
        z_grid = z_grid + z
        ax.plot_surface(x_grid, y_grid, z_grid, shade=False, fc=color, alpha=alpha, color=color)

        if text != "":
            ax.text(
                (x + dx / 2),
                (y + dy / 2),
                (z + dz / 2),
                str(text),
                color='black',
                fontsize=fontsize,
                ha='center',
                va='center'
            )

    def plotBoxAndItems(self, title="", alpha=0.2, write_num=False, fontsize=10):
        """Plot the bin and the items it contains."""
        fig = plt.figure()
        axGlob = plt.axes(projection='3d')

        # plot bin wireframe
        self._plotCube(
            axGlob,
            0, 0, 0,
            float(self.width),
            float(self.height),
            float(self.depth),
            color='black',
            mode=1,
            linewidth=2,
            text=""
        )

        for item in self.items:
            x, y, z = item.position
            w, h, d = item.getDimension()
            color = item.color

            item_label = getattr(item, "item_id", getattr(item, "item_id", ""))
            text = item_label if write_num else ""

            if item.typeof == 'cube':
                self._plotCube(
                    axGlob,
                    float(x), float(y), float(z),
                    float(w), float(h), float(d),
                    color=color,
                    mode=2,
                    text=text,
                    fontsize=fontsize,
                    alpha=alpha
                )
            elif item.typeof == 'cylinder':
                self._plotCylinder(
                    axGlob,
                    float(x), float(y), float(z),
                    float(w), float(h), float(d),
                    color=color,
                    mode=2,
                    text=text,
                    fontsize=fontsize,
                    alpha=alpha
                )

        plot_title = title or getattr(self.bin, "bin_id", getattr(self.bin, "bin_id", "Packed Bin"))
        plt.title(plot_title)
        self.setAxesEqual(axGlob)
        return plt

    def setAxesEqual(self, ax):
        """Make axes of 3D plot have equal scale."""
        x_limits = ax.get_xlim3d()
        y_limits = ax.get_ylim3d()
        z_limits = ax.get_zlim3d()

        x_range = abs(x_limits[1] - x_limits[0])
        x_middle = np.mean(x_limits)
        y_range = abs(y_limits[1] - y_limits[0])
        y_middle = np.mean(y_limits)
        z_range = abs(z_limits[1] - z_limits[0])
        z_middle = np.mean(z_limits)

        plot_radius = 0.5 * max([x_range, y_range, z_range])

        ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
        ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
        ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])