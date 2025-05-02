# vtfpy
vtfpy is a lightweight Python library for reading and writing VTF (Visualization Tool Format) files — widely used for visualizing molecular dynamics and particle simulations in tools like VMD (Visual Molecular Dynamics).

This is especially helpful for students or researchers who:

* Want to visualize custom or self-written molecular dynamics (MD) or Monte Carlo (MC) simulations
* Need a simple way to store particle simulations, time steps, and trajectories to disk


While professional simulation tools like VMD generate VTF files directly, students often build custom simulations from scratch. This library bridges the gap by enabling them to generate valid VTF files directly from Python classes or data structures. Even if you dont want to use this to visualize your simulation with VMD, it can be used to:

* store and load particle simulations. 
* load .vtf files and convert them to your custom python classes

🔑 Keywords: vtf, vmd, molecular dynamics, monte carlo, particle simulation, trajectory, visualization, python, simulation output, md, mc, student, teaching, open source, timesteps, custom simulations, visualize particles, vtfio, vtfpy

## 🚀 Features

- Write particle simulations to `.vtf` files with support for:
  - Single or multiple time steps
  - Automatic or custom property mapping (`x`, `y`, `z`, `radius`)
  - Flexible box definitions
- Read `.vtf` files back into your own particle instances

## 🧱 Installation

Just copy the `vtfio.py` module into your project — no dependencies outside the standard library.
pip is coming maybe.

## 🛠 Usage

### Writing a `.vtf` file:

```python
from vtfio import write_vtf

class Particle:
  def __init__(self, vector, r):
      self.vector = vector
      self.r = r
  
particles = [Particle([1.0, 2.0, 3.0], 0.5),Particle([4.0, 5.0, 6.0], 0.2),]

write_vtf(particles,"vector.vtf",x_attr=lambda p: p.vector[0],y_attr=lambda p: p.vector[1],z_attr=lambda p: p.vector[2],radius_attr="r")
```
or, if your properties are named x,y,z and radius:
```python
from vtfio import write_vtf

class Particle:
            def __init__(self, x, y, z, radius):
                self.x = x
                self.y = y
                self.z = z
                self.radius = radius

particles = [Particle(1.0, 2.0, 3.0, 0.5),Particle(4.0, 5.0, 6.0, 0.2)]

# Single timestep
write_vtf(particles, "output.vtf")
```
### Reading a `.vtf` file:
If your data collection or python class has names that are not x,y,z and radius, you will need to use a helper function like this:
```python
from vtfio import read_vtf

class Particle:
  def __init__(self, vector, r):
      self.vector = vector
      self.r = r
  
def factory(d):
  return Particle(vector=[d["x"], d["y"], d["z"]], r=d["radius"])

timesteps, box = read_vtf("teilchen_liste.vtf", Particle, factory=factory)

```
or, in case the properties of your structure are named like that:
```python
from vtfio import read_vtf

class Particle:
  def __init__(self, x, y, z, radius):
      self.x = x
      self.y = y
      self.z = z
      self.radius = radius
timesteps, box = read_vtf("particles.vtf", Particle)

```
🤝 Contributing

Contributions, issues, and feature requests are welcome!
If you have an idea to improve this tool — bug fixes, feature extensions, or documentation — feel free to submit a pull request or open an issue.

