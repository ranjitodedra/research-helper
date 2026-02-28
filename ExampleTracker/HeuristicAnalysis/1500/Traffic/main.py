import networkx as nx
import math
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
from typing import List, Dict, Tuple, Optional
import random
import time
import json
from pathlib import Path

class Vehicle:
    
    def __init__(self, vehicle_id: str, mass: float, speed: float, mass_factor: float, 
                 rolling_resistance: float, drag_coefficient: float, cross_sectional_area: float):
        self.vehicle_id = vehicle_id
        self.mass = mass
        self.speed = speed
        self.mass_factor = mass_factor
        self.rolling_resistance = rolling_resistance
        self.drag_coefficient = drag_coefficient
        self.cross_sectional_area = cross_sectional_area
        
    def get_vehicle_data(self):
        return {
            "mass": self.mass,
            "speed": self.speed,
            "mass_factor": self.mass_factor,
            "rolling_resistance": self.rolling_resistance,
            "drag_coefficient": self.drag_coefficient,
            "cross_sectional_area": self.cross_sectional_area
        }

class ModularBattery:
    
    def __init__(self, num_modules: int, module_capacity: float, initial_charges: List[float]):
        self.num_modules = num_modules
        self.module_capacity = module_capacity  # kWh per module
        self.total_capacity = num_modules * module_capacity  # Total battery capacity in kWh
        self.modules = []
        
        # Initialize modules with their charge levels
        for i, charge_percent in enumerate(initial_charges):
            charge_kwh = (charge_percent / 100.0) * module_capacity
            self.modules.append({
                'id': i + 1,
                'capacity': module_capacity,
                'current_charge': charge_kwh,
                'charge_percent': charge_percent,
                'depleted': charge_percent < 5.0
            })
    
    def get_total_charge_percent(self) -> float:
        total_charge = sum(module['current_charge'] for module in self.modules)
        return (total_charge / self.total_capacity) * 100.0
    
    def get_total_charge_kwh(self) -> float:
        return sum(module['current_charge'] for module in self.modules)
    
    def consume_energy(self, energy_kwh: float):
        remaining_energy = energy_kwh
        
        for module in self.modules:
            if remaining_energy <= 0:
                break
                
            if module['current_charge'] > 0:
                energy_from_module = min(remaining_energy, module['current_charge'])
                module['current_charge'] -= energy_from_module
                module['charge_percent'] = (module['current_charge'] / module['capacity']) * 100.0
                module['depleted'] = module['charge_percent'] < 5.0
                remaining_energy -= energy_from_module
    
    def get_depleted_modules(self) -> List[int]:
        return [module['id'] for module in self.modules if module['depleted']]
    
    def swap_modules(self, module_ids: List[int]):
        for module_id in module_ids:
            if 1 <= module_id <= self.num_modules:
                module = self.modules[module_id - 1]
                module['current_charge'] = module['capacity']
                module['charge_percent'] = 100.0
                module['depleted'] = False
    
    def get_module_status(self) -> Dict:
        return {
            f"M{module['id']}": f"{module['charge_percent']:.1f}%"
            for module in self.modules
        }

class EVRPBSS:
    
    def __init__(self, traci_bridge=None):
        self.graph = nx.Graph()
        self.vehicle = None
        self.battery = None
        self.customers = []
        self.bss_stations = []
        self.intersections = []
        self.depot = None
        self.base_speed = 0
        self.traffic_factors = {}
        self.debug_sumo = False  # Set to True for detailed SUMO debugging
        self.traci_bridge = traci_bridge  # SUMO TraCI bridge for real-time traffic
        self.vehicle_id = "delivery_vehicle_0"  # SUMO vehicle ID for visualization
        self.current_location = None
        self.total_load = 0
        self.package_weight = 5.0  # kg per package
        self.alpha = 0.1  # Speed reduction factor at full load
        self.battery_threshold = 20.0  # 20% threshold
        self.swap_margin = 0.05
        self.swap_time_per_module =2.0  # minutes per module
        
        # Journey tracking
        self.total_travel_time = 0.0
        self.total_energy_consumed = 0.0
        self.total_distance_covered = 0.0
        self.modules_swapped = 0
        self.served_customers = []
        self.path_taken = []
        self.soc_trail = []
        self.edge_energies = []
        
    def add_vehicle(self, vehicle: Vehicle):
        self.vehicle = vehicle
    
    def add_battery(self, battery: ModularBattery):
        self.battery = battery
    
    def add_node(self, node_id: str, node_type: str):
        self.graph.add_node(node_id, node_type=node_type)
        
        if node_type == 'depot':
            self.depot = node_id
        elif node_type == 'customer':
            self.customers.append(node_id)
        elif node_type == 'bss':
            self.bss_stations.append(node_id)
        elif node_type == 'intersection':
            self.intersections.append(node_id)
    
    def add_edge(self, from_node: str, to_node: str, distance: float, traffic_factor: float = 1.0):
        # Default edge data
        edge_data = {
            'angle': 0.86,  # Default slope angle
            'air_density': 1.205 # Default air density kg/m³
        }
        
        self.graph.add_edge(from_node, to_node, 
                           distance=distance, 
                           traffic_factor=traffic_factor,
                           edge_data=edge_data)
    
    def save_checkpoint(self, checkpoint_path: str) -> None:
        """Save current state to a checkpoint file."""
        checkpoint_data = {
            'current_location': self.current_location,
            'served_customers': self.served_customers,
            'total_load': self.total_load,
            'total_travel_time': self.total_travel_time,
            'total_energy_consumed': self.total_energy_consumed,
            'total_distance_covered': self.total_distance_covered,
            'modules_swapped': self.modules_swapped,
            'path_taken': self.path_taken,
            'soc_trail': self.soc_trail,
            'edge_energies': self.edge_energies,
            'battery_modules': [
                {
                    'id': module['id'],
                    'capacity': module['capacity'],
                    'current_charge': module['current_charge'],
                    'charge_percent': module['charge_percent'],
                    'depleted': module['depleted']
                }
                for module in self.battery.modules
            ]
        }
        
        checkpoint_file = Path(checkpoint_path)
        checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        print(f"Checkpoint saved to: {checkpoint_path}")
    
    def load_checkpoint(self, checkpoint_path: str) -> bool:
        """Load state from a checkpoint file."""
        checkpoint_file = Path(checkpoint_path)
        if not checkpoint_file.exists():
            print(f"Error: Checkpoint file not found: {checkpoint_path}")
            return False
        
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            self.current_location = checkpoint_data['current_location']
            self.served_customers = checkpoint_data['served_customers']
            self.total_load = checkpoint_data['total_load']
            self.total_travel_time = checkpoint_data['total_travel_time']
            self.total_energy_consumed = checkpoint_data['total_energy_consumed']
            self.total_distance_covered = checkpoint_data['total_distance_covered']
            self.modules_swapped = checkpoint_data['modules_swapped']
            self.path_taken = checkpoint_data['path_taken']
            self.soc_trail = checkpoint_data['soc_trail']
            self.edge_energies = checkpoint_data['edge_energies']
            
            # Restore battery state
            for module_data in checkpoint_data['battery_modules']:
                module = self.battery.modules[module_data['id'] - 1]
                module['current_charge'] = module_data['current_charge']
                module['charge_percent'] = module_data['charge_percent']
                module['depleted'] = module_data['depleted']
            
            print(f"Checkpoint loaded from: {checkpoint_path}")
            print(f"Resuming from: {self.current_location}")
            print(f"Served customers: {len(self.served_customers)}/{len(self.customers)}")
            return True
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
            return False
    
    def calculate_actual_speed(self, edge_data: Dict, current_load: float) -> float:
        traffic_factor = edge_data.get('traffic_factor', 1.0)
        return self.base_speed * traffic_factor
    
    def calculate_travel_time(self, distance: float, actual_speed: float) -> float:
        return (distance / actual_speed) * 60.0
    
    def calculate_energy_consumption(self, edge_data: Dict, distance: float, current_load: float) -> float:
        vehicle_data = self.vehicle.get_vehicle_data()
        M = vehicle_data['mass']
        v0 = self.calculate_actual_speed(edge_data, current_load)
        m = vehicle_data['mass_factor']
        f = vehicle_data['rolling_resistance']
        c = vehicle_data['drag_coefficient']
        A = vehicle_data['cross_sectional_area']
        g = 9.8

        meta = edge_data.get('edge_data', {})
        alpha_deg = meta.get('angle', 0.86)
        p = meta.get('air_density', 1.205)
        d = distance
        cos_alpha = math.cos(math.radians(alpha_deg))
        sin_alpha = math.sin(math.radians(alpha_deg))
        
        # Calculate dv_dt based on speed
        if 50 <= v0 <= 80:
            dv_dt = 0.3
        elif 81 <= v0 <= 120:
            dv_dt = 2
        else:
            dv_dt = 0
        
        # Total mass including load
        total_mass = M + current_load
        
        energy_consumption = (1 / 3600) * (total_mass * g * (f * cos_alpha + sin_alpha) + 
                                         0.0386 * (p * c * A * v0**2) + 
                                         (total_mass + m) * dv_dt) * d
        
        return energy_consumption
    
    def update_traffic_factors_from_sumo(self):
        """
        Update traffic factors for all edges from current SUMO simulation.
        
        Queries real-time edge speeds from SUMO TraCI and updates traffic_factor
        for all edges in the graph. Falls back to existing traffic_factor if
        TraCI is unavailable or edge not found.
        """
        # #region agent log
        import json
        from pathlib import Path
        log_path = Path(__file__).parent / ".cursor" / "debug.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"main.py:265","message":"update_traffic_factors_from_sumo entry","data":{"has_traci_bridge":self.traci_bridge is not None},"timestamp":int(__import__('time').time()*1000)}) + "\n")
        except Exception as e: print(f"[DEBUG LOG ERROR] {e}", file=sys.stderr)
        # #endregion
        if not self.traci_bridge or not self.traci_bridge.is_connected():
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"main.py:273","message":"update_traffic_factors_from_sumo early return","data":{"has_traci_bridge":self.traci_bridge is not None,"is_connected":self.traci_bridge.is_connected() if self.traci_bridge else False},"timestamp":int(__import__('time').time()*1000)}) + "\n")
            except Exception as e: print(f"[DEBUG LOG ERROR] {e}", file=sys.stderr)
            # #endregion
            return  # No TraCI bridge or not connected, use static factors
        
        updated_count = 0
        failed_count = 0
        edges_without_sumo_ids = 0
        total_edges = 0
        
        for u, v in self.graph.edges():
            total_edges += 1
            edge_data = self.graph[u][v]
            sumo_edge_ids = edge_data.get('sumo_edge_ids', [])
            
            if not sumo_edge_ids:
                edges_without_sumo_ids += 1
                continue  # No SUMO edge ID for this edge
            
            # Try each SUMO edge ID until we get a valid speed
            new_traffic_factor = None
            for sumo_edge_id in sumo_edge_ids:
                traffic_factor = self.traci_bridge.calculate_traffic_factor(
                    sumo_edge_id, self.base_speed
                )
                if traffic_factor is not None:
                    new_traffic_factor = traffic_factor
                    break
            
            if new_traffic_factor is not None:
                # Update traffic factor
                edge_data['traffic_factor'] = new_traffic_factor
                updated_count += 1
            else:
                # Keep existing traffic factor
                failed_count += 1
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"main.py:302","message":"update_traffic_factors_from_sumo exit","data":{"total_edges":total_edges,"updated_count":updated_count,"failed_count":failed_count,"edges_without_sumo_ids":edges_without_sumo_ids,"update_rate":updated_count/total_edges if total_edges > 0 else 0},"timestamp":int(__import__('time').time()*1000)}) + "\n")
        except Exception as e: print(f"[DEBUG LOG ERROR] {e}", file=sys.stderr)
        # #endregion
        
        # Only print if significant updates occurred (reduce verbosity)
        if updated_count > 0 and updated_count % 100 == 0:
            print(f"Updated traffic factors for {updated_count} edges from SUMO")
    
    def update_traffic_factor_for_edge(self, from_node: str, to_node: str) -> bool:
        """
        Update traffic factor for a single edge from SUMO.
        
        Args:
            from_node: Source node ID
            to_node: Target node ID
            
        Returns:
            True if updated, False otherwise
        """
        if not self.traci_bridge or not self.traci_bridge.is_connected():
            return False
        
        if not self.graph.has_edge(from_node, to_node):
            return False
        
        edge_data = self.graph[from_node][to_node]
        sumo_edge_ids = edge_data.get('sumo_edge_ids', [])
        
        if not sumo_edge_ids:
            return False
        
        # Try each SUMO edge ID
        for sumo_edge_id in sumo_edge_ids:
            traffic_factor = self.traci_bridge.calculate_traffic_factor(
                sumo_edge_id, self.base_speed
            )
            if traffic_factor is not None:
                edge_data['traffic_factor'] = traffic_factor
                return True
        
        return False
    
    def sync_sumo_simulation(self, travel_time_minutes: float):
        """
        Advance SUMO simulation by the travel time of vehicle movement.
        
        Args:
            travel_time_minutes: Travel time in minutes
        """
        if not self.traci_bridge or not self.traci_bridge.is_connected():
            return
        
        # Convert minutes to seconds
        travel_time_seconds = travel_time_minutes * 60.0
        
        # Advance SUMO simulation
        self.traci_bridge.advance_simulation(travel_time_seconds)
    
    def _update_sumo_vehicle_route(self, path: List[str]):
        """
        Update SUMO vehicle route based on NetworkX path using SUMO routing API.
        
        Args:
            path: List of node IDs representing the path
        """
        if not self.traci_bridge or not self.traci_bridge.is_connected():
            return
        
        if not self.traci_bridge.vehicle_id:
            return
        
        if len(path) < 2:
            return
        
        try:
            # Use SUMO routing API instead of pre-mapped edge IDs
            success = self.traci_bridge.update_vehicle_route(
                self.traci_bridge.vehicle_id,
                nx_path=path,
                graph=self.graph
            )
            
            if success:
                if hasattr(self, 'debug_sumo') and self.debug_sumo:
                    print(f"[SUMO DEBUG] Route updated successfully: {len(path)} nodes")
            else:
                # Only log route update failures at debug level to reduce verbosity
                if hasattr(self, 'debug_sumo') and self.debug_sumo:
                    print(f"[SUMO DEBUG] Route update failed for path: {path[:3]}... (length: {len(path)})")
                    try:
                        status = self.traci_bridge.get_vehicle_status(self.traci_bridge.vehicle_id)
                        if status:
                            print(f"[SUMO DEBUG] Vehicle still exists: edge={status['edge_id']}, speed={status['speed']:.2f} m/s")
                        else:
                            print(f"[SUMO DEBUG] Vehicle status unavailable")
                    except:
                        pass
                    
        except Exception as e:
            # Log error but don't crash heuristic
            print(f"[SUMO ERROR] Route update exception: {e}")
            import traceback
            if hasattr(self, 'debug_sumo') and self.debug_sumo:
                traceback.print_exc()
    
    def _readd_vehicle_at_current_location(self, next_target: Optional[str] = None):
        """
        Attempt to re-add the SUMO vehicle at the current NetworkX node using routing API.
        """
        if not self.traci_bridge or not self.traci_bridge.is_connected():
            return False
        
        try:
            success = self.traci_bridge.add_vehicle_at_network_node(
                self.vehicle_id,
                self.current_location,
                self.graph,
                next_node_id=next_target
            )
            if success:
                if hasattr(self, 'debug_sumo') and self.debug_sumo:
                    print(f"[SUMO DEBUG] Vehicle re-added at node {self.current_location}")
            else:
                if hasattr(self, 'debug_sumo') and self.debug_sumo:
                    print(f"[SUMO DEBUG] Failed to re-add vehicle at node {self.current_location}")
            return success
        except Exception as e:
            print(f"[SUMO] Error re-adding vehicle at current node: {e}")
            return False
    
    def initialize_sumo_vehicle(self):
        """
        Initialize delivery vehicle in SUMO simulation for visualization.
        """
        if not self.traci_bridge:
            print("[SUMO] No TraCI bridge available")
            return False
        
        if not self.traci_bridge.is_connected():
            print("[SUMO] TraCI bridge not connected")
            return False
        
        if not self.traci_bridge.gui:
            print("[SUMO] GUI mode not enabled")
            return False
        
        if not self.depot:
            print("[SUMO] No depot defined")
            return False
        
        try:
            print(f"[SUMO] Initializing vehicle at depot: {self.depot}")
            
            # Map depot node to SUMO junction
            from sumo_converter import map_nx_node_to_sumo_junction
            depot_junction = map_nx_node_to_sumo_junction(self.depot, self.graph, self.traci_bridge)
            
            if not depot_junction:
                print("[SUMO] WARNING: Could not map depot to SUMO junction, trying fallback...")
                # Fallback: try to find any valid edge
                try:
                    import traci
                    all_edges = traci.edge.getIDList()
                    if all_edges:
                        route_edges = [all_edges[0]]
                        print(f"[SUMO] Using fallback edge: {route_edges[0]}")
                    else:
                        print("[SUMO] ERROR: No edges available in SUMO network")
                        return False
                except:
                    print("[SUMO] ERROR: Could not access SUMO edges")
                    return False
            else:
                print(f"[SUMO] Mapped depot to SUMO junction: {depot_junction}")
                
                # Get initial route: if customers exist, route to first customer; otherwise find nearby edge
                if self.customers:
                    # Map first customer to SUMO junction
                    customer_junction = map_nx_node_to_sumo_junction(self.customers[0], self.graph, self.traci_bridge)
                    if customer_junction:
                        print(f"[SUMO] Mapped first customer to SUMO junction: {customer_junction}")
                        if customer_junction == depot_junction:
                            print("[SUMO] WARNING: Depot and first customer map to same junction, using nearby edge instead")
                            route_edges = None
                        else:
                            # Find route between junctions
                            route_edges = self.traci_bridge.find_route_between_junctions(
                                depot_junction, customer_junction, vclass="delivery"
                            )
                            if route_edges:
                                print(f"[SUMO] Found route from depot to customer: {len(route_edges)} edges")
                            else:
                                print("[SUMO] WARNING: Could not find route between junctions, using nearby edge")
                                route_edges = None
                    else:
                        print("[SUMO] WARNING: Could not map customer to SUMO junction")
                        route_edges = None
                else:
                    route_edges = None
                
                # If no route found, find any edge near depot junction
                if not route_edges:
                    connected_edges = self.traci_bridge._get_edges_connected_to_junction(depot_junction)
                    if connected_edges:
                        route_edges = [connected_edges[0]]
                        print(f"[SUMO] Using nearby edge from depot junction: {route_edges[0]}")
                    else:
                        try:
                            import traci
                            all_edges = traci.edge.getIDList()
                            if all_edges:
                                route_edges = [all_edges[0]]
                                print(f"[SUMO] Using first available SUMO edge: {route_edges[0]}")
                            else:
                                print("[SUMO] ERROR: No edges available in SUMO network")
                                return False
                        except Exception as e:
                            print(f"[SUMO] ERROR: Could not find edge near depot junction: {e}")
                            return False
            
            # Add vehicle to SUMO (bright magenta for maximum visibility)
            if route_edges:
                print(f"[SUMO] Adding vehicle with {len(route_edges)} route edges...")
                print(f"[SUMO] Route edges: {route_edges[:5]}...")  # Show first 5 edges
                success = self.traci_bridge.add_vehicle(
                    self.vehicle_id,
                    route_edges,
                    color=(255, 0, 255),  # Bright Magenta - very distinctive!
                    vehicle_type="delivery_vehicle"
                )
                if success:
                    # Verify vehicle appears in SUMO
                    exists, status_msg = self.traci_bridge.verify_vehicle_exists(self.vehicle_id)
                    if exists:
                        vehicle_status = self.traci_bridge.get_vehicle_status(self.vehicle_id)
                        print(f"[SUMO] Delivery vehicle added to SUMO GUI: {self.vehicle_id}")
                        if vehicle_status:
                            print(f"[SUMO] Vehicle details:")
                            print(f"[SUMO]   - Edge: {vehicle_status['edge_id']}")
                            print(f"[SUMO]   - Position: {vehicle_status['position']}")
                            print(f"[SUMO]   - Speed: {vehicle_status['speed']:.2f} m/s")
                            print(f"[SUMO]   - Color: {vehicle_status['color']}")
                        return True
                    else:
                        print(f"[SUMO] WARNING: Vehicle added but verification failed: {status_msg}")
                        return False
                else:
                    print(f"[SUMO] Failed to add vehicle to SUMO")
                    print(f"[SUMO] This might be due to:")
                    print(f"[SUMO]   1. Edge mapping issues between NetworkX and SUMO")
                    print(f"[SUMO]   2. SUMO network not matching the converted network")
                    print(f"[SUMO]   3. Vehicle type creation failure")
                    return False
            else:
                print("[SUMO] ERROR: Could not find any valid SUMO edges for vehicle initialization")
                return False
        
        except Exception as e:
            print(f"[SUMO] Error: Could not initialize SUMO vehicle: {e}")
            import traceback
            traceback.print_exc()
        
        return False
    
    def bfs_find_reachable_nodes(self, start_node: str, max_energy: float) -> List[str]:
        visited = set()
        queue = deque([(start_node, 0.0)])  # (node, energy_used)
        reachable = []
        
        while queue:
            current_node, energy_used = queue.popleft()
            
            if current_node in visited:
                continue
            visited.add(current_node)
            
            if energy_used <= max_energy:
                reachable.append(current_node)
                # graph.neighbors(node) -> returns an iterator over all nodes adjacent (directly connected) to node.
                for neighbor in self.graph.neighbors(current_node):
                    if neighbor not in visited:
                        edge_data = self.graph[current_node][neighbor]
                        distance = edge_data['distance']
                        energy_needed = self.calculate_energy_consumption(
                            edge_data, distance, self.total_load
                        )
                        
                        if energy_used + energy_needed <= max_energy:
                            queue.append((neighbor, energy_used + energy_needed))
        
        return reachable
    
    def find_shortest_path(self, start: str, end: str) -> List[str]:
        try:
            # Use single shortest path (much faster than finding all paths and sorting)
            path = nx.shortest_path(self.graph, start, end)
            return path if path else []
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
    
    def calculate_path_distance(self, start: str, end: str) -> float:
        path = self.find_shortest_path(start, end)
        if not path:
            return float('inf')
        
        total_distance = 0.0
        for i in range(len(path) - 1):
            from_node = path[i]
            to_node = path[i + 1]
            if self.graph.has_edge(from_node, to_node):
                total_distance += self.graph[from_node][to_node]['distance']
        
        return total_distance
    
    def calculate_path_cost(self, path: List[str]) -> Tuple[float, float, float]:
        if len(path) < 2:
            return 0.0, 0.0, 0.0
        
        total_time = 0.0
        total_energy = 0.0
        total_distance = 0.0
        current_load = self.total_load
        
        for i in range(len(path) - 1):
            from_node = path[i]
            to_node = path[i + 1]
            
            edge_data = self.graph[from_node][to_node]
            distance = edge_data['distance']
            actual_speed = self.calculate_actual_speed(edge_data, current_load)
            
            travel_time = self.calculate_travel_time(distance, actual_speed)
            energy = self.calculate_energy_consumption(edge_data, distance, current_load)
            
            total_time += travel_time
            total_energy += energy
            total_distance += distance
            
            # Reduce load if delivering to customer
            if to_node in self.customers and to_node not in self.served_customers:
                current_load -= self.package_weight
        
        return total_time, total_energy, total_distance
    
    def find_bss_within_range(self, max_distance: float) -> List[str]:
        nearby_bss = []
        
        for bss in self.bss_stations:
            distance = self.calculate_path_distance(self.current_location, bss)
            if distance <= max_distance:
                nearby_bss.append(bss)
        
        return nearby_bss
    
    def select_best_opportunity_bss(self, nearby_bss: List[str], destination: str) -> Optional[str]:
        if not nearby_bss:
            return None
        
        # Calculate cost for each BSS: Cost_current_to_bss + Cost_bss_to_destination
        bss_costs = []
        for bss in nearby_bss:
            path_to_bss = self.find_shortest_path(self.current_location, bss)
            path_from_bss = self.find_shortest_path(bss, destination)
            
            if path_to_bss and path_from_bss:
                time_to_bss, energy_to_bss, _ = self.calculate_path_cost(path_to_bss)
                time_from_bss, energy_from_bss, _ = self.calculate_path_cost(path_from_bss)
                
                total_time = time_to_bss + time_from_bss
                total_energy = energy_to_bss + energy_from_bss
                
                bss_costs.append((bss, total_time, total_energy))
        
        if not bss_costs:
            return None
        
        # Find minimum cost without sorting (much faster)
        best_bss = min(bss_costs, key=lambda x: 0.5 * x[1] + 0.5 * x[2])
        return best_bss[0]
    
    def select_best_customer(self) -> Optional[str]:
        available_energy = self.battery.get_total_charge_kwh()
        reachable_customers = []
        
        # for customer in self.customers:
        #     if customer not in self.served_customers:
        #         reachable = self.bfs_find_reachable_nodes(customer, available_energy)
        #         if customer in reachable:
        #             reachable_customers.append(customer)

        reachable = self.bfs_find_reachable_nodes(self.current_location, available_energy)
        reachable_customers = [c for c in self.customers if c not in self.served_customers and c in reachable]
        
        if not reachable_customers:
            return None
        
        # Calculate costs for all reachable customers
        customer_costs = []
        for customer in reachable_customers:
            path = self.find_shortest_path(self.current_location, customer)
            if path:
                time, energy, distance = self.calculate_path_cost(path)
                customer_costs.append((customer, time, energy, distance))
        
        if not customer_costs:
            return None
        
        # Normalize costs
        max_time = max(cost[1] for cost in customer_costs)
        max_energy = max(cost[2] for cost in customer_costs)
        
        best_customer = None
        min_cost = float('inf')
        
        for customer, time, energy, distance in customer_costs:
            normalized_time = time / max_time if max_time > 0 else 0
            normalized_energy = energy / max_energy if max_energy > 0 else 0
            cost = 0.5 * normalized_time + 0.5 * normalized_energy
            
            if cost < min_cost:
                min_cost = cost
                best_customer = customer
        
        return best_customer
    
    def select_best_bss(self, from_node: str) -> Optional[str]:
        available_energy = self.battery.get_total_charge_kwh()
        reachable_bss = []
        
        # for bss in self.bss_stations:
        #     reachable = self.bfs_find_reachable_nodes(bss, available_energy)
        #     if bss in reachable:
        #         reachable_bss.append(bss)

        reachable = self.bfs_find_reachable_nodes(from_node, available_energy)
        reachable_bss = [bss for bss in self.bss_stations if bss in reachable]
        
        if not reachable_bss:
            return None
        
        # Calculate costs for all reachable BSS
        bss_costs = []
        for bss in reachable_bss:
            path = self.find_shortest_path(from_node, bss)
            if path:
                time, energy, distance = self.calculate_path_cost(path)
                bss_costs.append((bss, time, energy, distance))
        
        if not bss_costs:
            return None
        
        # Normalize costs
        max_time = max(cost[1] for cost in bss_costs)
        max_energy = max(cost[2] for cost in bss_costs)
        
        best_bss = None
        min_cost = float('inf')
        
        for bss, time, energy, distance in bss_costs:
            normalized_time = time / max_time if max_time > 0 else 0
            normalized_energy = energy / max_energy if max_energy > 0 else 0
            cost = 0.5 * normalized_time + 0.5 * normalized_energy
            
            if cost < min_cost:
                min_cost = cost
                best_bss = bss
        
        return best_bss
    
    def estimate_energy_for_journey(self, destination: str, via_bss: bool = False) -> float:
        threshold = (self.battery_threshold / 100.0) * self.battery.total_capacity

        if via_bss:
            # Opportunity: Current -> BSS -> Customer
            bss = self.select_best_bss(self.current_location)
            if not bss:
                return float('inf')
            p1 = self.find_shortest_path(self.current_location, bss)
            p2 = self.find_shortest_path(bss, destination)
            if p1 and p2:
                _, e1, _ = self.calculate_path_cost(p1)
                _, e2, _ = self.calculate_path_cost(p2)
                return e1 + e2 + threshold
            return float('inf')

        # Normal journeys
        if destination in self.customers:
            # Current -> Customer -> Nearest BSS
            p1 = self.find_shortest_path(self.current_location, destination)
            if not p1:
                return float('inf')
            bss = self.select_best_bss(destination)
            if not bss:
                return float('inf')
            p2 = self.find_shortest_path(destination, bss)
            if p2:
                _, e1, _ = self.calculate_path_cost(p1)
                _, e2, _ = self.calculate_path_cost(p2)
                return e1 + e2 + threshold
            return float('inf')
        else:
            # Depot: Current -> Depot
            p = self.find_shortest_path(self.current_location, destination)
            if p:
                _, e, _ = self.calculate_path_cost(p)
                return e + threshold
            return float('inf')
    
    def is_bss_worth_visiting(self, bss: str, destination: str) -> bool:
        # Direct path
        direct_path = self.find_shortest_path(self.current_location, destination)
        if not direct_path:
            return False
        direct_time, direct_energy, _ = self.calculate_path_cost(direct_path)

        # Via BSS
        path_to_bss = self.find_shortest_path(self.current_location, bss)
        path_from_bss = self.find_shortest_path(bss, destination)
        if not path_to_bss or not path_from_bss:
            return False

        time_to_bss, energy_to_bss, _ = self.calculate_path_cost(path_to_bss)
        time_from_bss, energy_from_bss, _ = self.calculate_path_cost(path_from_bss)

        swap_time = len(self.battery.get_depleted_modules()) * self.swap_time_per_module

        via_time = time_to_bss + swap_time + time_from_bss
        via_energy = energy_to_bss + energy_from_bss

        # Normalize across the two alternatives
        max_time = max(direct_time, via_time, 1e-9)
        max_energy = max(direct_energy, via_energy, 1e-9)

        direct_cost = 0.5 * (direct_time / max_time) + 0.5 * (direct_energy / max_energy)
        via_cost    = 0.5 * (via_time   / max_time) + 0.5 * (via_energy   / max_energy)

        # Accept via BSS if it's within tolerance of direct
        return (via_cost - direct_cost) < self.swap_margin  # e.g., self.swap_margin = 0.05
    
    def move_to_node(self, target_node: str):
        """Move one step closer to target_node, then return to main loop"""
        if target_node == self.current_location:
            print(f"Already at {target_node}")
            return True
        
        path = self.find_shortest_path(self.current_location, target_node)
        if not path or len(path) < 2:
            print(f"Error: No path found to {target_node}")
            return False

        # CHANGE: Move only to the NEXT node in the path (not the entire path)
        from_node = path[0]  # Current location
        to_node = path[1]    # Next step only
        
        edge_data = self.graph[from_node][to_node]
        distance = edge_data['distance']
        actual_speed = self.calculate_actual_speed(edge_data, self.total_load)
        
        travel_time = self.calculate_travel_time(distance, actual_speed)
        energy = self.calculate_energy_consumption(edge_data, distance, self.total_load)
        
        # Update statistics
        self.total_travel_time += travel_time
        self.total_energy_consumed += energy
        self.total_distance_covered += distance
        self.edge_energies.append(energy)
        
        # Consume battery energy
        self.battery.consume_energy(energy)
        
        # Advance SUMO simulation to match vehicle movement
        self.sync_sumo_simulation(travel_time)
        
        # Update vehicle route in SUMO if visualization is enabled
        if self.traci_bridge and self.traci_bridge.gui:
            self._update_sumo_vehicle_route(path)
            # Ensure color stays bright magenta
            try:
                if self.traci_bridge.vehicle_id:
                    self.traci_bridge.highlight_vehicle(self.traci_bridge.vehicle_id, (255, 0, 255))
                    
                    # Verify vehicle exists and get status
                    exists, status_msg = self.traci_bridge.verify_vehicle_exists(self.traci_bridge.vehicle_id)
                    if exists:
                        if hasattr(self, 'debug_sumo') and self.debug_sumo:
                            vehicle_status = self.traci_bridge.get_vehicle_status(self.traci_bridge.vehicle_id)
                            if vehicle_status:
                                print(f"[SUMO DEBUG] Vehicle status: edge={vehicle_status['edge_id']}, "
                                      f"speed={vehicle_status['speed']:.2f} m/s, "
                                      f"position={vehicle_status['position']}")
                    else:
                        # Only log vehicle not found at debug level to reduce verbosity
                        if hasattr(self, 'debug_sumo') and self.debug_sumo:
                            print(f"[SUMO DEBUG] {status_msg}")
            except Exception as e:
                if hasattr(self, 'debug_sumo') and self.debug_sumo:
                    print(f"[SUMO DEBUG] Error verifying vehicle: {e}")
        
        # Update current location
        self.current_location = to_node
        if not self.path_taken or self.path_taken[-1] != to_node:
            self.path_taken.append(to_node)
        
        # Record SoC at this node for final summary
        self.soc_trail.append((to_node, self.battery.get_total_charge_percent()))
        
        print(f"Step: {from_node} -> {to_node}: "
              f"Distance={distance:.2f}km, Time={travel_time:.2f}min, "
              f"Energy={energy:.3f}kWh, SoC={self.battery.get_total_charge_percent():.1f}%")
        
        # Handle node-specific actions
        if to_node in self.customers and to_node not in self.served_customers:
            self.serve_customer(to_node)
        elif to_node in self.bss_stations:
            if self.handle_bss_visit(to_node):
                return True
            return False
        
        # Return True if we've reached the target, False if we need more steps
        return to_node == target_node
    
    def serve_customer(self, customer: str):
        print(f"Serving customer {customer}")
        self.served_customers.append(customer)
        self.total_load -= self.package_weight
        print(f"Load reduced to {self.total_load}kg")
    
    def handle_bss_visit(self, bss: str):
        print(f"\n=== HANDLING BSS VISIT AT {bss} ===")
        
        # Step 1: Re-evaluate from current BSS location
        print("Re-evaluating customer and BSS selection from current BSS location...")
        
        # Check if there are any customers left to serve
        if len(self.served_customers) >= len(self.customers):
            # All customers served - destination is depot
            destination = self.depot
            is_depot = True
            print(f"All customers served - destination is depot: {destination}")
        else:
            # Still have customers to serve
            # Update traffic factors before selecting customer
            if self.traci_bridge:
                self.update_traffic_factors_from_sumo()
            
            destination = self.select_best_customer()
            is_depot = False
            if not destination:
                print("No reachable customers found from BSS")
                return False
            print(f"New selected customer from BSS: {destination}")
            
            # Update traffic factors before selecting BSS
            if self.traci_bridge:
                self.update_traffic_factors_from_sumo()
            
            # Select new BSS from customer location (only for customer destinations)
            nearest_bss_from_customer = self.select_best_bss(destination)
            if not nearest_bss_from_customer:
                print("No reachable BSS found from customer")
                return False
            print(f"New nearest BSS from customer: {nearest_bss_from_customer}")
        
        # Step 2: Calculate selected journey energy requirements
        if is_depot:
            # For depot: only need energy from BSS to depot + threshold
            selected_journey_energy = self.estimate_energy_for_journey(destination, via_bss=False)
        else:
            # For customer: need energy from BSS to customer + nearest BSS after that
            selected_journey_energy = self.estimate_energy_for_journey(destination, via_bss=False) # E1 + E2 + battery_threshold
        
        current_energy = self.battery.get_total_charge_kwh()
        
        print(f"Selected journey energy: {selected_journey_energy:.3f} kWh")
        print(f"Current energy: {current_energy:.3f} kWh")
        
        # Step 3: Check if current SoC allows completing selected journey
        if current_energy >= selected_journey_energy:
            print("Current SoC sufficient for selected journey")
            
            if is_depot:
                if self.current_location == self.depot:
                    print("Already at depot")
                    return True
                print("Moving directly to depot...")
                return self.move_to_node(destination)
            else:
                # For customer: check for depleted modules
                depleted_modules = self.battery.get_depleted_modules()
                if depleted_modules:
                    print(f"Swapping {len(depleted_modules)} depleted modules: {depleted_modules}")
                    self.battery.swap_modules(depleted_modules)
                    self.modules_swapped += len(depleted_modules)
                    
                    # Add swapping time
                    swap_time = len(depleted_modules) * self.swap_time_per_module
                    self.total_travel_time += swap_time
                    print(f"Swapping time: {swap_time} minutes")
                
                print("Moving to selected customer...")
                return self.move_to_node(destination)
        
        else:
            print("Current SoC insufficient for selected journey")
            
            if is_depot:
                # Skip depleted module check, go directly to swapping enough/all modules
                print("For depot: skipping depleted module check, checking if swapping enough modules helps...")
                
                # Check if swapping enough modules helps 
                energy_deficit = selected_journey_energy - current_energy
                
                if energy_deficit > 0:
                    # Find minimum modules to swap to meet energy requirement
                    modules_to_swap = self.find_minimum_modules_to_swap(energy_deficit)
                    
                    if modules_to_swap:
                        print(f"Swapping {len(modules_to_swap)} modules to meet energy requirement for depot: {modules_to_swap}")
                        self.battery.swap_modules(modules_to_swap)
                        self.modules_swapped += len(modules_to_swap)
                        
                        swap_time = len(modules_to_swap) * self.swap_time_per_module
                        self.total_travel_time += swap_time
                        print(f"Swapping time: {swap_time} minutes")
                        
                        print("Moving to depot...")
                        if self.current_location == self.depot:
                            print("Already at depot")
                            return True
                        return self.move_to_node(destination)
                
                # If swapping enough modules doesn't help, swap all modules
                print("Swapping all modules for depot return...")
                all_modules = list(range(1, self.battery.num_modules + 1))
                self.battery.swap_modules(all_modules)
                self.modules_swapped += len(all_modules)
                
                swap_time = len(all_modules) * self.swap_time_per_module
                self.total_travel_time += swap_time
                print(f"Swapping all modules time: {swap_time} minutes")
                
                # Check if we can reach depot after swapping all modules
                new_energy = self.battery.total_capacity  # Full capacity after swapping all
                if new_energy >= selected_journey_energy:
                    print("After swapping all modules, sufficient energy to reach depot")
                    if self.current_location == self.depot:
                        print("Already at depot")
                        return True
                    return self.move_to_node(destination)
                else:
                    print("Even after swapping all modules, insufficient energy - implementing Step 11...")
                    alternative_bss = self.find_bss_for_insufficient_energy(destination)
                    if alternative_bss:
                        return self.move_to_node(alternative_bss)
                    else:
                        return False
            
            else:
                # For customer
                # Step 4: Check if swapping only depleted modules helps
                depleted_modules = self.battery.get_depleted_modules()
                if depleted_modules:
                    # Calculate new SoC after swapping only depleted modules
                    new_energy = current_energy
                    for module_id in depleted_modules:
                        module = self.battery.modules[module_id - 1]
                        energy_to_add = module['capacity'] - module['current_charge']
                        new_energy += energy_to_add
                    
                    print(f"New SoC after swapping depleted modules: {new_energy:.3f} kWh")
                    
                    if new_energy >= selected_journey_energy:
                        print("Swapping only depleted modules sufficient")
                        self.battery.swap_modules(depleted_modules)
                        self.modules_swapped += len(depleted_modules)
                        
                        swap_time = len(depleted_modules) * self.swap_time_per_module
                        self.total_travel_time += swap_time
                        print(f"Swapping time: {swap_time} minutes")
                        
                        print("Moving to selected customer...")
                        return self.move_to_node(destination)
                
                # Step 5: Check if swapping enough modules helps
                energy_deficit = selected_journey_energy - current_energy
                
                if energy_deficit > 0:
                    # Find minimum modules to swap to meet energy requirement
                    modules_to_swap = self.find_minimum_modules_to_swap(energy_deficit)
                    
                    if modules_to_swap:
                        print(f"Swapping {len(modules_to_swap)} modules to meet energy requirement: {modules_to_swap}")
                        self.battery.swap_modules(modules_to_swap)
                        self.modules_swapped += len(modules_to_swap)
                        
                        swap_time = len(modules_to_swap) * self.swap_time_per_module
                        self.total_travel_time += swap_time
                        print(f"Swapping time: {swap_time} minutes")
                        
                        print("Moving to selected customer...")
                        return self.move_to_node(destination)
                
                # Step 6: Swap all modules and find alternative BSS
                print("Swapping all modules and finding alternative BSS...")
                all_modules = list(range(1, self.battery.num_modules + 1))
                self.battery.swap_modules(all_modules)
                self.modules_swapped += len(all_modules)
                
                swap_time = len(all_modules) * self.swap_time_per_module
                self.total_travel_time += swap_time
                print(f"Swapping all modules time: {swap_time} minutes")
                
                # Step 7: Find alternative BSS (Step 11 from Rules.md)
                alternative_bss = self.find_bss_for_insufficient_energy(destination)
                if alternative_bss:
                    return self.move_to_node(alternative_bss)
                else:
                    return False
    
    def find_minimum_modules_to_swap(self, energy_deficit: float) -> List[int]:
        modules_to_swap = []
        remaining_deficit = energy_deficit
        
        # Sort modules by current charge (ascending) to prioritize low-charge modules
        sorted_modules = sorted(self.battery.modules, key=lambda x: x['current_charge'])
        
        for module in sorted_modules:
            if remaining_deficit <= 0:
                break
            
            energy_available = module['capacity'] - module['current_charge']
            if energy_available > 0:
                modules_to_swap.append(module['id'])
                remaining_deficit -= energy_available
        
        return modules_to_swap if remaining_deficit <= 0 else []
    
    def find_bss_for_insufficient_energy(self, destination: str) -> Optional[str]:
        print("Insufficient energy - implementing Step 4.4 logic...")
        
        # Check if destination is depot
        is_depot = destination == self.depot
        
        available_energy = self.battery.get_total_charge_kwh()
        
        # Find all reachable BSS from current location
        reachable = self.bfs_find_reachable_nodes(self.current_location, available_energy)
        reachable_bss = [bss for bss in self.bss_stations if bss in reachable]
        
        if not reachable_bss:
            print("No reachable BSS found from current location - ERROR!")
            return None
        
        # For each reachable BSS, compute total time and energy for the insufficient-energy plan
        # Segments:
        #   current -> BSS
        #   BSS -> destination
        #   (if destination is customer) destination -> nearest BSS (post-service safety)
        candidates: List[Tuple[str, float, float]] = []  # (bss, total_time, total_energy)
        
        for bss in reachable_bss:
            path_to_bss = self.find_shortest_path(self.current_location, bss)
            if not path_to_bss:
                continue
            t1, e1, _ = self.calculate_path_cost(path_to_bss)
            
            path_bss_to_dest = self.find_shortest_path(bss, destination)
            if not path_bss_to_dest:
                continue
            t2, e2, _ = self.calculate_path_cost(path_bss_to_dest)
            
            t3 = 0.0
            e3 = 0.0
            if not is_depot:
                # After reaching customer, ensure we can reach nearest BSS
                nearest_bss_from_customer = self.select_best_bss(destination)
                if not nearest_bss_from_customer:
                    continue
                path_dest_to_bss = self.find_shortest_path(destination, nearest_bss_from_customer)
                if not path_dest_to_bss:
                    continue
                t3, e3, _ = self.calculate_path_cost(path_dest_to_bss)
            
            # After swap at BSS, pack is full; check feasibility for energy reserves using the earlier logic
            threshold_kwh = (self.battery_threshold / 100.0) * self.battery.total_capacity
            required_after_swap = e2 + (e3 if not is_depot else 0.0) + threshold_kwh
            if self.battery.total_capacity < required_after_swap:
                continue
            print(required_after_swap)
            total_time = t1 + t2 + t3
            total_energy = e1 + e2 + e3
            candidates.append((bss, total_time, total_energy))
        
        if not candidates:
            if is_depot:
                print("No BSS allows reaching depot - ERROR!")
            else:
                print("No BSS allows reaching customer and subsequent BSS - ERROR!")
            return None
        
        # Normalize and compute cost = 0.5 * norm_time + 0.5 * norm_energy
        max_time = max(t for _, t, _ in candidates) or 1e-9
        max_energy = max(e for _, _, e in candidates) or 1e-9
        best_bss = None
        best_cost = float('inf')
        for bss, t, e in candidates:
            norm_t = t / max_time
            norm_e = e / max_energy
            cost = 0.5 * norm_t + 0.5 * norm_e
            if cost < best_cost:
                best_cost = cost
                best_bss = bss
        
        print(f"Selected BSS for insufficient energy scenario: {best_bss} (cost={best_cost:.3f})")
        return best_bss
    
    def run_routing_algorithm(self, checkpoint_path: Optional[str] = None, checkpoint_interval: int = 50):
        """
        Run the routing algorithm with optional checkpoint support.
        
        Args:
            checkpoint_path: Path to save checkpoints (if None, no checkpoints saved)
            checkpoint_interval: Save checkpoint every N steps (default: 50)
        """
        print("=" * 60)
        print("STARTING EV ROUTING WITH MODULAR BATTERY SWAPPING")
        print("=" * 60)
        
        self.print_initial_status()
        
        # Initialize SUMO vehicle for visualization if GUI is enabled
        if self.traci_bridge and self.traci_bridge.gui:
            print("\n" + "="*60)
            print("SUMO GUI VISUALIZATION")
            print("="*60)
            print(f"Delivery Vehicle ID: {self.vehicle_id}")
            print("="*60)
            print("To track this vehicle in SUMO GUI:")
            print(f"  1. Right-click on any vehicle in SUMO")
            print(f"  2. Select 'Select Vehicle' or type: {self.vehicle_id}")
            print(f"  3. The vehicle should appear in BRIGHT MAGENTA color")
            print("="*60 + "\n")
            
            self.initialize_sumo_vehicle()
            
            if self.traci_bridge.vehicle_id:
                print(f"\n[SUMO] Your delivery vehicle ID is: {self.vehicle_id}")
                print(f"[SUMO] Look for this ID in SUMO GUI to track your vehicle!\n")
        
        # Extended main loop: continue until all customers served AND back at depot
        step_count = 0
        last_checkpoint_step = 0
        while len(self.served_customers) < len(self.customers) or self.current_location != self.depot:
            step_count += 1
            
            # Save checkpoint periodically
            if checkpoint_path and (step_count - last_checkpoint_step) >= checkpoint_interval:
                self.save_checkpoint(checkpoint_path)
                last_checkpoint_step = step_count
            
            # Periodic vehicle verification (every 10 steps)
            if self.traci_bridge and self.traci_bridge.gui and step_count % 10 == 0:
                if self.traci_bridge.vehicle_id:
                    exists, status_msg = self.traci_bridge.verify_vehicle_exists(self.traci_bridge.vehicle_id)
                    if not exists:
                        # Only log vehicle missing at debug level to reduce verbosity
                        if hasattr(self, 'debug_sumo') and self.debug_sumo:
                            print(f"[SUMO DEBUG] Vehicle missing at step {step_count}: {status_msg}")
                            print(f"[SUMO DEBUG] Attempting to re-add vehicle at current location: {self.current_location}")
                        self._readd_vehicle_at_current_location()
                    else:
                        # Check if vehicle is at traffic light
                        if self.traci_bridge.is_vehicle_at_traffic_light(self.traci_bridge.vehicle_id):
                            if hasattr(self, 'debug_sumo') and self.debug_sumo:
                                print(f"[SUMO DEBUG] Vehicle stopped at traffic light (step {step_count})")
                        # Print vehicle status only at debug level to reduce verbosity
                        if hasattr(self, 'debug_sumo') and self.debug_sumo:
                            vehicle_status = self.traci_bridge.get_vehicle_status(self.traci_bridge.vehicle_id)
                            if vehicle_status:
                                print(f"[SUMO DEBUG] Vehicle status (step {step_count}): edge={vehicle_status['edge_id']}, "
                                      f"speed={vehicle_status['speed']:.2f} m/s")
            
            print(f"\n--- Current Status ---")
            print(f"Location: {self.current_location}")
            print(f"Unserved customers: {len(self.customers) - len(self.served_customers)}")
            print(f"Current SoC: {self.battery.get_total_charge_percent():.1f}%")
            
            # Handle current location
            if self.current_location in self.customers and self.current_location not in self.served_customers:
                print(f"📍 Currently at customer location: {self.current_location}")
                self.serve_customer(self.current_location)
                continue
            
            if self.current_location in self.bss_stations:
                print(f"📍 Currently at BSS location: {self.current_location}")
                if self.handle_bss_visit(self.current_location):
                    continue
                else:
                    print("BSS handling failed!")
                    return False
            
            # Determine next target
            if len(self.served_customers) < len(self.customers):
                # Still have customers to serve
                # Update traffic factors from SUMO before selecting customer
                if self.traci_bridge:
                    self.update_traffic_factors_from_sumo()
                
                best_customer = self.select_best_customer()
                if best_customer:
                    print(f"Selected customer: {best_customer}")
                    
                    # Update traffic factors before selecting BSS
                    if self.traci_bridge:
                        self.update_traffic_factors_from_sumo()
                    
                    nearest_bss_from_customer = self.select_best_bss(best_customer)
                    
                    if nearest_bss_from_customer:
                        print(f"Nearest BSS from customer: {nearest_bss_from_customer}")
                        
                        # Estimate energy for journey
                        required_energy = self.estimate_energy_for_journey(best_customer, via_bss=False)
                        current_energy = self.battery.get_total_charge_kwh()
                        
                        print(f"Required energy: {required_energy:.3f}kWh, Current: {current_energy:.3f}kWh")
                        
                        # Check if we have enough energy
                        if current_energy >= required_energy:
                            print("Sufficient energy for journey - checking for BSS opportunities...")
                            
                            # Check for depleted modules and nearby BSS opportunities
                            depleted_modules = self.battery.get_depleted_modules()
                            
                            if depleted_modules:
                                print(f"Found {len(depleted_modules)} depleted modules: {depleted_modules}")
                                
                                # Find BSS within range
                                destination_distance = self.calculate_path_distance(self.current_location, best_customer)
                                nearby_bss = self.find_bss_within_range(destination_distance)
                                
                                if nearby_bss:
                                    print(f"Found {len(nearby_bss)} BSS within range: {nearby_bss}")
                                    
                                    # Update traffic factors before selecting opportunity BSS
                                    if self.traci_bridge:
                                        self.update_traffic_factors_from_sumo()
                                    
                                    best_opportunity_bss = self.select_best_opportunity_bss(nearby_bss, best_customer)
                                    
                                    if best_opportunity_bss and self.is_bss_worth_visiting(best_opportunity_bss, best_customer):
                                        print("BSS visit is cost-effective - moving towards BSS")
                                        self.move_to_node(best_opportunity_bss)  # Move one step towards BSS
                                        continue
                                    else:
                                        print("BSS not cost-effective - moving towards customer")
                                        self.move_to_node(best_customer)  # Move one step towards customer
                                        continue
                                else:
                                    print("No BSS within range - moving towards customer")
                                    self.move_to_node(best_customer)  # Move one step towards customer
                                    continue
                            else:
                                print("No depleted modules - moving towards customer")
                                self.move_to_node(best_customer)  # Move one step towards customer
                                continue
                        else:
                            # Insufficient energy - need BSS first
                            print("Insufficient energy - finding nearest BSS")
                            
                            # Update traffic factors before finding BSS for insufficient energy
                            if self.traci_bridge:
                                self.update_traffic_factors_from_sumo()
                            
                            nearest_bss = self.find_bss_for_insufficient_energy(best_customer)
                            if nearest_bss:
                                print(f"Moving towards nearest BSS: {nearest_bss}")
                                self.move_to_node(nearest_bss)  # Move one step towards BSS
                                continue
                            else:
                                print("No reachable BSS found!")
                                return False
                    else:
                        print("No reachable BSS found")
                        return False
                else:
                    print("No reachable customers found")
                    return False
            else:
                # All customers served - head to depot
                if self.current_location != self.depot:
                    print("[DEPOT] All customers served - heading to depot")
                    
                    current_energy = self.battery.get_total_charge_kwh()
                    depot_energy_needed = self.estimate_energy_for_journey(self.depot, via_bss=False)
                    
                    if current_energy >= depot_energy_needed:
                        print("Moving towards depot")
                        self.move_to_node(self.depot)
                        continue
                    else:
                        print("Insufficient energy for depot - finding BSS")
                        
                        # Check if we're at a BSS
                        if self.current_location in self.bss_stations:
                            print(f"📍 Currently at BSS: {self.current_location}")
                            if self.handle_bss_visit(self.current_location):
                                continue  # After BSS visit, continue towards depot
                            else:
                                print("BSS handling failed!")
                                return False
                        else:
                            # Find and move towards BSS
                            # Update traffic factors before finding BSS
                            if self.traci_bridge:
                                self.update_traffic_factors_from_sumo()
                            
                            nearest_bss = self.find_bss_for_insufficient_energy(self.depot)
                            if nearest_bss:
                                print(f"Moving towards BSS: {nearest_bss}")
                                self.move_to_node(nearest_bss)  # Move one step towards BSS
                                continue
                            else:
                                print("No BSS available for depot return!")
                                return False
        
        print("[SUCCESS] All customers served and returned to depot!")
        
        self.print_final_status()
        return True
    
    def print_initial_status(self):
        # Initialize SoC trail with starting node
        self.soc_trail = [(self.current_location, self.battery.get_total_charge_percent())]
        self.edge_energies = []
        print(f"Current location: {self.current_location}")
        print(f"Total Travel Time: {self.total_travel_time:.2f} minutes")
        print(f"Total Energy Consumed: {self.total_energy_consumed:.3f} kWh")
        print(f"Total Distance Covered: {self.total_distance_covered:.2f} km")
        print(f"Current SoC: {self.battery.get_total_charge_percent():.1f}%")
        print("Charge of modules:")
        for module_id, charge in self.battery.get_module_status().items():
            print(f"  {module_id} = {charge}")
        print(f"Number of Modules Swapped: {self.modules_swapped}")
        print(f"Number of Packages: {len(self.customers)}")
        print(f"Payload: {self.total_load} kg")
        print(f"Number of unserved customers: {len(self.customers)}")
        print(f"Served Customers: {self.served_customers}")
    
    def print_final_status(self):
        print("\n" + "=" * 60)
        print("FINAL JOURNEY STATUS")
        print("=" * 60)
        print(f"Current location: {self.current_location}")
        print(f"Total Travel Time: {self.total_travel_time:.2f} minutes")
        print(f"Total Energy Consumed: {self.total_energy_consumed:.3f} kWh")
        print(f"Total Distance Covered: {self.total_distance_covered:.2f} km")
        print(f"Total Swapping Cost: {self.modules_swapped * 50}")
        print(f"Current SoC: {self.battery.get_total_charge_percent():.1f}%")
        print("Charge of modules:")
        for module_id, charge in self.battery.get_module_status().items():
            print(f"  {module_id} = {charge}")
        print(f"Number of Modules Swapped: {self.modules_swapped}")
        print(f"Number of Packages: {len(self.customers)}")
        print(f"Payload: {self.total_load} kg")
        print(f"Number of unserved customers: {len(self.customers) - len(self.served_customers)}")
        print(f"Served Customers: {self.served_customers}")
        
        print(f"Path Taken: {' -> '.join(self.path_taken)}")
        
        print("\n")

        if self.soc_trail:
            soc_str = ' -> '.join([f"{node}({soc:.1f}%)" for node, soc in self.soc_trail])
            print(f"SoC Trail: {soc_str}")
        
        print("\n")

        # Energy trail between nodes: A - x kWh > B - y kWh > C ... > Z
        if self.path_taken and len(self.path_taken) > 1 and self.edge_energies:
            parts = [self.path_taken[0]]
            limit = min(len(self.edge_energies), len(self.path_taken) - 1)
            for i in range(limit):
                parts.append(f" - {self.edge_energies[i]:.3f} kWh > {self.path_taken[i+1]}")
            print(f"Energy Trail: {''.join(parts)}")
    
    def visualize_graph(self):
        plt.figure(figsize=(12, 10))
        pos = nx.spring_layout(self.graph, seed=42)
        
        # Color nodes by type
        node_colors = []
        for node in self.graph.nodes():
            node_type = self.graph.nodes[node].get('node_type', 'intersection')
            if node_type == 'depot':
                node_colors.append('red')
            elif node_type == 'customer':
                node_colors.append('orange')
            elif node_type == 'bss':
                node_colors.append('yellow')
            else:  # intersection
                node_colors.append('lightblue')
        
        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, 
                              node_size=1000, alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(self.graph, pos, alpha=0.5, edge_color='gray')
        
        # Highlight path taken
        if len(self.path_taken) > 1:
            path_edges = [(self.path_taken[i], self.path_taken[i+1]) 
                         for i in range(len(self.path_taken)-1)]
            nx.draw_networkx_edges(self.graph, pos, edgelist=path_edges, 
                                  edge_color='red', width=3, alpha=0.8)
        
        # Add labels
        nx.draw_networkx_labels(self.graph, pos, font_size=10, font_weight='bold')
        
        # Add edge labels for path edges only
        if len(self.path_taken) > 1:
            edge_labels = {}
            for i in range(len(self.path_taken) - 1):
                from_node = self.path_taken[i]
                to_node = self.path_taken[i + 1]
                if self.graph.has_edge(from_node, to_node):
                    edge_data = self.graph[from_node][to_node]
                    distance = edge_data['distance']
                    actual_speed = self.calculate_actual_speed(edge_data, self.total_load)
                    travel_time = self.calculate_travel_time(distance, actual_speed)
                    energy = self.calculate_energy_consumption(edge_data, distance, self.total_load)
                    
                    edge_labels[(from_node, to_node)] = f"d:{distance:.1f}km\nt:{travel_time:.1f}min\ne:{energy:.3f}kWh"
            
            nx.draw_networkx_edge_labels(self.graph, pos, edge_labels, font_size=8)
        
        plt.title("EVRP-BSS: Electric Vehicle Routing with Modular Battery Swapping", 
                 fontsize=14, fontweight='bold')
        plt.legend(['Depot', 'Customer', 'BSS', 'Intersection', 'Path Taken'], 
                  loc='upper right', bbox_to_anchor=(1.15, 1))
        plt.axis('off')
        plt.tight_layout()
        plt.show()

def create_example_scenario():
    # Initialize the system
    evrp = EVRPBSS()
    
    # Create vehicle (using values from seniors_code.py as reference)
    vehicle = Vehicle(
        vehicle_id="EV1",
        mass=1500.0,  # kg
        speed=60.0,   # km/h
        mass_factor=100.0,  # kg
        rolling_resistance=0.01,
        drag_coefficient=0.3,
        cross_sectional_area=2.5  # m²
    )
    evrp.add_vehicle(vehicle)
    
    # Create modular battery (5 modules, 20kWh each)
    battery = ModularBattery(
        num_modules=5,
        module_capacity=20.0,  # kWh per module
        initial_charges=[100.0, 100.0, 100.0, 50.0, 0.0]  # All modules at 100%
    )
    evrp.add_battery(battery)
    
    # Set base speed
    evrp.base_speed = 50.0  # km/h
    
    # Add nodes
    evrp.add_node("D", "depot")
    evrp.add_node("1", "intersection")
    evrp.add_node("2", "intersection")
    evrp.add_node("3", "intersection")
    evrp.add_node("C1", "customer")
    evrp.add_node("C2", "customer")
    evrp.add_node("C3", "customer")
    evrp.add_node("BSS1", "bss")
    evrp.add_node("BSS2", "bss")
    
    # Add edges with distances and traffic factors
    edges = [
        ("D", "1", 5.0, 1.0),
        ("1", "2", 8.0, 1.2),
        ("2", "3", 6.0, 0.9),
        ("1", "C1", 4.0, 1.1),
        ("2", "C2", 3.0, 1.0),
        ("3", "C3", 5.0, 1.3),
        ("1", "BSS1", 7.0, 1.0),
        ("3", "BSS2", 4.0, 1.1),
        ("BSS1", "C1", 6.0, 1.0),
        ("BSS2", "C3", 3.0, 1.0)
    ]
    
    for from_node, to_node, distance, traffic_factor in edges:
        evrp.add_edge(from_node, to_node, distance, traffic_factor)
    
    # Set initial conditions
    evrp.current_location = "D"
    evrp.total_load = len(evrp.customers) * evrp.package_weight  # 3 packages
    evrp.path_taken = ["D"]
    
    return evrp

if __name__ == "__main__":
    # Start timing
    start_time = time.time()
    
    # Create and run example scenario
    evrp_system = create_example_scenario()
    
    # Run the routing algorithm
    success = evrp_system.run_routing_algorithm()
    
    # End timing
    end_time = time.time()
    runtime = end_time - start_time
    
    print(f"\n" + "=" * 60)
    print(f"PROGRAM RUNTIME: {runtime:.3f} seconds")
    print("=" * 60)
    
    if success:
        # Create visualization
        evrp_system.visualize_graph()
    else:
        print("Routing failed!")
