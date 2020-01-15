from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


import compas

try:
    import System
    import Rhino.UI
    import Eto.Drawing as drawing
    import Eto.Forms as forms
except Exception:
    compas.raise_if_ironpython()


from compas_rhino.etoforms import PropertyListForm
from compas.datastructures import Mesh

__all__ = ['SceneNodePropertyForm']

class Table(forms.GridView):
    def __init__(self, ShowHeader=True):
        self.ShowHeader = ShowHeader
        self.Height = 300

    @classmethod
    def from_sceneNode(cls, sceneNode):
        table = cls(ShowHeader=False)
        table.add_column()
        table.add_column()
        data = []

        data.append(['Type', sceneNode.item.__class__.__name__])
        data.append(['Name', sceneNode.artist.name])
        data.append(['Layer', sceneNode.artist.layer])

        if hasattr(sceneNode.artist, 'settings'):
            for key in sceneNode.artist.settings:
                data.append([key, str(sceneNode.artist.settings[key])])
    
        table.DataStore = data
        return table

    @classmethod
    def from_vertices(cls, mesh):
        table = cls()
        table.add_column('key')
        table.add_column('x')
        table.add_column('y')
        table.add_column('z')
        table.DataStore = [[key, mesh.vertex[key]['x'], mesh.vertex[key]['y'], mesh.vertex[key]['z']] for key in mesh.vertices()]
        return table

    @classmethod
    def from_edges(cls, mesh):
        table = cls()
        table.add_column('vertex1')
        table.add_column('vertex2')
        table.DataStore = [list(edge) for edge in mesh.edges()]
        return table

    @classmethod
    def from_faces(cls, mesh):
        table = cls()
        table.add_column('key')
        table.add_column('vertices')
        table.DataStore = [[key, str(mesh.face[key])] for key in mesh.faces()]
        return table

    def add_column(self, HeaderText=None, Editable=False):
        column = forms.GridColumn()
        if self.ShowHeader:
            column.HeaderText = HeaderText
        column.Editable = Editable
        column.DataCell = forms.TextBoxCell(self.Columns.Count)
        self.Columns.Add(column)


class SceneNodePropertyForm(forms.Dialog):

    # Initializer
    def __init__(self, sceneNode):
        self.Rnd = System.Random()
        self.Title = "Properties"
        self.TabControl = self.from_sceneNode(sceneNode)
        tab_items = forms.StackLayoutItem(self.TabControl, True)
        layout = forms.StackLayout()
        layout.Spacing = 5
        layout.HorizontalContentAlignment = forms.HorizontalAlignment.Stretch
        layout.Items.Add(tab_items)
        self.Content = layout
        self.Padding = drawing.Padding(12)
        self.Resizable = False
        self.ClientSize = drawing.Size(400, 600)

    # Create the dialog content
    def Create(self):
        # create default tabs
        # self.TabControl = self.DefaultTabs()
        self.TabControl = self.from_mesh()
        # create stack layout item for tabs
        tab_items = forms.StackLayoutItem(self.TabControl, True)
        # create stack layout for content
        layout = forms.StackLayout()
        layout.Spacing = 5
        layout.HorizontalContentAlignment = forms.HorizontalAlignment.Stretch
        # add the stuff above to this layout

        layout.Items.Add(tab_items)
        return layout

    # Create the default tabs
    def DefaultTabs(self):
        # creates a tab control
        control = self.CreateTabControl()

        p = PropertyListForm(["name"], [1])
        tab = forms.TabPage()
        tab.Text = "Basic"
        tab.Content = p.table
        control.Pages.Add(tab)

        return control

    def from_sceneNode(self, sceneNode):
        # creates a tab control
        control = self.CreateTabControl()

        tab = forms.TabPage()
        tab.Text = "Basic"
        tab.Content = Table.from_sceneNode(sceneNode)
        control.Pages.Add(tab)

        item = sceneNode.item

        if isinstance(item, Mesh):
            tab = forms.TabPage()
            tab.Text = "Vertices"
            tab.Content = Table.from_vertices(item)
            control.Pages.Add(tab)

            tab = forms.TabPage()
            tab.Text = "Edges"
            tab.Content = Table.from_edges(item)
            control.Pages.Add(tab)

            tab = forms.TabPage()
            tab.Text = "Faces"
            tab.Content = Table.from_faces(item)
            control.Pages.Add(tab)

        return control

    # Delegate function to tab position control
    def DockPositionDelegate(self, position):
        self.TabControl = position

    # Creates the one and only tab control
    def CreateTabControl(self):
        tab = forms.TabControl()
        # Orient the tabs at the top
        tab.TabPosition = forms.DockPosition.Top
        return tab

    def show(self):
        self.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)


if __name__ == "__main__":

    from compas_rhino.scene import Scene

    scene = Scene()

    mesh = Mesh.from_polyhedron(6)

    node = scene.add(mesh, name="Cube", layer="World")
    
    scene.update()

    dialog = SceneNodePropertyForm(node)
    dialog.show()