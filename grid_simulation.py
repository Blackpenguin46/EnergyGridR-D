import math
import random
import logging


class GridSimulator:
    def __init__(self):
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(filename='grid_simulation_log.txt', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def log_node_placement(self, node_type, x, y):
        logging.info(f"Node placed: {node_type} at ({x}, {y})")

    def log_node_movement(self, node_type, x, y):
        logging.info(f"Node moved: {node_type} to ({x}, {y})")

    def log_node_removal(self, node_type, x, y):
        logging.info(f"Node removed: {node_type} from ({x}, {y})")

    def log_connection(self, start_index, end_index):
        logging.info(f"Connection added: from node {start_index} to node {end_index}")

    def simulate_performance(self, grid_topology):
        total_energy_output = 0
        total_efficiency = 0
        total_load_balance = 100

        for node in grid_topology['nodes']:
            node_type, x, y = node
            energy_output, efficiency = self.get_node_performance(node_type)
            total_energy_output += energy_output
            total_efficiency += efficiency

        total_line_loss = self.calculate_line_loss(grid_topology)
        total_energy_output -= total_line_loss

        if grid_topology['nodes']:
            average_efficiency = (total_efficiency / len(grid_topology['nodes'])) * (
                        1 - total_line_loss / total_energy_output)
        else:
            average_efficiency = 0

        load_balance = self.calculate_load_balance(grid_topology)

        performance_data = {
            "total_energy_output": total_energy_output,
            "average_efficiency": average_efficiency,
            "load_balance": load_balance
        }

        logging.info(f"Simulated performance: {performance_data}")
        return performance_data

    def get_node_performance(self, node_type):
        if node_type == "Generator":
            return 1000, 90
        elif node_type == "Substation":
            return 500, 95
        elif node_type == "City":
            return -300, 85
        elif node_type == "Building":
            return -100, 80
        else:
            return 0, 0

    def calculate_line_loss(self, grid_topology):
        total_loss = 0
        for connection in grid_topology['connections']:
            start_node, end_node = connection
            start_type, start_x, start_y = grid_topology['nodes'][start_node]
            end_type, end_x, end_y = grid_topology['nodes'][end_node]
            distance = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
            loss_percentage = 0.05 * (distance / 100)
            total_loss += loss_percentage * 1000
        return total_loss

    def calculate_load_balance(self, grid_topology):
        total_generation = sum(1000 for node in grid_topology['nodes'] if node[0] == "Generator")
        total_consumption = sum(
            300 if node[0] == "City" else 100 for node in grid_topology['nodes'] if node[0] in ["City", "Building"])
        if total_generation > 0:
            return (1 - abs(total_generation - total_consumption) / total_generation) * 100
        return 0

    def perform_security_assessment(self, grid_topology):
        vulnerability_score = self.calculate_vulnerability_score(grid_topology)
        suggestions = self.generate_security_suggestions(grid_topology)
        security_data = {
            "vulnerability_score": vulnerability_score,
            "suggestions": suggestions
        }
        logging.info(f"Performed security assessment: {security_data}")
        return security_data

    def calculate_vulnerability_score(self, grid_topology):
        score = 5
        num_nodes = len(grid_topology['nodes'])
        num_connections = len(grid_topology['connections'])

        score += num_nodes * 0.1 + num_connections * 0.2

        critical_nodes = sum(1 for node in grid_topology['nodes'] if node[0] in ["Generator", "Substation"])
        score += critical_nodes * 0.5

        return min(max(score, 0), 10)

    def generate_security_suggestions(self, grid_topology):
        suggestions = [
            "Implement advanced encryption for all communication channels",
            "Regularly update and patch all systems",
            "Conduct frequent security audits and penetration testing"
        ]

        if any(node[0] == "Generator" for node in grid_topology['nodes']):
            suggestions.append("Enhance physical security measures for generator sites")

        if len(grid_topology['connections']) > 5:
            suggestions.append("Implement network segmentation to isolate critical systems")

        return suggestions

    def export_log(self):
        log_file = "grid_simulation_log.txt"
        logging.info(f"Exported simulation log to: {log_file}")
        return log_file