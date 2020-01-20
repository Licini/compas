from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas

try:
    import clr
    clr.AddReference("Eto")
    clr.AddReference("Rhino.UI")

except Exception:
    compas.raise_if_ironpython()

try:
    import Rhino
    import Rhino.UI
    import Eto.Drawing as drawing
    import Eto.Forms as forms

    Dialog = forms.Dialog[bool]

except ImportError:
    compas.raise_if_ironpython()

    class Dialog:
        pass

from compas_rhino.etoforms import PropertyListForm
from compas_rhino.etoforms.scenenodeproperty import SceneNodePropertyForm


__all__ = ['TreeForm']

class Item(forms.TreeGridItem):
    SceneNode = None



class TreeForm(forms.Form):

    def setup(self, scene):

        self.m_treegridview = forms.TreeGridView()
        self.m_treegridview.Size = drawing.Size(200, 500)

        name_column = forms.GridColumn()
        name_column.HeaderText = 'Name'
        name_column.Editable = True
        name_column.DataCell = forms.TextBoxCell(0)
        self.m_treegridview.Columns.Add(name_column)

        type_column = forms.GridColumn()
        type_column.HeaderText = 'Type'
        type_column.Editable = False
        type_column.DataCell = forms.TextBoxCell(1)
        self.m_treegridview.Columns.Add(type_column)

        # select_column = forms.GridColumn()
        # select_column.HeaderText = 'Selected'
        # select_column.Editable = True
        # select_column.DataCell = forms.CheckBoxCell(2)
        # self.m_treegridview.Columns.Add(select_column)

        treecollection = forms.TreeGridItemCollection()
        scene_node = Item(Values=('scene', 'Scene'))
        for node in scene.nodes:
            item = Item(Values=(node.artist.name, node.item.__class__.__name__))
            item.SceneNode = node
            scene_node.Children.Add(item)
            
        treecollection.Add(scene_node)
        self.m_treegridview.DataStore = treecollection

        layout = forms.DynamicLayout()
        layout.AddRow(self.m_treegridview)
        layout.Add(None)
        layout.BeginVertical()
        layout.BeginHorizontal()
        layout.AddRow(None, self.ok, self.cancel)
        layout.EndHorizontal()
        layout.EndVertical()

        self.Title = 'TreeView'
        self.Padding = drawing.Padding(12)
        self.Resizable = True
        self.Content = layout
        self.ClientSize = drawing.Size(400, 600)

        self.m_treegridview.Activated += self.on_activated

    @property
    def ok(self):
        self.DefaultButton = forms.Button(Text='OK')
        self.DefaultButton.Click += self.on_ok
        return self.DefaultButton

    @property
    def cancel(self):
        self.AbortButton = forms.Button(Text='Cancel')
        self.AbortButton.Click += self.on_cancel
        return self.AbortButton

    def on_ok(self, sender, event):
        # try:
        #     for i, name in enumerate(self.names):
        #         value = self.table.DataStore[i][1]
        #         self.values[i] = value
        # except Exception as e:
        #     print(e)
        #     self.Close(False)
        self.Close(True)

    def on_cancel(self, sender, event):
        self.Close(False)

    def on_activated(self, sender, event):
        try:
            p = SceneNodePropertyForm()
            p.setup(event.Item.SceneNode)
            p.Show()
        except Exception as e:
            print(e)

    def show(self):
        return self.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    from compas.geometry import Point
    from compas.geometry import Line
    from compas.geometry import Frame

    from compas.datastructures import Mesh

    from compas_rhino.scene import Scene

    scene = Scene()

    a = Point(1.0, 1.0, 0.0)
    b = Point(5.0, 5.0, 0.0)
    ab = Line(a, b)
    world = Frame.worldXY()

    mesh = Mesh.from_polyhedron(6)

    scene.add(a, name="A", color=(0, 0, 0), layer="A")
    scene.add(b, name="B", color=(255, 255, 255), layer="B")
    scene.add(ab, name="AB", color=(128, 128, 128), layer="AB")
    scene.add(world, name="World", layer="World")
    scene.add(mesh, name="Cube", layer="Cube")

    scene.update()

    t = TreeForm()
    t.setup(scene)
    t.Show()