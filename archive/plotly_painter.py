"""
Plotly painter patches for better visualization of the packing results. Code inspired by https://plotly.com/python/3d-volumetric-charts/

https://github.com/ravhello/Insightfully-3D-bin-packing/blob/master/py3dbp/main.py

class Painter:

    def __init__(self, bin):
        self.items = bin.items
        self.width = float(bin.width)
        self.height = float(bin.height)
        self.depth = float(bin.depth)

    def plotBoxAndItems(self, title="", alpha=0.2, write_name=True, fontsize=10, alpha_proportional=False, top_face_proportional=False, show_edges=True):
        # Side effect: Plot the Bin and the items it contains. 
        fig = go.Figure()

        # Plot bin as wireframe
        self._plotBinWireframe(fig, 0, 0, 0, self.width, self.height, self.depth, color='black')

        # Find max weight for proportional alpha
        max_weight = max([item.weight for item in self.items]) if len(self.items) > 0 else Decimal('1')

        for item in self.items:
            x, y, z = item.position
            w, h, d = item.getDimension()
            color = item.color
            text = item.item_id if write_name and 'corner' not in item.item_name else ""
            # Calculate alpha and top_alpha
            if alpha_proportional:
                alpha = float(item.weight / max_weight) if item.weight is not None else alpha
            if top_face_proportional:
                top_alpha = 1 - float(item.loadbear / max_weight)
                top_alpha = max(0, min(top_alpha, 1))  # Ensure alpha is between 0 and 1
            else:
                top_alpha = alpha

            if item.typeof == 'cube':
                # Plot the cube with optional top face adjustment
                self._plotCube(fig, float(x), float(y), float(z), float(w), float(h), float(d),
                            color=color, opacity=alpha, text=text, fontsize=fontsize,
                            show_edges=show_edges, item_name=item.item_name, top_alpha=top_alpha, top_face_proportional=top_face_proportional)
            elif item.typeof == 'cylinder':
                # Plot cylinder if applicable
                self._plotCylinder(fig, float(x), float(y), float(z), float(w), float(h), float(d),
                            color=color, opacity=alpha, text=text, fontsize=fontsize,
                            show_edges=show_edges, item_name=item.item_name, top_alpha=top_alpha, top_face_proportional=top_face_proportional)
            else:
                if external_logger:
                    external_logger.warning(f'Item {item.item_id} has an invalid type: {item.typeof}')
                    external_logger.warning(f'Item {item.item_id} will not be plotted')

        # Configure plot layout
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis_title='X Axis',
                yaxis_title='Y Axis',
                zaxis_title='Z Axis',
                aspectmode='data'
            ),
            autosize=True,  # Ensure it resizes automatically
            template='plotly_white'  # Optional, improves aesthetics
        )

        fig.show(config={"displayModeBar": True, "responsive": True})

        return fig  # Return the generated figure

    def _plotBinWireframe(self, fig, x, y, z, dx, dy, dz, color='black'):
        # Auxiliary function to plot a wireframe cube for the bin.
        # Define the vertices of the cube
        vertices = [
            [x, y, z],
            [x+dx, y, z],
            [x+dx, y+dy, z],
            [x, y+dy, z],
            [x, y, z+dz],
            [x+dx, y, z+dz],
            [x+dx, y+dy, z+dz],
            [x, y+dy, z+dz]
        ]

        # Define the 12 lines (edges) of the cube
        edges = [
            [vertices[0], vertices[1], 'Lower north edge'], [vertices[1], vertices[2], 'Lower east edge'], [vertices[2], vertices[3], 'Lower south edge'], [vertices[3], vertices[0], 'Lower west edge'],
            [vertices[4], vertices[5], 'Upper north edge'], [vertices[5], vertices[6], 'Upper east edge'], [vertices[6], vertices[7], 'Upper south edge'], [vertices[7], vertices[4], 'Upper west edge'],
            [vertices[0], vertices[4], 'North vertical edge'], [vertices[1], vertices[5], 'East vertical edge'], [vertices[2], vertices[6], 'South vertical edge'], [vertices[3], vertices[7], 'West vertical edge']
        ]

        # Add the edges to the plot
        for edge in edges:
            fig.add_trace(go.Scatter3d(
                x=[edge[0][0], edge[1][0]],
                y=[edge[0][1], edge[1][1]],
                z=[edge[0][2], edge[1][2]],
                mode='lines',
                line=dict(color=color, width=2),
                name=f'Bin - {edge[2]}',
                legendgroup='bin',
                showlegend=False
            ))

    def _plotCube(self, fig, x, y, z, dx, dy, dz, color='red', opacity=0.5, text="", fontsize=10, show_edges=True, item_name="", top_alpha=None, top_face_proportional=False):
        # Auxiliary function to plot a cube with optional top face transparency adjustment. 
        if top_alpha is None:
            top_alpha = opacity  # Default to opacity if not provided

        # Define the vertices of the cube
        vertices = [
            [x, y, z],           # 0
            [x+dx, y, z],        # 1
            [x+dx, y+dy, z],     # 2
            [x, y+dy, z],        # 3
            [x, y, z+dz],        # 4
            [x+dx, y, z+dz],     # 5
            [x+dx, y+dy, z+dz],  # 6
            [x, y+dy, z+dz]      # 7
        ]

        # Prepare the faces of the cube
        if top_face_proportional:
            # Exclude the top face
            faces = []
            # Bottom face
            faces.extend([
                (0, 1, 2), (0, 2, 3)
            ])
            # Front face
            faces.extend([
                (3, 2, 6), (3, 6, 7)
            ])
            # Back face
            faces.extend([
                (0, 1, 5), (0, 5, 4)
            ])
            # Left face
            faces.extend([
                (0, 3, 7), (0, 7, 4)
            ])
            # Right face
            faces.extend([
                (1, 2, 6), (1, 6, 5)
            ])
        else:
            # Include all faces
            faces = []
            faces.extend([
                (0, 1, 2), (0, 2, 3),  # Bottom face
                (4, 5, 6), (4, 6, 7),  # Top face
                (3, 2, 6), (3, 6, 7),  # Front face
                (0, 1, 5), (0, 5, 4),  # Back face
                (0, 3, 7), (0, 7, 4),  # Left face
                (1, 2, 6), (1, 6, 5)   # Right face
            ])

        # Create indices for the faces
        i = [face[0] for face in faces]
        j = [face[1] for face in faces]
        k = [face[2] for face in faces]

        # Create a 3D mesh for the cube without the top face if top_face_proportional is True
        fig.add_trace(go.Mesh3d(
            x=[v[0] for v in vertices],
            y=[v[1] for v in vertices],
            z=[v[2] for v in vertices],
            i=i,
            j=j,
            k=k,
            color=color,
            opacity=opacity,
            hovertext=text,
            hoverinfo='text',
            name=item_name,
            legendgroup=item_name,
            showlegend=True
        ))

        # Optionally add the edges of the cube
        if show_edges:
            edges = [
                [vertices[0], vertices[1]], [vertices[1], vertices[2]], [vertices[2], vertices[3]], [vertices[3], vertices[0]],
                [vertices[4], vertices[5]], [vertices[5], vertices[6]], [vertices[6], vertices[7]], [vertices[7], vertices[4]],
                [vertices[0], vertices[4]], [vertices[1], vertices[5]], [vertices[2], vertices[6]], [vertices[3], vertices[7]]
            ]
            for edge in edges:
                fig.add_trace(go.Scatter3d(
                    x=[edge[0][0], edge[1][0]],
                    y=[edge[0][1], edge[1][1]],
                    z=[edge[0][2], edge[1][2]],
                    mode='lines',
                    line=dict(color='black', width=1),
                    name=f'{item_name} edge',
                    legendgroup=item_name,
                    showlegend=False
                ))

        # Add the top face separately if top_face_proportional is True
        if top_face_proportional:
            fig.add_trace(go.Surface(
                x=[[x, x+dx], [x, x+dx]],
                y=[[y, y], [y+dy, y+dy]],
                z=[[z+dz, z+dz], [z+dz, z+dz]],
                opacity=top_alpha,
                colorscale=[[0, color], [1, color]],  # Single color
                showscale=False,  # No color scale
                hoverinfo='skip',  # No hover info for the face
                name=f'{item_name} top face',
                legendgroup=item_name,
                showlegend=False
            ))
        elif top_alpha != opacity:
            # Add the top face with adjusted opacity if needed
            fig.add_trace(go.Surface(
                x=[[x, x+dx], [x, x+dx]],
                y=[[y, y], [y+dy, y+dy]],
                z=[[z+dz, z+dz], [z+dz, z+dz]],
                opacity=top_alpha,
                colorscale=[[0, color], [1, color]],  # Single color
                showscale=False,  # No color scale
                hoverinfo='skip',  # No hover info for the face
                name=f'{item_name} top face',
                legendgroup=item_name,
                showlegend=False
            ))

        # Add optional text label
        if text:
            # Calculate the center position of the cube
            x_center = x + dx / 2
            y_center = y + dy / 2
            z_center = z + dz / 2

            fig.add_trace(go.Scatter3d(
                x=[x_center],
                y=[y_center],
                z=[z_center],
                mode='text',
                text=[text],
                textfont=dict(size=fontsize, color="Black"),
                hoverinfo='skip',
                showlegend=False
            ))

    def _plotCylinder(self, fig, x, y, z, dx, dy, dz, color='red', opacity=0.5, text="", fontsize=10, show_edges=True, item_name="", top_alpha=None, top_face_proportional=False):
         Auxiliary function to plot a cylinder using parametric representation.

        if top_alpha is None:
            top_alpha = opacity  # Default to opacity if not provided

        # Radius and height for the cylinder
        radius = min(dx, dy) / 2
        height = dz

        # Center of the cylinder
        x_center = x + dx / 2
        y_center = y + dy / 2

        # Parametrize the cylinder surface (without top face if needed)
        x_surface, y_surface, z_surface = self.cylinder(radius, height, a=z, include_top=not top_face_proportional)
        x_surface += x_center
        y_surface += y_center

        # Add cylinder surface
        fig.add_trace(go.Surface(
            x=x_surface,
            y=y_surface,
            z=z_surface,
            colorscale=[[0, color], [1, color]],
            opacity=opacity,
            showscale=False,
            hoverinfo='skip',
            name=item_name,
            legendgroup=item_name,
            showlegend=True
        ))

        # Plot bottom face
        xb_low, yb_low, zb_low = self.disk(radius, z)
        xb_low += x_center
        yb_low += y_center

        fig.add_trace(go.Surface(
            x=xb_low,
            y=yb_low,
            z=zb_low,
            colorscale=[[0, color], [1, color]],
            opacity=opacity,
            showscale=False,
            hoverinfo='skip',
            name=f'{item_name} bottom face',
            legendgroup=item_name,
            showlegend=False
        ))

        # Add the top face separately if needed
        if top_face_proportional:
            # Plot top face with adjusted opacity
            xb_up, yb_up, zb_up = self.disk(radius, z + dz)
            xb_up += x_center
            yb_up += y_center

            fig.add_trace(go.Surface(
                x=xb_up,
                y=yb_up,
                z=zb_up,
                colorscale=[[0, color], [1, color]],
                opacity=top_alpha,
                showscale=False,
                hoverinfo='skip',
                name=f'{item_name} top face',
                legendgroup=item_name,
                showlegend=False
            ))
        elif top_alpha != opacity:
            # Plot top face with specified top_alpha
            xb_up, yb_up, zb_up = self.disk(radius, z + dz)
            xb_up += x_center
            yb_up += y_center

            fig.add_trace(go.Surface(
                x=xb_up,
                y=yb_up,
                z=zb_up,
                colorscale=[[0, color], [1, color]],
                opacity=top_alpha,
                showscale=False,
                hoverinfo='skip',
                name=f'{item_name} top face',
                legendgroup=item_name,
                showlegend=False
            ))
        else:
            # Plot top face as part of the cylinder surface (already plotted)
            pass  # No action needed

        # Plot edges if requested
        if show_edges:
            # Boundary circles at top and bottom
            xb_low_edge, yb_low_edge, zb_low_edge = self.boundary_circle(radius, z)
            xb_up_edge, yb_up_edge, zb_up_edge = self.boundary_circle(radius, z + dz)
            xb_low_edge += x_center
            yb_low_edge += y_center
            xb_up_edge += x_center
            yb_up_edge += y_center

            # Bottom edge
            fig.add_trace(go.Scatter3d(
                x=xb_low_edge,
                y=yb_low_edge,
                z=zb_low_edge,
                mode='lines',
                line=dict(color="black", width=1),
                opacity=1,
                hoverinfo='skip',
                name=f'{item_name} bottom edge',
                legendgroup=item_name,
                showlegend=False
            ))

            # Top edge
            fig.add_trace(go.Scatter3d(
                x=xb_up_edge,
                y=yb_up_edge,
                z=zb_up_edge,
                mode='lines',
                line=dict(color="black", width=1),
                opacity=1,
                hoverinfo='skip',
                name=f'{item_name} top edge',
                legendgroup=item_name,
                showlegend=False
            ))

        # Add optional text label
        if text:
            fig.add_trace(go.Scatter3d(
                x=[x_center],
                y=[y_center],
                z=[z + dz / 2],
                mode='text',
                text=[text],
                textfont=dict(size=fontsize, color="Black"),
                hoverinfo='skip',
                showlegend=False
            ))

    # Modifica della funzione di parametrizzazione del cilindro
    @staticmethod
    def cylinder(r, h, a=0, nt=100, nv=50, include_top=True):
        
        #Parametrize the cylinder of radius r, height h, base at z=a.
        #If include_top is False, the top surface is not included.
        
        theta = np.linspace(0, 2 * np.pi, nt)
        v = np.linspace(a, a + h, nv)
        theta_grid, v_grid = np.meshgrid(theta, v)
        x = r * np.cos(theta_grid)
        y = r * np.sin(theta_grid)
        z = v_grid

        if not include_top:
            # Exclude the top layer of z values
            mask = z < (a + h)
            x = np.where(mask, x, np.nan)
            y = np.where(mask, y, np.nan)
            z = np.where(mask, z, np.nan)

        return x, y, z

    @staticmethod
    def boundary_circle(r, h, nt=100):
        
        #Parametrize the circle at height h with radius r.
        
        theta = np.linspace(0, 2 * np.pi, nt)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = h * np.ones(theta.shape)
        return x, y, z
    
    @staticmethod
    def disk(r, h, nr=50, nt=100):
        
        #Generate x, y, z coordinates for a filled disk (circle) at height h.
        
        theta = np.linspace(0, 2*np.pi, nt)
        radius = np.linspace(0, r, nr)
        radius_grid, theta_grid = np.meshgrid(radius, theta)
        x = radius_grid * np.cos(theta_grid)
        y = radius_grid * np.sin(theta_grid)
        z = h * np.ones_like(x)
        return x, y, z
"""