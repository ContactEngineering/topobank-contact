"""
Plot the results of a single contact mechanics load step downloaded from
contact.engineering.

The ZIP download of a contact mechanics analysis contains one netCDF file
per load step, named `step-<n>/nc/results.nc`. Each file holds the
two-dimensional pressure, gap, displacement and contacting-points fields
of that step; global scalars (nominal pressure, rigid body displacement,
convergence status, units) are stored as attributes.

Conventions (see docs/conventions.md for details):
- x is the FIRST array index, y is the SECOND array index.
- Pressures are in units of the contact modulus E*; lengths are in the
  unit given by the `length_unit` attribute.
- The rigid body displacement (`mean_displacement`) is a penetration-like
  coordinate: increasing values press the surfaces together.

Usage:
    python plot_contact_step.py path/to/step-0/nc/results.nc
"""

import sys

import matplotlib.pyplot as plt
import xarray as xr

filename = sys.argv[1] if len(sys.argv) > 1 else "results.nc"
ds = xr.load_dataset(filename)

unit = ds.attrs.get("length_unit", "?")
print(f"Boundary conditions:      {ds.attrs['type']}")
print(f"Nominal pressure:         {ds.attrs['mean_pressure']:.5g} E*")
print(f"Fractional contact area:  {ds.attrs['total_contact_area']:.5g}")
if "mean_displacement" in ds.attrs:
    print(f"Rigid body displacement:  {ds.attrs['mean_displacement']:.5g} {unit}")
if "converged" in ds.attrs:
    print(f"Converged:                {bool(ds.attrs['converged'])}")

fields = {
    "pressure": f"Pressure ({ds.pressure.attrs.get('units', 'E*')})",
    "gap": f"Gap ({ds.gap.attrs.get('units', unit)})",
    "displacement": f"Displacement ({ds.displacement.attrs.get('units', unit)})",
    "contacting_points": "Contacting points",
}

fig, axes = plt.subplots(2, 2, figsize=(10, 8))
for ax, (name, label) in zip(axes.ravel(), fields.items()):
    # The first array index is x, the second is y. matplotlib's imshow
    # expects the leading index to be the image row (vertical), so we
    # transpose and set origin="lower" to get x to the right and y up.
    im = ax.imshow(ds[name].data.T, origin="lower", cmap="viridis")
    ax.set_xlabel(f"x (pixels, spacing in {unit})")
    ax.set_ylabel(f"y (pixels, spacing in {unit})")
    ax.set_title(label)
    fig.colorbar(im, ax=ax)

fig.tight_layout()
plt.show()
