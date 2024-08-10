import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import random

class ChartingService:
    def __init__(self):
        pass

    def generate_colors(self, n, seed=None):
        if seed is not None:
            random.seed(seed)  # Set the seed for reproducibility

        colors = set()
        while len(colors) < n:
            hue = random.randint(0, 360)
            saturation = random.randint(40, 100)
            lightness = random.randint(30, 70)
            rgb_color = self.hsl_to_rgb(hue, saturation, lightness)
            color = "#{:02x}{:02x}{:02x}".format(*rgb_color)
            colors.add(color)
        return list(colors)

    def hsl_to_rgb(self, h, s, l):
        h /= 360
        s /= 100
        l /= 100
        if s == 0:
            r = g = b = l  # achromatic
        else:
            def hue_to_rgb(p, q, t):
                if t < 0:
                    t += 1
                if t > 1:
                    t -= 1
                if t < 1/6:
                    return p + (q - p) * 6 * t
                if t < 1/2:
                    return q
                if t < 2/3:
                    return p + (q - p) * (2/3 - t) * 6
                return p

            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue_to_rgb(p, q, h + 1/3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1/3)

        return int(r * 255), int(g * 255), int(b * 255)

    def assign_colors_to_products(self, products):
        unique_product_names = set(product[0] for product in products)
        n = len(unique_product_names)

        colors = self.generate_colors(n, 96)
        product_colors = {product_name: colors[i] for i, product_name in enumerate(unique_product_names)}
        return product_colors

    def create_chart(self, input_data, jobs, idle_times):
        print(input_data)
        product_colors = self.assign_colors_to_products(input_data)
        colors = {product: color for product, color in product_colors.items()}

        # Determine the number of machines from the job data
        num_machines = (len(jobs[0]) - 1) // 2

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 6 + num_machines))

        # Plot the job schedules for each machine
        for job in jobs:
            product = job[0]
            for i in range(num_machines):
                start_time = job[1 + i]
                end_time = job[1 + num_machines + i]
                ax.broken_barh([(start_time, end_time - start_time)], ((i+1)*10, 9), facecolors=(colors[product]), edgecolor='black')
                ax.text(start_time + (end_time - start_time) / 2, (i+1)*10 + 5, product, ha='center', va='center', color='black', fontsize=10, fontweight='bold')

        # Set y-ticks and labels dynamically based on the number of machines
        y_ticks = [(i+1)*10 + 5 for i in range(num_machines)]
        y_labels = [f'Machine {i+1}' for i in range(num_machines)]
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)

        ax.set_xlabel('Time')
        ax.set_ylabel('Machines')
        ax.set_title('Gantt Chart for Jobs on Multiple Machines')
        ax.grid(True)

        # Create legend
        patches_list = [patches.Patch(color=color, label=product) for product, color in colors.items()]
        ax.legend(handles=patches_list)

        # Save the plot to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        return buf, idle_times
