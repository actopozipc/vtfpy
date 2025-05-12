from typing import List, Any, Union, Optional, Callable
import re
import numpy as np
from typing import List, Callable, Tuple, Type
def append_vtf_timesteps(
    particle_timesteps,
    filename,
    x_attr=None,
    y_attr=None,
    z_attr=None
):
    """
    Append particle positions as timesteps to an existing VTF file
    Assumes topology and box size are already defined in the file

    Args:
        particle_timesteps: List of particle objects or list of lists (for multiple timesteps)
        filename: Existing .vtf file to append to
        x_attr, y_attr, z_attr: Attribute names or callables for position extraction
    Returns:
        None
    """

    def get_attr(obj, name_candidates):
        for name in name_candidates:
            if hasattr(obj, name):
                return getattr(obj, name)
        raise AttributeError(f"None of {name_candidates} found in object {obj}")

    def get_value(p, key, fallbacks):
        if callable(key):
            return key(p)
        elif isinstance(key, str):
            return getattr(p, key)
        else:
            return get_attr(p, fallbacks)

    if not isinstance(particle_timesteps[0], list):
        particle_timesteps = [particle_timesteps]

    with open(filename, 'a') as f:
        for timestep in particle_timesteps:
            f.write("timestep\n")
            for i, p in enumerate(timestep, start=1):
                x = get_value(p, x_attr, ["x", "pos_x", "vector"])
                y = get_value(p, y_attr, ["y", "pos_y", "vector"])
                z = get_value(p, z_attr, ["z", "pos_z", "vector"])
                # if p.vector exists and x/y/z were not given, this fallback works
                if isinstance(x, (list, tuple, np.ndarray)) and len(x) == 3:
                    x, y, z = x[0], x[1], x[2]
                f.write(f"atom {i} position {x} {y} {z}\n")
            f.write("\n")
def write_vtf(
    particle_timesteps: Union[List[Any], List[List[Any]]],
    filename: str,
    box_size: Union[tuple, list, Any, Callable[[], tuple]] = (10.0, 10.0, 10.0),
    x_attr: Optional[Union[str, Callable[[Any], float]]] = None,
    y_attr: Optional[Union[str, Callable[[Any], float]]] = None,
    z_attr: Optional[Union[str, Callable[[Any], float]]] = None,
    radius_attr: Optional[Union[str, Callable[[Any], float]]] = None
):
    """
    Write particle data to a .vtf file

    Args:
        particle_timesteps: A list of particle objects or list of lists (for multiple timesteps)
        filename: Output filename
        box_size: Tuple/list, object with x/y/z or width/height/depth, or callable returning (x,y,z)
        x_attr, y_attr, z_attr, radius_attr: Either attribute names (str) or functions (callables) to extract values
    REturns:
        None
    Example usage:
            #Class with insufficient properties:
            class Particle:
                def __init__(self, vector, r):
                    self.vector = vector
                    self.r = r

            particles = [
                Particle([1.0, 2.0, 3.0], 0.5),
                Particle([4.0, 5.0, 6.0], 0.2),
            ]

            write_vtf(
                particles,
                "vector.vtf",
                x_attr=lambda p: p.vector[0],
                y_attr=lambda p: p.vector[1],
                z_attr=lambda p: p.vector[2],
                radius_attr="r"
            )
            #Class with properties:
            class Particle:
            def __init__(self, x, y, z, radius):
                self.x = x
                self.y = y
                self.z = z
                self.radius = radius

        particles = [
            Particle(1.0, 2.0, 3.0, 0.5),
            Particle(4.0, 5.0, 6.0, 0.2)
        ]

        # Single timestep
        write_vtf(particles, "custom_box_output.vtf",box_size=box )
        
    """

    

    def get_value(p, key, fallbacks):
        if callable(key):
            return key(p)
        elif isinstance(key, str):
            return getattr(p, key)
        else:
            return get_attr(p, fallbacks)

    def parse_box_size(box):
        if callable(box):
            return box()
        elif isinstance(box, (tuple, list)) and len(box) >= 3:
            return box[:3]
        else:
            x = get_attr(box, ['x', 'width', 'lx', 'a'])
            y = get_attr(box, ['y', 'height', 'ly', 'b'])
            z = get_attr(box, ['z', 'depth', 'lz', 'c'])
            return (x, y, z)
    if not isinstance(particle_timesteps[0], list):
        particle_timesteps = [particle_timesteps]
    bx, by, bz = parse_box_size(box_size)

    with open(filename, 'w') as f:
        f.write(f"pbc {bx} {by} {bz}\n\n")

        first_step = particle_timesteps[0]
        for i, p in enumerate(first_step, start=1):
            radius = get_value(p, radius_attr, ["radius", "r", "size"])
            f.write(f"atom {i} radius {radius}\n")

        f.write("\n")

        for timestep in particle_timesteps:
            f.write("timestep\n")
            for i, p in enumerate(timestep, start=1):
                x = get_value(p, x_attr, ["x", "pos_x"])
                y = get_value(p, y_attr, ["y", "pos_y"])
                z = get_value(p, z_attr, ["z", "pos_z"])
                f.write(f"atom {i} position {x} {y} {z}\n")
            f.write("\n")



def read_vtf(
    filename: str,
    cls: Type,
    factory: Callable[[dict], Any] = None
) -> Tuple[List[List[Any]], Tuple[float, float, float]]:
    """
    Reads a VTF file and returns a list of timesteps,
    where each timestep is a list of instances of cls

    Args:
        filename: Path to the .vtf file
        cls: The class to instantiate
        factory: Optional function that takes a dict with 'x', 'y', 'z', 'radius' and returns an object

    Returns:
        (timesteps, box_size)
    Example usage:
        #Class with insufficient properties:
        class Particle:
            def __init__(self, vector, r):
                self.vector = vector
                self.r = r

        def factory(d):
            return Particle(vector=[d["x"], d["y"], d["z"]], r=d["radius"])

        timesteps, box = read_vtf("teilchen_liste.vtf", Particle, factory=factory)
        #Class with enough properties:
        class Particle:
            def __init__(self, x, y, z, radius):
                self.x = x
                self.y = y
                self.z = z
                self.radius = radius
        timesteps, box = read_vtf("particles.vtf", Particle)
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    box_size = (0.0, 0.0, 0.0)
    atom_radii = {}

    timesteps = []
    current_positions = {}

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        if line.startswith('pbc'):
            _, x, y, z = line.split()
            box_size = (float(x), float(y), float(z))

        elif line.startswith('atom') and 'radius' in line:
            match = re.match(r'atom (\d+) radius ([\d\.eE+-]+)', line)
            if match:
                atom_id = int(match.group(1))
                radius = float(match.group(2))
                atom_radii[atom_id] = radius

        elif line.startswith('timestep'):
            if current_positions:
                timestep = []
                for atom_id in sorted(current_positions):
                    x, y, z = current_positions[atom_id]
                    r = atom_radii.get(atom_id, 0.5)
                    particle_data = {'x': x, 'y': y, 'z': z, 'radius': r}
                    if factory:
                        particle = factory(particle_data)
                    else:
                        particle = cls(**particle_data)
                    timestep.append(particle)
                timesteps.append(timestep)
                current_positions = {}

        elif line.startswith('atom') and 'position' in line:
            match = re.match(r'atom (\d+) position ([\d\.eE+-]+) ([\d\.eE+-]+) ([\d\.eE+-]+)', line)
            if match:
                atom_id = int(match.group(1))
                pos = tuple(float(match.group(i)) for i in range(2, 5))
                current_positions[atom_id] = pos
    if current_positions:
        timestep = []
        for atom_id in sorted(current_positions):
            x, y, z = current_positions[atom_id]
            r = atom_radii.get(atom_id, 0.5)
            particle_data = {'x': x, 'y': y, 'z': z, 'radius': r}
            if factory:
                particle = factory(particle_data)
            else:
                particle = cls(**particle_data)
            timestep.append(particle)
        timesteps.append(timestep)

    return timesteps, box_size

