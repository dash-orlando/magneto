'''
Create a MayaVI2 cartesian volume with meshed grid planes
'''

from    tvtk.api        import  tvtk
from    mayavi.scripts  import  mayavi2
import  numpy           as      np

# Generate meshgrid (cartesian volume)
data = np.ones((10, 10, 10))
i = tvtk.ImageData(spacing=(1, 1, 1), origin=(0, 0, 0))
i.point_data.scalars = data.ravel()
i.point_data.scalars.name = 'scalars'
i.dimensions = data.shape


# View the data.
@mayavi2.standalone
def view():
    from mayavi.sources.vtk_data_source import VTKDataSource
    from mayavi.modules.api import Outline, GridPlane

    mayavi.new_scene()
    src = VTKDataSource(data=i)
    mayavi.add_source(src)
    mayavi.add_module(Outline())
    g = GridPlane()
    g.grid_plane.axis = 'x'
    mayavi.add_module(g)
    g = GridPlane()
    g.grid_plane.axis = 'y'
    mayavi.add_module(g)
    g = GridPlane()
    g.grid_plane.axis = 'z'
    mayavi.add_module(g)

if __name__ == '__main__':
    view()
